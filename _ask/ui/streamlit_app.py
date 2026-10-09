"""Native Streamlit workbench over admitted Engineering Model snapshots."""
from __future__ import annotations

import os
from pathlib import Path
import re
import sys

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
        return {"snapshot": snapshot.identity, "projection": project(snapshot, root),
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


def _render_tasks(projection: dict) -> None:
    st.subheader("Tasks")
    tasks = projection.get("tasks", [])
    if not tasks:
        st.text("No tasks in this snapshot.")
    for task in tasks:
        # Admitted IDs/statuses are constrained by the Engineering Model schema.
        st.markdown(f"{task['id']}: {task['status']}")


def _render_node(node: dict) -> None:
    st.header("Engineering object")
    st.text(f"{node['id']} · {node['type']} · {node['lifecycle']}")
    st.text(node.get("title", ""))
    if node.get("description"):
        st.text(node["description"])
    reference = node.get("reference")
    if reference:
        st.text(f"Reference: {reference.get('path', '')}"
                + (f"#{reference['id']}" if reference.get("id") is not None else "")
                + (f"::{reference['symbol']}" if reference.get("symbol") is not None else ""))
    for event in node.get("history", []):
        history_text = "{}: {} — {}".format(
            event.get("event", "history"), event.get("actor", ""), event.get("rationale", ""))
        st.text(history_text)
        st.caption(_markdown_escape(history_text))


def _render_scenarios(projection: dict) -> None:
    st.subheader("Canonical scenarios and planned tests")
    scenarios = projection.get("scenarios", [])
    if not scenarios:
        st.text("No canonical scenarios are linked in this snapshot.")
    for scenario in scenarios:
        st.markdown(f"**{scenario['id']}**")
        st.text(scenario.get("title", ""))
        ref = scenario.get("reference", {})
        st.text(f"Reference: {ref.get('path', '')}"
                + (f"#{ref['id']}" if ref.get("id") is not None else "")
                + (f"::{ref['symbol']}" if ref.get("symbol") is not None else ""))
        for field in ("given", "when", "then"):
            if field not in scenario:
                continue
            value = scenario[field]
            values = value if isinstance(value, list) else [value]
            for entry in values:
                st.text(f"{field}: {entry}")
        if scenario.get("canonical_status") == "unavailable":
            st.text("Canonical scenario details are unavailable in the captured snapshot.")
        for case in scenario.get("tests", []):
            st.text(f"Test node: {case.get('node_id', '')}")
            st.text(f"Test reference: {case.get('reference', {}).get('path', '')}"
                    + (f"#{case['reference']['id']}" if case.get("reference", {}).get("id") is not None else "")
                    + (f"::{case['reference']['symbol']}" if case.get("reference", {}).get("symbol") is not None else ""))
            if case.get("case_id"):
                st.text(f"Case: {case['case_id']} via {case.get('runner_id', '')} ({case.get('type', '')})")
            for assertion in case.get("expected_assertions", []):
                st.text(f"Planned assertions for {assertion.get('criterion_id', '')}:")
                for check in assertion.get("checks", []):
                    st.text(f"- {check}")


def _render_evidence(projection: dict) -> None:
    st.subheader("Evidence adapter inspection")
    # This is the adapter's complete read-only result, not a UI-derived outcome.
    st.json(projection.get("evidence", {}), expanded=2)


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
    st.rerun()


st.set_page_config(page_title="Engineering Model", layout="wide")
st.title("Engineering Model")

root = _model_root()
work_ids = _workstreams(root)
if not work_ids:
    st.warning("No Engineering Model workstreams were found under the configured model root.")
    st.text(str(root))
    st.stop()

if "work_id" not in st.session_state or st.session_state.work_id not in work_ids:
    st.session_state.work_id = work_ids[0]
work_id = st.selectbox("Workstream", options=work_ids, key="work_id")

if st.session_state.get(STATE_WORK) != work_id or STATE_VIEW not in st.session_state:
    st.session_state[STATE_VIEW] = _capture_view(root, work_id)
    st.session_state[STATE_WORK] = work_id
    st.session_state[STATE_CANDIDATE] = None

view = st.session_state[STATE_VIEW]
projection = view.get("projection")
if projection is None:
    st.warning("Current inputs could not be admitted.")
    _show_diagnostics(view.get("diagnostics", []))
    st.error("No admitted or previously published snapshot is available for this workstream.")
    if st.button("Refresh inputs", key="refresh"):
        st.session_state[STATE_VIEW] = _capture_view(root, work_id)
        st.rerun()
    st.stop()

identity = view["snapshot"]
st.caption(f"Snapshot: {identity['digest']}")
if view["last_validated"]:
    st.warning("Showing last validated snapshot (read-only). Current working inputs were not admitted.")
elif view.get("diagnostics"):
    st.warning("Current inputs could not be admitted; the displayed snapshot is read-only.")
_show_diagnostics(view.get("diagnostics", []))

if st.button("Refresh inputs", key="refresh"):
    st.session_state[STATE_VIEW] = _capture_view(root, work_id)
    st.session_state[STATE_WORK] = work_id
    st.session_state[STATE_CANDIDATE] = None
    st.rerun()

projection = view["projection"]
_render_tasks(projection)
nodes = _node_map(projection)
node_ids = sorted(nodes)
if "object_id" not in st.session_state or st.session_state.object_id not in node_ids:
    st.session_state.object_id = node_ids[0]
object_id = st.selectbox("Engineering object", options=node_ids, key="object_id")
selected_node = nodes[object_id]
_render_node(selected_node)
_render_decision(selected_node, view["editable"], root, work_id, view)

_render_scenarios(projection)

with st.form("evidence_candidate_inspection"):
    st.text_input("Evidence candidate", key="candidate_sha", placeholder="Empty means current checkout")
    inspect_candidate = st.form_submit_button("Inspect evidence candidate", key="inspect_candidate")
if inspect_candidate:
    try:
        st.session_state[STATE_CANDIDATE] = project(
            view["captured"], root,
            candidate_sha=st.session_state.candidate_sha.strip() or None,
        )
        st.session_state[STATE_FEEDBACK] = []
    except (OSError, ValueError, KeyError, TypeError) as exc:
        st.session_state[STATE_FEEDBACK] = [_diagnostic("EM007_EVIDENCE", "$candidate_sha", str(exc))]

candidate_projection = st.session_state.get(STATE_CANDIDATE)
_render_evidence(candidate_projection or projection)
feedback = st.session_state.get(STATE_FEEDBACK, [])
if feedback:
    st.error("The requested action or inspection did not succeed. The displayed snapshot was not refreshed.")
    _show_diagnostics(feedback)
