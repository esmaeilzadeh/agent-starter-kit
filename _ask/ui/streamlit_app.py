"""Native Streamlit workbench over admitted Engineering Model snapshots."""
from __future__ import annotations

import os
from pathlib import Path
import re
import ast
import json
import subprocess
import sys

import pandas as pd
import streamlit as st


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_ROOT = REPOSITORY_ROOT / "_ask" / "scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from engineering_model.actions import edit
from engineering_model.admission import admit, load_published
from engineering_model.projection import project


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


def _render_overview(projection: dict, snapshot, root: Path, work_id: str, context: str,
                     load_results, results_loaded: bool) -> None:
    nodes = _node_map(projection)
    model = projection.get("model", {})
    tasks = {item["id"]: item for item in projection.get("tasks", [])}
    scenarios = projection.get("scenarios", [])
    test_plan = _task_test_assignments(snapshot, work_id)

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
                    test_id = str(case.get("case_id", case.get("id", case.get("node_id", "Test"))))
                    with st.container(border=True):
                        st.markdown(f"**{case.get('title') or test_id}**")
                        st.caption(f"{test_id} · {case.get('type', 'test')}")
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
        st.caption("Test execution results are loaded only when requested.")
        st.button("Load test results", key="overview_load_results",
                  icon=":material/download:", on_click=load_results)
    else:
        evidence = st.session_state.get(STATE_OVERVIEW_RESULTS, {}).get("evidence", {})
        by_workstream = evidence.get("by_workstream", {})
        records = [record for result in by_workstream.values()
                   for scenario in result.get("scenarios", [])
                   for record in (scenario.get("evidence") or {}).get("tests", [])]
        if not records:
            st.info("No test results are recorded for this workstream.")
        for record in records:
            st.markdown(f"**{record.get('test_id', 'Test')}** · {_result_label(record)}")
        for result in by_workstream.values():
            for error in result.get("completion", {}).get("errors", []):
                _show_evidence_error(error)

    identity = projection.get("snapshot", {}).get("digest", "unavailable")
    loaded = st.session_state.get(STATE_OVERVIEW_RESULTS) or {}
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
    with st.form("decision_resolution"):
        st.selectbox("Option", options=option_ids, key="option_id", disabled=not editable)
        st.text_input("Actor", key="actor", disabled=not editable)
        st.text_area("Rationale", key="rationale", disabled=not editable)
        submitted = st.form_submit_button("Resolve decision", key="resolve", disabled=not editable)
    if not submitted:
        return
    proposal = {"commands": [{"op": "resolve_decision", "id": node["id"],
                              "option_id": st.session_state.option_id,
                              "actor": st.session_state.actor,
                              "rationale": st.session_state.rationale}]}
    result = edit(root, work_id, view["snapshot"]["digest"], proposal)
    if not result["valid"]:
        st.session_state[STATE_FEEDBACK] = result.get("diagnostics", [])
        return
    st.session_state[STATE_FEEDBACK] = []
    refreshed = _capture_view(root, work_id)
    st.session_state[STATE_VIEW] = refreshed
    st.session_state[STATE_WORK] = work_id
    st.session_state[STATE_CANDIDATE] = None
    st.session_state[STATE_EVIDENCE_PROJECTION] = None
    st.session_state[STATE_OVERVIEW_RESULTS] = None
    st.rerun()


st.set_page_config(page_title="Engineering workbench", page_icon=":material/schema:", layout="wide")
st.title("Engineering workbench")
st.caption("Inspect model state, planned behavior, and verification evidence.")

root = _model_root()
branch = _current_branch(root)
work_ids = _workstreams(root)
if not work_ids:
    st.warning("No Engineering Model workstreams were found under the configured model root.")
    st.text(str(root))
    st.stop()

if (st.session_state.get(STATE_BRANCH) != branch or "work_id" not in st.session_state
        or st.session_state.work_id not in work_ids):
    st.session_state.work_id = _default_workstream(branch, work_ids)
    st.session_state[STATE_BRANCH] = branch
    st.session_state[STATE_VIEW] = None
    st.session_state[STATE_WORK] = None
with st.container(horizontal=True, vertical_alignment="bottom"):
    work_id = st.selectbox("Workstream in current branch", options=work_ids, key="work_id")
    refresh_inputs = st.button("Refresh inputs", key="refresh", icon=":material/refresh:")
st.caption(f"Branch: `{branch}`. This view reads workstreams from this checkout only; use the selector to switch among workstreams on this branch. To inspect work from another branch, check out that branch and refresh the page.")

