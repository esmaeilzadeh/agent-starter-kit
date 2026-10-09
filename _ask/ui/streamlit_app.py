"""Native Streamlit workbench over admitted Engineering Model snapshots."""
from __future__ import annotations

import os
from pathlib import Path
import re
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


def _model_root() -> Path:
    configured = os.environ.get("ASK_MODEL_ROOT")
    return Path(configured).expanduser().resolve() if configured else REPOSITORY_ROOT


def _workstreams(root: Path) -> list[str]:
    work = root / "work"
    if not work.is_dir():
        return []
    return sorted(path.parent.name for path in work.glob("*/engineering-model.json") if path.is_file())


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


def _selected_table_row(title: str, rows: list[dict], *, columns: list[str], context: str,
                        empty_message: str) -> dict | None:
    st.subheader(title)
    if not rows:
        st.info(empty_message)
        return None
    frame = pd.DataFrame([{column: row.get(column, "") for column in columns} for row in rows])
    key = f"table:{title}:{context}"
    preferred = next((index for index, row in enumerate(rows) if row.get("_preferred")), 0)
    event = st.dataframe(frame, column_order=columns, hide_index=True, key=key, row_height=36,
                         on_select="rerun", selection_mode="single-row",
                         selection_default={"selection": {"rows": [preferred]}})
    selected = event.selection.rows
    index = selected[0] if selected else preferred
    return rows[index]


