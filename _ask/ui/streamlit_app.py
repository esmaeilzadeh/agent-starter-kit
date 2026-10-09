"""Native Streamlit workbench over admitted Engineering Model snapshots."""
from __future__ import annotations

import os
from pathlib import Path
import re
import ast
import json
import subprocess
import sys
from types import MappingProxyType

import pandas as pd
import streamlit as st


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = Path(__file__).resolve().parent
SCRIPT_ROOT = REPOSITORY_ROOT / "_ask" / "scripts"
if str(UI_ROOT) not in sys.path:
    sys.path.insert(0, str(UI_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from engineering_model.actions import edit
from engineering_model.admission import admit, load_published
from engineering_model.projection import project
from engineering_model.snapshot import Snapshot, decode, referenced_paths
from engineering_model.workbench_sources import discover_work, read_snapshot
from workbench_context import (
    STATE_COMMITTED_SOURCE_CACHE, STATE_FORM_IDENTITY, STATE_ROUTE, STATE_SOURCE,
    STATE_SOURCE_SELECTION,
    reset_for_work, route_to,
)
from workbench_navigation import build_outline, render_breadcrumbs, render_outline


STATE_VIEW = "_engineering_displayed_view"
STATE_WORK = "_engineering_displayed_work_id"
STATE_CANDIDATE = "_engineering_candidate_projection"
STATE_FEEDBACK = "_engineering_feedback"
STATE_EVIDENCE_PROJECTION = "_engineering_evidence_projection"
STATE_BRANCH = "_engineering_branch"
STATE_OVERVIEW_RESULTS = "_engineering_overview_results"


def _model_root() -> Path:
    configured = os.environ.get("ASK_MODEL_ROOT")
    return Path(configured).expanduser().resolve() if configured else REPOSITORY_ROOT


def _workstreams(root: Path) -> list[str]:
    work = root / "work"
    if not work.is_dir():
        return []
    return sorted(path.parent.name for path in work.glob("*/engineering-model.json") if path.is_file())


def _current_branch(root: Path) -> str:
    try:
        result = subprocess.run(["git", "branch", "--show-current"], cwd=root,
                                capture_output=True, text=True, timeout=2, check=False)
        return result.stdout.strip() if result.returncode == 0 else "unknown branch"
    except (OSError, subprocess.TimeoutExpired):
        return "unknown branch"


def _default_workstream(branch: str, work_ids: list[str]) -> str:
    branch_work_id = branch.removeprefix("agent/") if branch.startswith("agent/") else None
    return branch_work_id if branch_work_id in work_ids else work_ids[0]


def _diagnostic(code: str, path: str, message: str) -> dict:
    return {"code": code, "path": path, "message": message}


def _capture_view(root: Path, work_id: str) -> dict:
    """Admit once, or expose a previously published snapshot read-only."""
    try:
        snapshot, diagnostics = admit(root, work_id)
        editable = not diagnostics and snapshot is not None
        last_validated = False
        if diagnostics:
            try:
                snapshot = load_published(root, work_id)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                diagnostics = [*diagnostics, _diagnostic(
                    "EM007_GENERATION", f"work/{work_id}/engineering-model.json", str(exc))]
            last_validated = snapshot is not None
        if snapshot is None:
            return {"snapshot": None, "projection": None, "captured": None,
                    "editable": False, "last_validated": False, "diagnostics": diagnostics}
        return {"snapshot": snapshot.identity, "projection": project(snapshot, root, include_evidence=False),
                "captured": snapshot, "editable": editable, "last_validated": last_validated,
                "diagnostics": diagnostics}
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        return {"snapshot": None, "projection": None, "captured": None,
                "editable": False, "last_validated": False,
                "diagnostics": [_diagnostic("EM007_READ", f"work/{work_id}/engineering-model.json", str(exc))]}


def _capture_committed_view(root: Path, work_id: str, ref: str) -> dict:
    """Project a source resolved entirely from one immutable Git commit."""
    try:
        initial = read_snapshot(root, ref, work_id)
        commit = initial.commit
        files = dict(initial.files)
        requested = set()
        pending = set(referenced_paths(decode(files[f"work/{work_id}/engineering-model.json"])))
        while pending:
            batch = sorted(pending - requested)
            if not batch:
                break
            requested.update(batch)
            captured = read_snapshot(root, commit, work_id, paths=batch)
            files.update(captured.files)
            for relative in batch:
                raw = files.get(relative)
                if raw is None or not relative.endswith(".json"):
                    continue
                try:
                    linked = decode(raw)
                except (UnicodeError, ValueError, TypeError):
                    continue
                if not isinstance(linked, dict):
                    continue
                if linked.get("schema") == "ask-spec/v1":
                    pending.add(str(Path(relative).with_suffix(".md")))
                    feature = linked.get("feature_specification")
                    if isinstance(feature, str):
                        pending.add(feature)
                elif linked.get("schema") == "ask-feature-spec/v1":
                    parent = linked.get("extends")
                    if isinstance(parent, str):
                        pending.add(parent)
                elif linked.get("schema") == "ask-test-plan/v1":
                    linked_work = linked.get("work_id")
                    if isinstance(linked_work, str):
                        pending.add(f"specs/current/{linked_work}.json")
                        if linked.get("task_scopes"):
                            pending.add(f"work/{linked_work}/inner-loop/tasks.yaml")
                pending.update(referenced_paths(linked))
        statuses = {path: "present" if raw is not None else "missing"
                    for path, raw in files.items()}
        for path in requested:
            statuses.setdefault(path, "missing")
            files.setdefault(path, None)
        snapshot = Snapshot(work_id, MappingProxyType(files), MappingProxyType(statuses))
        projection = project(snapshot, root, include_evidence=False)
        # Runtime state is checkout-local. A historical source must not borrow it.
        for task in projection.get("workbench", {}).get("tasks", []):
            task.update(status="planned", status_source="no-runtime-record",
                        runtime_status=None, result_path=None)
        return {"snapshot": snapshot.identity, "projection": projection, "captured": snapshot,
                "editable": False, "last_validated": False, "diagnostics": list(initial.diagnostics),
                "source_context": {"ref": ref, "commit": commit}}
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        return {"snapshot": None, "projection": None, "captured": None,
                "editable": False, "last_validated": False,
                "diagnostics": [_diagnostic("EM008_COMMITTED_READ", f"work/{work_id}/engineering-model.json", str(exc))]}


def _show_diagnostics(diagnostics: list[dict]) -> None:
    for diagnostic in diagnostics:
        st.text("{} [{}]: {}".format(diagnostic.get("code", "unknown"),
                                     diagnostic.get("path", "$"),
                                     diagnostic.get("message", "")))


def _node_map(projection: dict) -> dict[str, dict]:
    return {node["id"]: node for node in projection["model"].get("nodes", [])}


def _markdown_escape(value: object) -> str:
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~-])", r"\\\1", str(value))


