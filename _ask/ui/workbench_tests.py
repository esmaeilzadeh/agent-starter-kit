"""Selected test, source, execution and related-work detail."""
from __future__ import annotations

import streamlit as st

from workbench_debug import render_debug
from workbench_loading import inspect_historical_contract_candidate


def test_records(projection: dict) -> list[dict]:
    return list(projection.get("workbench", {}).get("tests", []))


def render_test(projection: dict, test_id: str, *, detail: dict | None = None,
                context: str = "test", on_open=None, root=None,
                show_execution: bool = True) -> None:
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
    readable = detail.get("readable_test", {}) if isinstance(detail, dict) else {}
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
    flow = readable.get("flow") if isinstance(readable, dict) else None
    if isinstance(flow, dict):
        st.markdown("#### Selected behavior flow")
        for label, key in (("Setup", "given"), ("Action", "when"), ("Expected result", "then")):
            value = flow.get(key)
            if value:
                st.markdown(f"**{label}**")
                for item in value if isinstance(value, list) else [value]:
                    st.write(item)
    contexts = readable.get("context", []) if isinstance(readable, dict) else []
    visible_contexts = [item for item in contexts if isinstance(item, dict)
                        and item.get("role") in {"setup", "helper", "fixture"}]
    if visible_contexts:
        st.markdown("#### Setup and helpers")
        for index, item in enumerate(visible_contexts):
            selector = str(item.get("selector", "source"))
            role = str(item.get("role", "helper"))
            label = f"{role.title()} · {selector}"
            with st.expander(label, expanded=False,
                             key=f"source-context:{context}:{test_id}:{index}:{selector}"):
                st.caption(f"Selected revision: {item.get('source_sha') or 'unavailable'}")
                st.caption(f"Source path: {item.get('source_path') or 'unavailable'}")
                if item.get("status") == "available" and item.get("source"):
                    st.code(item["source"], language="python")
                else:
                    st.info(item.get("diagnostic") or "This helper is unavailable at the selected revision.")
    if not show_execution:
        return
    st.markdown("#### Recorded execution")
    history = detail.get("execution_history", {}) if isinstance(detail, dict) else {}
    runs = history.get("runs", []) if isinstance(history, dict) else []
    evidence_state = detail.get("evidence", {}) if isinstance(detail, dict) else {}
    historical_candidates = detail.get("historical_candidates", []) if isinstance(detail, dict) else []
    if evidence_state.get("status") == "historical" or any(
            run.get("source_status") == "historical" for run in runs if isinstance(run, dict)):
        st.caption("Historical evidence")
    if evidence_state.get("status") == "unavailable":
        st.info("Current evidence is unavailable for this selected test.")
        if evidence_state.get("diagnostic"):
            st.caption(str(evidence_state["diagnostic"]))
    elif evidence_state.get("status") == "invalid" and evidence_state.get("diagnostic"):
        st.warning(str(evidence_state["diagnostic"]))
    current_runs = [run for run in runs if isinstance(run, dict)
                    and run.get("source_status") == "current"
                    and run.get("output_status") == "valid"]
    if runs and not current_runs:
        st.info("No current recorded execution is attached to this selected revision.")
    elif not runs and historical_candidates:
        st.info("No retained execution matches the current test contract.")
    elif not runs:
        st.info("No recorded execution is attached to this selected test.")
    for run in runs:
        if not isinstance(run, dict):
            continue
        if run.get("outcome"):
            st.write("Recorded outcome: " + str(run["outcome"]).replace("_", " ").title())
        output_status = run.get("output_status", "unavailable")
        source_status = run.get("source_status", "unavailable")
        st.write("Output integrity: " + str(output_status))
        st.write("Git candidate currency: " + str(source_status))
        applicability = run.get("working_source_applicability", "unavailable")
        applicability_label = ("Working source applicability" if
                                detail.get("context_kind") == "working-tree" else
                                "Selected source applicability")
        st.write(f"{applicability_label}: {applicability}")
        if output_status != "valid" or source_status not in {"current", "historical"}:
            st.error("Untrusted execution evidence; this recorded outcome is not a verified pass.")
        elif source_status == "historical":
            st.caption("This retained outcome belongs to a historical source revision.")
        run_id = str(run.get("run_id", "unavailable"))
        execution_label = f"Execution details · {run_id}"
        with st.expander(execution_label, expanded=False,
                         key=f"execution:{context}:{test_id}:{run_id}"):
            st.caption(f"Work: {run.get('work_id', projection.get('work_id', 'unknown'))} · "
                       f"Test: {run.get('test_id', test_id)} · Case: {run.get('case_id', test.get('case_id', 'unavailable'))}")
            st.caption("Run ID: " + run_id)
            st.caption("Runner (validated against selected test): " + str(test.get("runner_id", "unavailable")))
            st.caption("Phase: " + str(run.get("phase", "unavailable")) +
                       " · Scope: " + str(run.get("scope", "unavailable")) +
                       " · Task: " + str(run.get("task_id", "unavailable")))
            artifact = run.get("output_artifact")
            st.caption("Execution ID: unavailable (not exposed by retained history)")
            st.caption("Output artifact: " + str(artifact or "unavailable"))
            st.caption("Candidate: " + str(run.get("candidate_sha", "unavailable")))
            st.caption("Source revision: " + str(run.get("source_sha", "unavailable")))
            st.caption("Contract: spec " + str(run.get("spec_digest", "unavailable")) +
                       " · plan " + str(run.get("plan_digest", "unavailable")))
            st.write("Timestamp: " + str(run.get("recorded_at") or "unavailable"))
            st.write("Duration: " + (str(run["duration"]) if run.get("duration") is not None
                                      else "unavailable"))
            if run.get("failure_kind"):
                st.write("Failure detail: " + str(run["failure_kind"]).replace("_", " "))
            if run.get("diagnostic"):
                st.caption(str(run["diagnostic"]))
            if run.get("output_text"):
                st.markdown("**Captured execution output**")
                st.code(run["output_text"], language="text")
    if not runs and isinstance(history, dict) and history.get("diagnostic"):
        if history.get("status") == "invalid":
            st.warning(str(history["diagnostic"]))
        else:
            st.info(str(history["diagnostic"]))
    if historical_candidates and root is not None:
        st.markdown("#### Historical contract evidence")
        st.caption("Inspect a retained contract candidate to view its recorded outcomes. These records do not verify the current contract.")
        detail_identity = str(detail.get("identity", "selected-detail"))
        candidate_key = f"historical-candidate:{detail_identity}"
        selected_candidate = st.selectbox(
            "Historical contract candidate",
            options=historical_candidates,
            format_func=lambda _candidate, index_map={value: index + 1 for index, value in
                                                       enumerate(historical_candidates)}:
                f"Retained candidate {index_map[_candidate]}",
            key=candidate_key,
        )
        inspected_key = f"historical-inspection:{detail_identity}:{selected_candidate}"
        if st.button("Inspect candidate", key=f"historical-inspect:{detail_identity}"):
            st.session_state[inspected_key] = inspect_historical_contract_candidate(
                root, str(projection.get("work_id", "")), test, selected_candidate)
        historical_contracts = st.session_state.get(inspected_key)
        if historical_contracts is None:
            st.caption("No candidate has been inspected for this selected work, source and test.")
        for index, record in enumerate(historical_contracts or []):
            inspection_status = str(record.get("inspection_status", "unavailable"))
            if inspection_status != "historical":
                st.error(f"Historical candidate inspection: {inspection_status}")
                if record.get("inspection_diagnostic"):
                    st.caption("Inspection diagnostic: " + str(record["inspection_diagnostic"]))
                continue
            if record.get("identity_status") == "no_match":
                st.info("No retained historical contract matches this exact selected test identity.")
                continue
            if not record.get("executions"):
                st.info("The historical contract matches this test, but it has no retained execution outcomes.")
                continue
            st.caption(f"Historical candidate: {record.get('candidate_sha', 'unavailable')} · "
                       f"Criterion: {record.get('criterion_id', 'unavailable')}")
            st.caption("Historical contract: spec " + str(record.get("spec_digest", "unavailable")) +
                       " · plan " + str(record.get("plan_digest", "unavailable")))
            for retained in record.get("executions", []):
                execution = retained.get("execution", {})
                st.caption("Execution ID: " + str(execution.get("execution_id", "unavailable")))
                st.caption("Runner: " + str(execution.get("runner_id", test.get("runner_id", "unavailable"))) +
                           " · Phase: " + str(retained.get("phase", "unavailable")))
                st.write("Recorded historical outcome: " +
                         str(execution.get("outcome", "unavailable")).replace("_", " ").title())
                st.caption("Source revision: " + str(execution.get("source_sha", "unavailable")))
                st.caption("Output artifact: " + str(execution.get("output_artifact", "unavailable")))
                if execution.get("failure_kind"):
                    st.write("Failure detail: " + str(execution["failure_kind"]).replace("_", " "))
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