def _render_tasks(projection: dict, nodes: dict[str, dict], context: str) -> None:
    tasks = projection.get("tasks", [])
    rows = [{"_id": task["id"], "ID": task["id"],
             "Title": nodes.get(task["id"], {}).get("title", ""),
             "Status": task["status"], "Lifecycle": task["lifecycle"],
             "Blockers": len(task["blockers"])} for task in tasks]
    selected = _selected_table_row("Tasks", rows,
                                   columns=["ID", "Title", "Status", "Lifecycle", "Blockers"],
                                   context=context, empty_message="No tasks in this snapshot.")
    with st.container(border=True):
        if selected:
            task = next(item for item in tasks if item["id"] == selected["_id"])
            st.markdown(f"#### {nodes.get(task['id'], {}).get('title') or task['id']}")
            st.caption(f"{task['id']} · {task['lifecycle']}")
            st.badge(task["status"].replace("_", " ").title(),
                     color="orange" if task["status"] == "blocked" else "green")
            description = nodes.get(task["id"], {}).get("description")
            if description:
                st.write(description)
            if task["blockers"]:
                st.markdown("**Blocked by**")
                st.table(pd.DataFrame([{"ID": item["id"], "Type": item["type"],
                                        "Reason": item["reason"]}
                                       for item in task["blockers"]]))
            else:
                st.caption("No unresolved prerequisites.")
        else:
            st.caption("Select a task to inspect its status and blockers.")


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
    selected = _selected_table_row("Engineering objects", rows,
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


def _render_nested(value: object, label: str) -> None:
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
                        for entry in item:
                            st.error(str(entry))
                    else:
                        _render_nested(item, key)
                    continue
                details = st.expander(f"{key.replace('_', ' ').title()} · {len(item)}",
                                      expanded=False, on_change="rerun")
                if details.open:
                    with details:
                        _render_nested(item, key)
    elif isinstance(value, list):
        if all(not isinstance(item, (dict, list)) for item in value):
            st.table(pd.DataFrame([{"Value": str(item)} for item in value]))
        else:
            for index, item in enumerate(value):
                details = st.expander(f"{label} {index + 1}", expanded=False, on_change="rerun")
                if details.open:
                    with details:
                        _render_nested(item, label)


def _render_scenarios(projection: dict, context: str) -> None:
    scenarios = projection.get("scenarios", [])
    rows = [{"_id": item["id"], "ID": item["id"], "Title": item.get("title", ""),
             "Reference": _reference_label(item.get("reference")),
             "Canonical": item.get("canonical_status", "available"),
             "Planned tests": len(item.get("tests", []))} for item in scenarios]
    selected = _selected_table_row("Scenarios and planned tests", rows,
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
            st.markdown("**Planned tests**")
            st.table(pd.DataFrame([
                {"Test node": case.get("node_id", ""),
                 "Title": case.get("title", ""),
                 "Case": case.get("case_id", case.get("id", "")),
                 "Type": case.get("type", ""), "Runner": case.get("runner_id", ""),
                 "Availability": case.get("canonical_status", "available")}
                for case in cases]))
            for case in cases:
                with st.expander(f"Test detail · {case.get('node_id', '')}", expanded=False):
                    if case.get("canonical_status") == "unavailable":
                        st.warning("Planned case details are unavailable in the captured snapshot.")
                    for assertion in case.get("expected_assertions", []):
                        st.markdown(f"**Planned assertions for {assertion.get('criterion_id', '')}**")
                        for check in assertion.get("checks", []):
                            st.write(check)
                    if case.get("source_paths"):
                        st.table(pd.DataFrame([{"Source": path} for path in case["source_paths"]]))
        if scenario.get("evidence"):
            details = st.expander("Scenario evidence", expanded=False, on_change="rerun")
            if details.open:
                with details:
                    _render_nested(scenario["evidence"], "Scenario evidence")


def _render_evidence(projection: dict) -> None:
    st.subheader("Evidence records")
    # This is the adapter's complete read-only result, not a UI-derived outcome.
    evidence = projection.get("evidence", {})
    results = evidence.get("by_workstream", {})
    candidate = next((item.get("candidate_sha") for item in results.values()
                      if item.get("candidate_sha")), "current")
    st.caption(f"Candidate revision: {candidate}")
    rows = [{"_id": work_id, "Workstream": work_id,
             "Status": result.get("status", "unknown"),
             "Candidate SHA": result.get("candidate_sha", ""),
             "Current SHA": result.get("current_sha", ""),
             "Historical": bool(result.get("historical")),
             "Current completion": bool(result.get("current_completion"))}
            for work_id, result in sorted(results.items())]
    selected = _selected_table_row("Evidence", rows,
                                   columns=["Workstream", "Status", "Candidate SHA", "Current SHA",
                                            "Historical", "Current completion"],
                                   context=projection["snapshot"]["digest"] + ":" + str(candidate),
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
                st.error(str(error))
            _render_nested(result, "Evidence")
        else:
            st.caption("Select a workstream to inspect its evidence record.")
    raw_details = st.expander("Raw evidence JSON", expanded=False, on_change="rerun")
    if raw_details.open:
        with raw_details:
            st.json(evidence, expanded=False)


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
    st.rerun()


st.set_page_config(page_title="Engineering workbench", page_icon=":material/schema:", layout="wide")
st.title("Engineering workbench")
st.caption("Inspect model state, planned behavior, and verification evidence.")

root = _model_root()
work_ids = _workstreams(root)
if not work_ids:
    st.warning("No Engineering Model workstreams were found under the configured model root.")
    st.text(str(root))
    st.stop()

if "work_id" not in st.session_state or st.session_state.work_id not in work_ids:
    st.session_state.work_id = work_ids[0]
with st.container(horizontal=True, vertical_alignment="bottom"):
    work_id = st.selectbox("Workstream", options=work_ids, key="work_id")
    refresh_inputs = st.button("Refresh inputs", key="refresh", icon=":material/refresh:")

if st.session_state.get(STATE_WORK) != work_id or STATE_VIEW not in st.session_state:
    st.session_state[STATE_VIEW] = _capture_view(root, work_id)
    st.session_state[STATE_WORK] = work_id
    st.session_state[STATE_CANDIDATE] = None
    st.session_state[STATE_EVIDENCE_PROJECTION] = None

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
status_col, snapshot_col = st.columns([1, 4], vertical_alignment="center")
with status_col:
    st.badge("Validated snapshot" if view["editable"] else "Read-only snapshot",
             icon=":material/check_circle:" if view["editable"] else ":material/visibility:",
             color="green" if view["editable"] else "orange")
with snapshot_col:
    st.caption(f"Snapshot: {identity['digest']}")
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
    st.rerun()

projection = view["projection"]
nodes = _node_map(projection)
section = st.segmented_control(
    "Workbench section",
    ["Overview", "Objects", "Scenarios", "Evidence"],
    key="workbench_section", default="Overview", label_visibility="collapsed",
    selection_mode="single", required=True, width="stretch")

if section == "Overview":
    tasks = projection.get("tasks", [])
    model_nodes = projection.get("model", {}).get("nodes", [])
    open_decisions = sum(node.get("type") == "decision" and node.get("lifecycle") == "open"
                         for node in model_nodes)
    blocked_tasks = sum(task.get("status") == "blocked" for task in tasks)
    metric_cols = st.columns(3)
    metric_cols[0].metric("Tasks", len(tasks))
    metric_cols[1].metric("Blocked", blocked_tasks, delta_color="inverse")
    metric_cols[2].metric("Open decisions", open_decisions, delta_color="inverse")
    _render_tasks(projection, nodes, f"{work_id}:{identity['digest']}")

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
    _render_evidence(candidate_projection or _get_evidence_projection())
feedback = st.session_state.get(STATE_FEEDBACK, [])
if feedback:
    st.error("The requested action or inspection did not succeed. The displayed snapshot was not refreshed.")
    _show_diagnostics(feedback)