def _reference_label(reference: dict | None) -> str:
    if not reference:
        return ""
    return (str(reference.get("path", ""))
            + (f"#{reference['id']}" if reference.get("id") is not None else "")
            + (f"::{reference['symbol']}" if reference.get("symbol") is not None else ""))


def _show_evidence_error(message: object) -> None:
    text = str(message)
    if text.startswith("migration_required:"):
        st.warning(text)
    else:
        st.error(text)


def _without_debug_identifiers(value: object) -> object:
    """Keep hashes in the explicit debug panel, not ordinary evidence details."""
    hidden = {"candidate_sha", "current_sha", "digest", "input_digests", "plan_digest",
              "spec_digest", "review_digest", "source_digests", "yaml_digest"}
    if isinstance(value, dict):
        return {key: _without_debug_identifiers(item) for key, item in value.items()
                if key not in hidden and not key.endswith("_digest")}
    if isinstance(value, list):
        return [_without_debug_identifiers(item) for item in value]
    return value


def _current_commit(root: Path) -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                                capture_output=True, text=True, timeout=2, check=False)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _render_debug_trace(root: Path, work_id: str, snapshot_digest: str,
                        *, candidate_sha: str | None = None, key: str) -> None:
    details = st.expander("Debug trace and identifiers", expanded=False,
                          on_change="rerun", key=key)
    if not details.open:
        return
    with details:
        commit = candidate_sha or _current_commit(root)
        st.markdown("**Commit SHA**")
        st.write("Commit SHA identifies a Git revision. Use it to inspect that exact revision or ask the traceability evaluator to check it.")
        if commit:
            st.code(
                f"git show {commit}\n"
                f"./ask model show --work-id {work_id} --candidate {commit} --format markdown\n"
                f"./ask traceability check-completion {work_id} --candidate-sha {commit} --anchor-sha HEAD",
                language="bash")
        else:
            st.info("A Git commit SHA is unavailable for this model root. Substitute the commit you want to inspect in these commands.")
            st.code(
                f"git show <commit-sha>\n"
                f"./ask model show --work-id {work_id} --candidate <commit-sha> --format markdown\n"
                f"./ask traceability check-completion {work_id} --candidate-sha <commit-sha> --anchor-sha HEAD",
                language="bash")
        st.markdown("**Snapshot digest**")
        st.write("Snapshot digest fingerprints the admitted model and referenced inputs. It guards freshness for edits; it is not a Git commit, so `git show` cannot use it.")
        st.code(f"./ask model show --work-id {work_id}\n"
                f"./ask model edit --work-id {work_id} --expected {snapshot_digest} --batch proposal.json",
                language="bash")


