"""Selected test, source, execution and related-work detail."""
from __future__ import annotations

import streamlit as st

from workbench_debug import render_debug


def test_records(projection: dict) -> list[dict]:
    return list(projection.get("workbench", {}).get("tests", []))


def render_test(projection: dict, test_id: str, *, detail: dict | None = None,
                context: str = "test", on_open=None) -> None:
    tests = {str(item.get("id")): item for item in test_records(projection)}
    test = tests.get(str(test_id))
    if test is None:
        st.warning("This test is not present in the captured workstream.")
        return
    st.subheader(test.get("title") or test_id)
    st.caption(f"Selected test: {test_id} · revision-bound planned identity")
    if test.get("case_id"):
        st.write(f"Case: `{test['case_id']}` via `{test.get('runner_id', 'unspecified')}`")
    st.markdown("#### Expected assertions")
    for assertion in test.get("expected_assertions", []):
        st.markdown(f"**{assertion.get('criterion_id', 'criterion')}**")
        for check in assertion.get("checks", []):
            st.write(check)
    st.markdown("#### Related scenarios")
    scenarios = test.get("scenario_ids", [])
    if not scenarios:
        st.caption("No scenario relationship is recorded.")
    for scenario_id in scenarios:
        if on_open:
            st.button(f"Open scenario {scenario_id}", key=f"{context}:scenario:{scenario_id}",
                      on_click=on_open, args=("scenario", scenario_id))
        else:
            st.write(scenario_id)
    st.markdown("#### Test source")
    source_paths = test.get("source_paths", [])
    source = detail.get("source", {}) if isinstance(detail, dict) else {}
    if source.get("status") in {"working-tree", "current", "historical"} and source.get("source"):
        source_path = source.get("source_path") or (source_paths[0] if source_paths else "source")
        st.caption(f"Selected source path: {source_path}")
        st.code(source["source"], language="python")
    elif source_paths:
        st.caption("Selected source path: " + ", ".join(source_paths))
        if detail is not None:
            st.info("Test source is unavailable in this captured snapshot.")
            if source.get("diagnostic"):
                st.caption(str(source["diagnostic"]))
    else:
        st.info("Test source is unavailable in this captured snapshot.")
    st.markdown("#### Recorded execution")
    history = detail.get("execution_history", {}) if isinstance(detail, dict) else {}
    runs = history.get("runs", []) if isinstance(history, dict) else []
    evidence_state = detail.get("evidence", {}) if isinstance(detail, dict) else {}
    if evidence_state.get("status") == "historical" or any(
            run.get("source_status") == "historical" for run in runs if isinstance(run, dict)):
        st.caption("Historical evidence")
    if evidence_state.get("status") == "unavailable":
        st.info("Current evidence is unavailable for this selected test.")
    current_runs = [run for run in runs if isinstance(run, dict)
                    and run.get("source_status") == "current"
                    and run.get("output_status") == "valid"]
    if not current_runs:
        st.info("No recorded execution is attached to this selected test.")
    for run in runs:
        if not isinstance(run, dict):
            continue
        if run.get("outcome"):
            st.write("Outcome: " + str(run["outcome"]).replace("_", " ").title())
        if run.get("recorded_at"):
            st.write("Timestamp: " + str(run["recorded_at"]))
        if run.get("duration") is not None:
            st.write("Duration: " + str(run["duration"]))
        if run.get("diagnostic"):
            st.caption(str(run["diagnostic"]))
    evidence = test.get("evidence")
    if detail is None and not evidence:
        st.info("No recorded execution is attached to this selected test.")
    elif detail is None and evidence:
        st.write("Outcome: " + str(evidence.get("outcome", evidence.get("status", "unknown"))))
        st.write("Timestamp: " + str(evidence.get("timestamp", "unavailable")))
        st.write("Duration: " + str(evidence.get("duration", "unavailable")))
        if evidence.get("failure"):
            st.error(str(evidence["failure"]))
    render_debug(work_id=projection.get("work_id", "unknown"),
                 snapshot_digest=projection.get("snapshot", {}).get("digest", "unavailable"),
                 candidate_sha=(detail.get("candidate_sha") if isinstance(detail, dict) else None),
                 source_path=(source_paths[0] if source_paths else None), context=context)
