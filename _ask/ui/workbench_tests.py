"""Selected test, source, execution and related-work detail."""
from __future__ import annotations

import streamlit as st

from workbench_debug import render_debug


def test_records(projection: dict) -> list[dict]:
    return list(projection.get("workbench", {}).get("tests", []))


def render_test(projection: dict, test_id: str, *, context: str = "test",
                on_open=None) -> None:
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
    if source_paths:
        st.caption("Selected source path: " + ", ".join(source_paths))
    else:
        st.info("Test source is unavailable in this captured snapshot.")
    st.markdown("#### Recorded execution")
    evidence = test.get("evidence")
    if not evidence:
        st.info("No recorded execution is attached to this selected test.")
    else:
        st.write("Outcome: " + str(evidence.get("outcome", evidence.get("status", "unknown"))))
        st.write("Timestamp: " + str(evidence.get("timestamp", "unavailable")))
        st.write("Duration: " + str(evidence.get("duration", "unavailable")))
        if evidence.get("failure"):
            st.error(str(evidence["failure"]))
    render_debug(work_id=projection.get("work_id", "unknown"),
                 snapshot_digest=projection.get("snapshot", {}).get("digest", "unavailable"),
                 source_path=(source_paths[0] if source_paths else None), context=context)