def _contained_descendants(nodes: dict[str, dict], model: dict, parent_id: str) -> set[str]:
    children: dict[str, list[str]] = {}
    for edge in model.get("edges", []):
        if edge.get("type") == "contains":
            children.setdefault(edge.get("source"), []).append(edge.get("target"))
    found: set[str] = set()
    pending = list(children.get(parent_id, []))
    while pending:
        identity = pending.pop()
        if identity in found or identity not in nodes:
            continue
        found.add(identity)
        pending.extend(children.get(identity, []))
    return found


def _overview_epics(nodes: dict[str, dict], model: dict) -> list[dict]:
    parents = {edge.get("target") for edge in model.get("edges", [])
               if edge.get("type") == "contains"}
    root_intents = [node for identity, node in nodes.items()
                    if node.get("type") == "intent" and identity not in parents]
    if root_intents:
        return sorted(root_intents, key=lambda node: node["id"])
    root_features = [node for identity, node in nodes.items()
                     if node.get("type") == "feature" and identity not in parents]
    if root_features:
        return sorted(root_features, key=lambda node: node["id"])
    return sorted((node for node in nodes.values()
                   if node.get("type") in {"intent", "feature"}), key=lambda node: node["id"])


def _task_test_assignments(snapshot, work_id: str) -> dict[str, list[str]]:
    path = f"work/{work_id}/test-plan.json"
    raw = snapshot.files.get(path)
    if raw is None:
        return {}
    try:
        plan = json.loads(raw)
    except (UnicodeError, ValueError, TypeError):
        return {}
    return {str(scope.get("task_id")): [str(test_id) for test_id in scope.get("test_ids", [])]
            for scope in plan.get("task_scopes", []) if isinstance(scope, dict)
            and isinstance(scope.get("task_id"), str)}


def _result_label(record: dict | None) -> str:
    if record is None:
        return "No recorded result"
    final = record.get("final_execution")
    if isinstance(final, dict):
        outcome = final.get("outcome", "unknown")
        return "Passed" if outcome == "passed" else f"Final run: {outcome}"
    if record.get("red"):
        return "Baseline failed; final result missing"
    return "Final result missing"


def _find_test_result(result: dict | None, test_id: str) -> dict | None:
    if result is None:
        return None
    for scenario in result.get("scenarios", []):
        for record in (scenario.get("evidence") or {}).get("tests", []):
            if record.get("test_id") == test_id:
                return record
    return None


def _scenario_work_id(scenario: dict, default: str) -> str:
    path = str((scenario.get("reference") or {}).get("path", ""))
    parts = Path(path).parts
    return Path(parts[2]).stem if len(parts) == 3 and parts[:2] == ("specs", "current") else default


def _render_overview(projection: dict, snapshot, root: Path, work_id: str, context: str,
                     load_results, results_loaded: bool) -> None:
    nodes = _node_map(projection)
    model = projection.get("model", {})
    tasks = {item["id"]: item for item in projection.get("tasks", [])}
    scenarios = projection.get("scenarios", [])
    test_plan = _task_test_assignments(snapshot, work_id)
    loaded = st.session_state.get(STATE_OVERVIEW_RESULTS) or {}
    results_by_workstream = loaded.get("evidence", {}).get("by_workstream", {})

    epics = _overview_epics(nodes, model)
    st.subheader("Epic")
    if not epics:
        st.info("No epic is defined in this workstream.")
    for epic in epics:
        st.markdown(f"### {epic.get('title') or epic['id']}")
        if epic.get("description"):
            st.write(epic["description"])
        related = _contained_descendants(nodes, model, epic["id"])
        epic_scenarios = [item for item in scenarios if item["id"] in related]
        epic_tasks = [item for item in tasks.values() if item["id"] in related]
        st.markdown("#### Scenarios")
        if not epic_scenarios:
            st.caption("No scenarios are linked to this epic.")
        for scenario in epic_scenarios:
            with st.container(border=True):
                st.markdown(f"**{scenario.get('title') or scenario['id']}**")
                for field in ("given", "when", "then"):
                    if scenario.get(field):
                        st.markdown(f"**{field.title()}**")
                        value = scenario[field]
                        for entry in value if isinstance(value, list) else [value]:
                            st.write(entry)
                cases = scenario.get("tests", [])
                if cases:
                    st.markdown("**Tests**")
                for case in cases:
                    test_id = str((case.get("reference") or {}).get("id")
                                  or case.get("id", case.get("node_id", "Test")))
                    with st.container(border=True):
                        st.markdown(f"**{case.get('title') or test_id}**")
                        st.caption(f"Test {test_id} · {case.get('type', 'test')}")
                        scenario_work_id = _scenario_work_id(scenario, work_id)
                        record = _find_test_result(results_by_workstream.get(scenario_work_id), test_id)
                        if not loaded:
                            st.caption("Result not loaded")
                        else:
                            st.caption(f"Result · {_result_label(record)} · {scenario_work_id}")
                        for assertion in case.get("expected_assertions", []):
                            st.markdown(f"Planned assertions for {assertion.get('criterion_id', '')}")
                            for check in assertion.get("checks", []):
                                st.write(check)
                        source = _test_source(root, case)
                        if source:
                            source_path, code = source
                            st.markdown(f"Test source · `{source_path}`")
                            st.code(code, language="python", line_numbers=True)
                        else:
                            st.caption("Test source is not available in the current checkout.")
        st.markdown("#### Tasks")
        if not epic_tasks:
            st.info("No tasks in this snapshot." if not tasks else "No tasks are linked to this epic.")
        for task in sorted(epic_tasks, key=lambda item: item["id"]):
            node = nodes.get(task["id"], {})
            with st.container(border=True):
                st.markdown(f"**{node.get('title') or task['id']}**")
                st.badge(task["status"].replace("_", " ").title(),
                         color="orange" if task["status"] == "blocked" else "green")
                if node.get("description"):
                    st.write(node["description"])
                test_ids = test_plan.get(task["id"], [])
                if test_ids:
                    st.caption("Related tests: " + ", ".join(test_ids))
                else:
                    st.caption("No task-test link recorded.")

    st.markdown("#### Results")
    if not results_loaded:
        st.caption("Execution results are shown with their related tests and loaded only when requested.")
        st.button("Load test results", key="overview_load_results",
                  icon=":material/download:", on_click=load_results)
    else:
        if not results_by_workstream:
            st.info("No verification result is recorded for this workstream.")
        else:
            st.caption("Each result above is matched to the workstream named by its scenario reference.")

    identity = projection.get("snapshot", {}).get("digest", "unavailable")
    evidence = loaded.get("evidence", {})
    candidate = next((item.get("candidate_sha") for item in
                      evidence.get("by_workstream", {}).values()
                      if item.get("candidate_sha")), None)
    _render_debug_trace(root, work_id, identity, candidate_sha=candidate,
                        key=f"debug-trace:{context}")


