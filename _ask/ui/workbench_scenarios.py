"""Canonical scenario detail with explicitly recorded delivery mappings."""
from __future__ import annotations

import streamlit as st


def scenario_relationships(projection: dict, scenario_id: str) -> dict:
    scenario_id = str(scenario_id)
    scenarios = {str(item.get("id")): item for item in projection.get("scenarios", [])}
    scenario = scenarios.get(scenario_id)
    if scenario is None:
        return {"scenario": None, "tasks": [], "tests": []}
    tasks = [task for task in projection.get("workbench", {}).get("tasks", [])
             if any(str(link.get("id")) == scenario_id
                    for link in task.get("related_scenarios", []))]
    tests = [test for test in projection.get("workbench", {}).get("tests", [])
             if scenario_id in {str(item) for item in test.get("scenario_ids", [])}]
    # Projection fixtures may carry canonical tests without a second workbench
    # index. Deduplicate by stable case identity while retaining all mappings.
    known = {str(test.get("id")) for test in tests}
    for test in scenario.get("tests", []):
        identity = str(test.get("id") or test.get("reference", {}).get("id") or test.get("node_id", ""))
        if identity and identity not in known:
            tests.append({**test, "id": identity})
            known.add(identity)
    return {"scenario": scenario, "tasks": tasks, "tests": tests}


def render_scenario(projection: dict, scenario_id: str, *, on_open=None) -> None:
    related = scenario_relationships(projection, scenario_id)
    scenario = related["scenario"]
    if scenario is None:
        st.warning("This scenario is not present in the captured workstream.")
        return
    st.subheader(scenario.get("title") or scenario.get("id"))
    reference = scenario.get("reference", {})
    st.caption(f"Canonical behavior · {scenario.get('criterion_id', reference.get('id', 'unavailable'))}")
    if scenario.get("canonical_status") == "unavailable":
        st.warning("Canonical Given/When/Then details are unavailable in the captured source.")
    else:
        for field in ("given", "when", "then"):
            if field in scenario:
                st.markdown(f"**{field.title()}**")
                values = scenario[field] if isinstance(scenario[field], list) else [scenario[field]]
                for value in values:
                    st.write(value)

    st.markdown("#### Related tasks")
    if not related["tasks"]:
        st.info("No task-to-scenario mapping is recorded for this scenario.")
    for task in related["tasks"]:
        task_id = str(task.get("id", ""))
        via = next((link.get("via") for link in task.get("related_scenarios", [])
                    if str(link.get("id")) == str(scenario_id)), "recorded mapping")
        with st.container(horizontal=True, vertical_alignment="center"):
            st.write(task.get("title") or task_id)
            st.caption(f"{task.get('status', 'not recorded')} · {via}")
            if on_open:
                st.button("Open task", key=f"scenario:{scenario_id}:task:{task_id}",
                          on_click=on_open, args=("task", task_id))

    st.markdown("#### Verifying tests")
    if not related["tests"]:
        st.info("No verifying test is linked to this scenario.")
    for test in related["tests"]:
        test_id = str(test.get("id", ""))
        with st.container(horizontal=True, vertical_alignment="center"):
            st.write(test.get("title") or test_id)
            st.caption(f"{test.get('type', 'test')} · {test_id}")
            if on_open:
                st.button("Open test", key=f"scenario:{scenario_id}:test:{test_id}",
                          on_click=on_open, args=("test", test_id))