if st.session_state.get(STATE_WORK) != work_id or STATE_VIEW not in st.session_state:
    st.session_state[STATE_VIEW] = _capture_view(root, work_id)
    st.session_state[STATE_WORK] = work_id
    st.session_state[STATE_CANDIDATE] = None
    st.session_state[STATE_EVIDENCE_PROJECTION] = None
    st.session_state[STATE_OVERVIEW_RESULTS] = None

view = st.session_state[STATE_VIEW]
projection = view.get("projection")
if projection is None:
    st.warning("Current inputs could not be admitted.")
    _show_diagnostics(view.get("diagnostics", []))
    st.error("No admitted or previously published snapshot is available for this workstream.")
    if refresh_inputs:
        st.session_state[STATE_VIEW] = _capture_view(root, work_id)
        st.rerun()
    st.stop()

identity = view["snapshot"]
with st.container(horizontal=True, vertical_alignment="center"):
    st.badge("Validated snapshot" if view["editable"] else "Read-only snapshot",
             icon=":material/check_circle:" if view["editable"] else ":material/visibility:",
             color="green" if view["editable"] else "orange")
if view["last_validated"]:
    st.warning("Showing last validated snapshot (read-only). Current working inputs were not admitted.")
elif view.get("diagnostics"):
    st.warning("Current inputs could not be admitted; the displayed snapshot is read-only.")
_show_diagnostics(view.get("diagnostics", []))

if refresh_inputs:
    st.session_state[STATE_VIEW] = _capture_view(root, work_id)
    st.session_state[STATE_WORK] = work_id
    st.session_state[STATE_CANDIDATE] = None
    st.session_state[STATE_EVIDENCE_PROJECTION] = None
    st.session_state[STATE_OVERVIEW_RESULTS] = None
    st.rerun()

projection = view["projection"]
nodes = _node_map(projection)
st.session_state.setdefault("workbench_section", "Overview")
section = st.segmented_control(
    "Workbench section",
    ["Overview", "Objects", "Scenarios", "Evidence"],
    key="workbench_section", label_visibility="collapsed",
    selection_mode="single", required=True, width="stretch")

overview_context = f"{work_id}:{identity['digest']}"
if section == "Overview":
    def load_overview_results():
        with st.spinner("Loading test results…"):
            st.session_state[STATE_OVERVIEW_RESULTS] = project(view["captured"], root)

    _render_overview(projection, view["captured"], root, work_id, overview_context,
                     load_overview_results,
                     st.session_state.get(STATE_OVERVIEW_RESULTS) is not None)

if section == "Objects":
    selected_node = _render_objects(nodes, f"{work_id}:{identity['digest']}:objects")
    if selected_node is not None:
        _render_decision(selected_node, view["editable"], root, work_id, view)

def _get_evidence_projection() -> dict:
    cached = st.session_state.get(STATE_EVIDENCE_PROJECTION)
    if cached is None:
        with st.spinner("Loading verification evidence…"):
            cached = project(view["captured"], root)
        st.session_state[STATE_EVIDENCE_PROJECTION] = cached
    return cached

if section == "Scenarios":
    _render_scenarios(_get_evidence_projection(), f"{work_id}:{identity['digest']}:scenarios")

if section == "Evidence":
    with st.form("evidence_candidate_inspection", border=False):
        input_col, action_col = st.columns([3, 1], vertical_alignment="bottom")
        input_col.text_input("Evidence candidate", key="candidate_sha",
                             placeholder="Empty means current checkout")
        inspect_candidate = action_col.form_submit_button(
            "Inspect candidate", key="inspect_candidate", icon=":material/search:", type="primary")
    if inspect_candidate:
        try:
            with st.spinner("Inspecting candidate evidence…"):
                st.session_state[STATE_CANDIDATE] = project(
                    view["captured"], root,
                    candidate_sha=st.session_state.candidate_sha.strip() or None,
                )
            st.session_state[STATE_FEEDBACK] = []
        except (OSError, ValueError, KeyError, TypeError) as exc:
            st.session_state[STATE_CANDIDATE] = None
            st.session_state[STATE_FEEDBACK] = [_diagnostic("EM007_EVIDENCE", "$candidate_sha", str(exc))]

    candidate_projection = st.session_state.get(STATE_CANDIDATE)
    _render_evidence(candidate_projection or _get_evidence_projection(), root,
                     f"{work_id}:{identity['digest']}:{candidate_projection is not None}")
feedback = st.session_state.get(STATE_FEEDBACK, [])
if feedback:
    st.error("The requested action or inspection did not succeed. The displayed snapshot was not refreshed.")
    _show_diagnostics(feedback)