def _selected_item(title: str, rows: list[dict], *, columns: list[str], context: str,
                        empty_message: str) -> dict | None:
    st.subheader(title)
    if not rows:
        st.info(empty_message)
        return None
    preferred = next((index for index, row in enumerate(rows) if row.get("_preferred")), 0)
    def label(row: dict) -> str:
        return " · ".join(str(row.get(column, "")) for column in columns[:3] if row.get(column, ""))
    by_id = {str(row["_id"]): row for row in rows}
    widget_key = f"item:{title}:{context}"
    if widget_key not in st.session_state:
        st.session_state[widget_key] = list(by_id)[preferred]
    selected_id = st.selectbox(title, options=list(by_id),
                               format_func=lambda identity: label(by_id[identity]),
                               key=widget_key, label_visibility="collapsed")
    return by_id[selected_id]


def _render_node(node: dict) -> None:
    st.markdown(f"#### {node.get('title') or node['id']}")
    st.caption(f"{node['id']} · {node['type']} · {node['lifecycle']}")
    if node.get("description"):
        st.text(node["description"])
    reference = node.get("reference")
    if reference:
        st.text(f"Reference: {reference.get('path', '')}"
                + (f"#{reference['id']}" if reference.get("id") is not None else "")
                + (f"::{reference['symbol']}" if reference.get("symbol") is not None else ""))
    history = node.get("history", [])
    if history:
        with st.expander(f"Decision history · {len(history)}", expanded=False):
            for event in history:
                history_text = "{}: {} — {}".format(
                    event.get("event", "history"), event.get("actor", ""), event.get("rationale", ""))
                st.caption(_markdown_escape(history_text))


def _render_objects(nodes: dict[str, dict], context: str) -> dict | None:
    rows = [{"_id": node_id, "ID": node_id, "Type": node["type"],
             "Title": node.get("title", ""), "Lifecycle": node["lifecycle"],
             "Reference": _reference_label(node.get("reference")),
             "_preferred": node["type"] == "decision" and
             (node["lifecycle"] == "open", bool(node.get("history")))}
            for node_id, node in sorted(nodes.items())]
    preferred = next((row["_id"] for row in rows if row["Type"] == "decision" and
                      row["Lifecycle"] == "open"), None)
    if preferred is None:
        preferred = next((row["_id"] for row in rows if row["Type"] == "decision"), None)
    for row in rows:
        row["_preferred"] = row["_id"] == preferred
    selected = _selected_item("Engineering objects", rows,
                                   columns=["ID", "Type", "Title", "Lifecycle", "Reference"],
                                   context=context,
                                   empty_message="No engineering objects in this snapshot.")
    with st.container(border=True):
        if selected is None:
            st.caption("Select an object to inspect its details.")
            return None
        node = nodes[selected["_id"]]
        _render_node(node)
    return node


def _render_nested(value: object, label: str, path: str = "root") -> None:
    """Show nested evidence in labeled fields and tables instead of an expanded JSON blob."""
    if isinstance(value, dict):
        simple = {key: item for key, item in value.items() if not isinstance(item, (dict, list))}
        if simple:
            st.table(pd.DataFrame([{"Field": key, "Value": str(item)}
                                   for key, item in simple.items()]))
        for key, item in value.items():
            if isinstance(item, (dict, list)) and item:
                if isinstance(item, list) and all(not isinstance(entry, (dict, list)) for entry in item):
                    st.markdown(f"**{key.replace('_', ' ').title()}**")
                    if key == "errors":
                        if not path.endswith(".completion"):
                            for entry in item:
                                _show_evidence_error(entry)
                    else:
                        _render_nested(item, key, f"{path}.{key}")
                    continue
                details = st.expander(f"{key.replace('_', ' ').title()} · {len(item)}",
                                      expanded=False, on_change="rerun",
                                      key=f"nested:{path}.{key}")
                if details.open:
                    with details:
                        _render_nested(item, key, f"{path}.{key}")
    elif isinstance(value, list):
        if all(not isinstance(item, (dict, list)) for item in value):
            st.table(pd.DataFrame([{"Value": str(item)} for item in value]))
        else:
            for index, item in enumerate(value):
                details = st.expander(f"{label} {index + 1}", expanded=False,
                                      on_change="rerun", key=f"nested:{path}[{index}]")
                if details.open:
                    with details:
                        _render_nested(item, label, f"{path}[{index}]")


def _test_source(root: Path, case: dict) -> tuple[str, str] | None:
    """Find the named test method in the plan's repository-local source files."""
    method_name = str(case.get("case_id", "")).rsplit(".", 1)[-1]
    if not method_name:
        return None
    for relative in case.get("source_paths", []):
        source_path = (root / relative).resolve()
        try:
            source_path.relative_to(root.resolve())
            source = source_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, UnicodeError, SyntaxError, ValueError):
            continue
        methods = [node for node in ast.walk(tree)
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and node.name == method_name]
        if methods:
            node = methods[0]
            return relative, "\n".join(source.splitlines()[node.lineno - 1:node.end_lineno])
    return None


def _render_scenarios(projection: dict, context: str) -> None:
    scenarios = projection.get("scenarios", [])
    rows = [{"_id": item["id"], "ID": item["id"], "Title": item.get("title", ""),
             "Reference": _reference_label(item.get("reference")),
             "Canonical": item.get("canonical_status", "available"),
             "Planned tests": len(item.get("tests", []))} for item in scenarios]
    selected = _selected_item("Scenarios and planned tests", rows,
                                   columns=["ID", "Title", "Reference", "Canonical", "Planned tests"],
                                   context=context,
                                   empty_message="No canonical scenarios are linked in this snapshot.")
    with st.container(border=True):
        if selected is None:
            st.caption("Select a scenario to inspect its behavior and planned tests.")
            return
        scenario = next(item for item in scenarios if item["id"] == selected["_id"])
        st.markdown(f"#### {scenario.get('title') or scenario['id']}")
        st.caption(f"{scenario['id']} · {_reference_label(scenario.get('reference'))}")
        if scenario.get("canonical_status") == "unavailable":
            st.warning("Canonical scenario details are unavailable in the captured snapshot.")
        for field in ("given", "when", "then"):
            if field in scenario:
                st.markdown(f"**{field.title()}**")
                value = scenario[field]
                for entry in value if isinstance(value, list) else [value]:
                    st.write(entry)
        cases = scenario.get("tests", [])
        if cases:
            def case_identity(case: dict) -> str:
                return str(case.get("node_id", case.get("id", "Test")))
            cases_by_id = {case_identity(case): case for case in cases}
            selected_case = st.selectbox(
                "Planned test", options=list(cases_by_id),
                format_func=lambda identity: f"{cases_by_id[identity].get('title', identity)} · {cases_by_id[identity].get('type', 'test')}",
                key=f"scenario-test:{context}:{scenario['id']}")
            selected_case = cases_by_id[selected_case]
            with st.container(border=True):
                st.markdown(f"#### {selected_case.get('title', selected_case.get('node_id', 'Test'))}")
                st.caption("{} · {} · runner {}".format(
                    selected_case.get("case_id", selected_case.get("id", "")),
                    selected_case.get("type", "test"), selected_case.get("runner_id", "unspecified")))
                if selected_case.get("canonical_status") == "unavailable":
                    st.warning("Planned case details are unavailable in the captured snapshot.")
                for assertion in selected_case.get("expected_assertions", []):
                    st.markdown(f"**Planned assertions for {assertion.get('criterion_id', '')}**")
                    for check in assertion.get("checks", []):
                        st.write(check)
                source = _test_source(root, selected_case)
                if source:
                    source_path, code = source
                    st.markdown(f"**Test source · `{source_path}`**")
                    st.code(code, language="python", line_numbers=True)
                else:
                    st.info("Test source is not available in the current checkout.")
        if scenario.get("evidence"):
            details = st.expander("Scenario evidence", expanded=False, on_change="rerun")
            if details.open:
                with details:
                        _render_nested(_without_debug_identifiers(scenario["evidence"]), "Scenario evidence",
                                       f"scenario:{scenario['id']}:evidence")


def _render_evidence(projection: dict, root: Path, context: str) -> None:
    st.subheader("Evidence records")
    # This is the adapter's complete read-only result, not a UI-derived outcome.
    evidence = projection.get("evidence", {})
    results = evidence.get("by_workstream", {})
    candidate = next((item.get("candidate_sha") for item in results.values()
                      if item.get("candidate_sha")), None)
    rows = [{"_id": work_id, "Workstream": work_id,
             "Status": result.get("status", "unknown"),
             "Historical": bool(result.get("historical")),
             "Current completion": bool(result.get("current_completion"))}
            for work_id, result in sorted(results.items())]
    selected = _selected_item("Evidence", rows,
                                   columns=["Workstream", "Status", "Historical", "Current completion"],
                                   context=projection["snapshot"]["digest"] + ":" + context + ":" + str(candidate),
                                   empty_message="No evidence adapter results are available.")
    with st.container(border=True):
        if selected:
            result = results[selected["_id"]]
            st.markdown(f"#### {selected['_id']}")
            st.caption("{} evidence{}; current completion: {}".format(
                result.get("status", "unknown"),
                " (historical)" if result.get("historical") else "",
                "yes" if result.get("current_completion") else "no"))
            for error in result.get("completion", {}).get("errors", []):
                _show_evidence_error(error)
            _render_nested(_without_debug_identifiers(result), "Evidence", f"evidence:{selected['_id']}")
        else:
            st.caption("Select a workstream to inspect its evidence record.")
    raw_details = st.expander("Raw evidence JSON", expanded=False,
                              on_change="rerun", key=f"raw-evidence:{context}")
    if raw_details.open:
        with raw_details:
            st.json(evidence, expanded=False)
    _render_debug_trace(root, selected["_id"] if selected else "unknown",
                        projection["snapshot"]["digest"], candidate_sha=candidate,
                        key=f"debug-trace:evidence:{context}")


def _render_decision(node: dict, editable: bool, root: Path, work_id: str, view: dict) -> None:
    if node.get("type") != "decision" or node.get("lifecycle") != "open":
        return
    st.subheader("Resolve decision")
    options = node.get("options", [])
    option_ids = [item["id"] for item in options]
    if not option_ids:
        st.info("This decision has no declared options.")
        return
    captured = st.session_state.get(STATE_FORM_IDENTITY)
    captured_for_work = (captured if isinstance(captured, dict)
                         and captured.get("work_id") == work_id else None)
    form_editable = bool(editable and captured_for_work and captured_for_work.get("editable"))
    if not form_editable:
        st.info("This source is read-only. Select the current working source and refresh before editing.")
    field_context = f"{work_id}:{node['id']}:{captured_for_work.get('digest') if captured_for_work else 'unavailable'}"
    with st.form(f"decision_resolution:{field_context}"):
        st.selectbox("Option", options=option_ids, key=f"decision-option:{field_context}",
                     disabled=not form_editable)
        st.text_input("Actor", key=f"decision-actor:{field_context}", disabled=not form_editable)
        st.text_area("Rationale", key=f"decision-rationale:{field_context}",
                     disabled=not form_editable)
        submitted = st.form_submit_button("Resolve decision", key="decision:submit",
                                          disabled=not form_editable)
    if not submitted:
        return
    actor = st.session_state.get(f"decision-actor:{field_context}", "")
    rationale = st.session_state.get(f"decision-rationale:{field_context}", "")
    option_id = st.session_state.get(f"decision-option:{field_context}", option_ids[0])
    if not actor.strip() or not rationale.strip():
        st.error("Actor and rationale are required to resolve a decision.")
        return
    proposal = {"commands": [{"op": "resolve_decision", "id": node["id"],
                              "option_id": option_id,
                              "actor": actor,
                              "rationale": rationale}]}
    expected_digest = (captured_for_work or {}).get("digest") or view["snapshot"]["digest"]
    result = edit(root, work_id, expected_digest, proposal)
    if not result["valid"]:
        st.session_state[STATE_FEEDBACK] = result.get("diagnostics", [])
        st.error("This decision form is stale. No change was saved; refresh to capture the current inputs.")
        return
    st.session_state[STATE_FEEDBACK] = []
    refreshed = _capture_view(root, work_id)
    st.session_state[STATE_VIEW] = refreshed
    st.session_state[STATE_WORK] = work_id
    st.session_state[STATE_CANDIDATE] = None
    st.session_state[STATE_EVIDENCE_PROJECTION] = None
    st.session_state[STATE_OVERVIEW_RESULTS] = None
    outline = build_outline(refreshed["projection"] or {})
    reset_for_work(st.session_state, work_id, refreshed,
                   outline["roots"][0] if outline["roots"] else "")
    st.rerun()


st.set_page_config(page_title="Engineering workbench", page_icon=":material/schema:", layout="wide")
st.title("Engineering workbench")
st.caption("Follow promised work through delivery tasks, tests, and recorded results.")

root = _model_root()
branch = _current_branch(root)
inventory = discover_work(root)
inventory_rows = {row["work_id"]: row for row in inventory.get("workstreams", [])}
work_ids = sorted(set(_workstreams(root)) | set(inventory_rows))
if not work_ids:
    st.warning("No Engineering Model workstreams were found under the configured model root.")
    st.text(str(root))
    st.stop()

if (st.session_state.get(STATE_BRANCH) != branch or "work_id" not in st.session_state
        or st.session_state.work_id not in work_ids):
    preferred = inventory.get("current_work_id")
    st.session_state.work_id = preferred if preferred in work_ids else _default_workstream(branch, work_ids)
    st.session_state[STATE_BRANCH] = branch
    st.session_state[STATE_VIEW] = None
    st.session_state[STATE_WORK] = None
with st.container(horizontal=True, vertical_alignment="bottom"):
    work_id = st.selectbox("Workstream", options=work_ids, key="work_id")
    source_ids = []
    if (root / "work" / work_id / "engineering-model.json").is_file():
        source_ids.append("working-tree")
    for row in inventory_rows.values():
        if row["work_id"] == work_id and row.get("model_status") == "available":
            ref = row.get("branch")
            if ref:
                source_ids.append(f"git:{ref}")
    if not source_ids:
        source_ids.append("working-tree")
    if st.session_state.get(STATE_WORK) != work_id or st.session_state.get(STATE_SOURCE_SELECTION) not in source_ids:
        source_row = inventory_rows.get(work_id, {})
        committed_ids = [value for value in source_ids if value.startswith("git:")]
        checked_out_work = inventory.get("current_work_id") == work_id
        preferred_source = (committed_ids[0] if source_row.get("read_only") and committed_ids and not checked_out_work else
                            "working-tree" if "working-tree" in source_ids else source_ids[0])
        st.session_state["source_id"] = preferred_source
        st.session_state[STATE_SOURCE_SELECTION] = preferred_source
    source_id = st.selectbox("Source", options=source_ids, key="source_id")
    refresh_inputs = st.button("Refresh", key="refresh", icon=":material/refresh:")

source_changed = st.session_state.get(STATE_SOURCE_SELECTION) != source_id
work_changed = st.session_state.get(STATE_WORK) != work_id
if work_changed or source_changed or STATE_VIEW not in st.session_state:
    if source_id == "working-tree":
        captured_view = _capture_view(root, work_id)
        source_kind, source_context = "working-tree", {}
    else:
        ref = source_id.removeprefix("git:")
        cache = st.session_state.setdefault(STATE_COMMITTED_SOURCE_CACHE, {})
        cache_key = (work_id, source_id)
        captured_view = cache.get(cache_key)
        if captured_view is None:
            captured_view = _capture_committed_view(root, work_id, ref)
            if captured_view.get("projection") is not None:
                cache[cache_key] = captured_view
        source_kind, source_context = "git-commit", captured_view.get("source_context", {"ref": ref})
    st.session_state[STATE_VIEW] = captured_view
    st.session_state[STATE_WORK] = work_id
    st.session_state[STATE_SOURCE_SELECTION] = source_id
    selected_view = st.session_state[STATE_VIEW]
    initial_outline = build_outline(selected_view["projection"] or {})
    reset_for_work(st.session_state, work_id, selected_view,
                   initial_outline["roots"][0] if initial_outline["roots"] else "",
                   source=source_kind, source_context=source_context)

view = st.session_state[STATE_VIEW]
projection = view.get("projection")
if projection is None:
    st.warning("Current inputs could not be admitted.")
    _show_diagnostics(view.get("diagnostics", []))
    st.error("No admitted or previously published snapshot is available for this workstream.")
    if refresh_inputs:
        if source_id == "working-tree":
            refreshed = _capture_view(root, work_id)
        else:
            cache = st.session_state.setdefault(STATE_COMMITTED_SOURCE_CACHE, {})
            cache.pop((work_id, source_id), None)
            refreshed = _capture_committed_view(root, work_id, source_id.removeprefix("git:"))
            if refreshed.get("projection") is not None:
                cache[(work_id, source_id)] = refreshed
        st.session_state[STATE_VIEW] = refreshed
        st.session_state[STATE_WORK] = work_id
        outline = build_outline(refreshed["projection"] or {})
        reset_for_work(st.session_state, work_id, refreshed,
                       outline["roots"][0] if outline["roots"] else "",
                       source="working-tree" if source_id == "working-tree" else "git-commit",
                       source_context=refreshed.get("source_context", {}))
        st.rerun()
    st.stop()

identity = view["snapshot"]
source_context = st.session_state.get(STATE_SOURCE, {})
source_label = ("Working tree" if source_context.get("kind") == "working-tree" else
                f"Committed · {source_context.get('ref', 'source')} · {source_context.get('commit', '')[:7]}")
with st.container(horizontal=True, vertical_alignment="center"):
    st.badge(source_label, icon=":material/source:", color="blue")
    st.badge("Validated inputs" if view["editable"] else "Read-only source" if source_context.get("kind") == "git-commit" else "Read-only snapshot",
             icon=":material/check_circle:" if view["editable"] else ":material/visibility:",
             color="green" if view["editable"] else "orange")
st.caption(f"Checkout: `{branch}` · Workstream: `{work_id}`")
if view["last_validated"]:
    st.warning("Showing last validated snapshot (read-only). Current working inputs were not admitted.")
elif view.get("diagnostics"):
    st.warning("Current inputs could not be admitted; the displayed snapshot is read-only.")
_show_diagnostics(view.get("diagnostics", []))

if refresh_inputs:
    if source_id == "working-tree":
        refreshed = _capture_view(root, work_id)
    else:
        cache = st.session_state.setdefault(STATE_COMMITTED_SOURCE_CACHE, {})
        cache.pop((work_id, source_id), None)
        refreshed = _capture_committed_view(root, work_id, source_id.removeprefix("git:"))
        if refreshed.get("projection") is not None:
            cache[(work_id, source_id)] = refreshed
    st.session_state[STATE_VIEW] = refreshed
    st.session_state[STATE_WORK] = work_id
    outline = build_outline(refreshed["projection"] or {})
    reset_for_work(st.session_state, work_id, refreshed,
                   outline["roots"][0] if outline["roots"] else "",
                   source="working-tree" if source_id == "working-tree" else "git-commit",
                   source_context=refreshed.get("source_context", {}))
    st.rerun()

projection = view["projection"]
navigation_col, detail_col = st.columns([1, 2], gap="large")
with navigation_col:
    outline = render_outline(projection)
route_id = st.session_state.get(STATE_ROUTE)
if route_id not in outline["ancestors"]:
    route_id = outline["roots"][0] if outline["roots"] else ""
    route_to(st.session_state, route_id)
with detail_col:
    with st.container(border=True):
        render_breadcrumbs(outline, route_id)
        selected = next((entry for entry in outline["entries"]
                         if entry["route_id"] == route_id), None)
        if selected is None:
            st.info("This workstream has no epic record yet.")
        elif selected["kind"] == "decision":
            selected_node = _node_map(projection).get(selected["node_id"])
            if selected_node:
                _render_decision(selected_node, view["editable"], root, work_id, view)
        elif selected["kind"] == "result":
            test_id = selected["node_id"]
            st.subheader("Result and evidence")
            st.caption(f"Selected test: {test_id}")
            st.info("Recorded execution details are available from this test's result once results are loaded.")
        elif selected["kind"] == "test":
            st.subheader(selected["label"])
            st.caption("Test · linked to its scenario and implementation task")
            st.info("Open Result / evidence in the outline to inspect a recorded execution.")
        elif selected["kind"] == "task":
            st.subheader(selected["label"])
            task = next((item for item in projection.get("workbench", {}).get("tasks", [])
                         if item["id"] == selected["node_id"]), {})
            st.caption(f"Task status: {task.get('status', 'not recorded')} · source: {task.get('record_source', 'unavailable')}")
        elif selected["kind"] == "scenario":
            scenario = next((item for item in projection.get("scenarios", [])
                             if item["id"] == selected["node_id"]), {})
            st.subheader(scenario.get("title") or selected["label"])
            if scenario.get("criterion_id"):
                st.caption(f"Canonical behavior · {scenario['criterion_id']}")
            if scenario.get("canonical_status") == "unavailable":
                st.warning("Canonical scenario details are unavailable in the captured source.")
        elif selected["kind"] == "story":
            st.subheader(selected["label"])
            st.caption("Recorded story in the current Engineering Model.")
        else:
            st.subheader(selected["label"])
            if selected["kind"] == "epic":
                st.caption("Epic · root of the selected workstream hierarchy")
                st.markdown("**Purpose**")
                st.write(selected["label"])
            else:
                st.info("Select a story, scenario, task, test, or result from this outline.")
feedback = st.session_state.get(STATE_FEEDBACK, [])
if feedback:
    st.error("The requested action or inspection did not succeed. The displayed snapshot was not refreshed.")
    _show_diagnostics(feedback)
