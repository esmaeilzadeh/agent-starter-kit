"""Epic-root purpose, delivery summary and contextual attention."""
from __future__ import annotations

import streamlit as st


def summary_records(projection: dict, *, failed_result_ids: list[str] | None = None) -> dict[str, list[str] | None]:
    """Build stable-ID filters from captured projection data only."""
    workbench = projection.get("workbench", {})
    tasks = workbench.get("tasks", [])
    attention = projection.get("attention", [])
    return {
        "scenarios": sorted(str(item.get("id")) for item in projection.get("scenarios", [])),
        "tasks": sorted(str(item.get("id")) for item in tasks),
        "blocked": sorted({str(item.get("id")) for item in attention if item.get("type") == "task"}
                           | {str(item.get("id")) for item in tasks if item.get("status") == "blocked"}),
        "decisions": sorted(str(item.get("id")) for item in attention
                             if item.get("type") == "decision" and item.get("status") == "open"),
        # Results have their own explicit load flow; unknown is never zero.
        "failed-results": None if failed_result_ids is None else sorted(set(failed_result_ids)),
    }


def render_overview(projection: dict, *, work_id: str, on_filter=None,
                    on_open=None, on_clear=None, active_filter: dict | None = None,
                    failed_result_ids: list[str] | None = None) -> None:
    """Render the epic root without reading test source or evaluating evidence."""
    model = projection.get("model", {})
    nodes = {node.get("id"): node for node in model.get("nodes", [])}
    epic = next((node for node in nodes.values() if node.get("type") == "intent"), None)
    epic = epic or next((node for node in nodes.values() if node.get("type") == "feature"), None)
    stories = projection.get("workbench", {}).get("stories", [])
    scenarios = projection.get("scenarios", [])
    tasks = projection.get("workbench", {}).get("tasks", [])

    st.subheader((epic or {}).get("title") or "Epic")
    st.caption("Purpose")
    if epic is None:
        st.info("No epic or purpose record is available in this workstream.")
    elif epic.get("description"):
        st.write(epic["description"])
    else:
        st.write(epic.get("title") or "Purpose is not recorded.")

    _render_delivery(stories, scenarios, on_open)
    model_tasks = {str(node.get("id")): node for node in model.get("nodes", [])
                   if node.get("type") == "task"}
    _render_progress(tasks, projection.get("tasks", []), model_tasks)
    _render_attention(projection.get("attention", []), nodes, on_open)
    _render_summaries(projection, work_id, on_filter=on_filter,
                      failed_result_ids=failed_result_ids)
    if active_filter and active_filter.get("work_id") == work_id:
        _render_filter(projection, active_filter, on_open=on_open, on_clear=on_clear)


def _render_delivery(stories: list[dict], scenarios: list[dict], on_open) -> None:
    st.markdown("#### Stories and scenarios")
    scenarios_by_id = {str(item.get("id")): item for item in scenarios}
    if not stories:
        st.info("No story records are present. Existing scenarios are shown directly here; story membership is not inferred.")
        if scenarios:
            st.caption("Scenarios without a recorded story")
            for scenario in scenarios:
                _scenario_row(scenario, on_open)
        else:
            st.caption("No canonical scenarios are recorded.")
        return
    for story in stories:
        with st.container(border=True):
            story_id = str(story.get("id", ""))
            st.markdown(f"**{story.get('title') or story_id}**")
            linked = [scenarios_by_id[item] for item in story.get("scenario_ids", [])
                      if item in scenarios_by_id]
            if not linked:
                st.caption("No scenarios are recorded under this story.")
            for scenario in linked:
                _scenario_row(scenario, on_open)
    assigned_ids = {str(identity) for story in stories for identity in story.get("scenario_ids", [])}
    unassigned = [scenario for scenario in scenarios if str(scenario.get("id")) not in assigned_ids]
    if unassigned:
        st.caption("Scenarios without a recorded story")
        for scenario in unassigned:
            _scenario_row(scenario, on_open)


def _scenario_row(scenario: dict, on_open) -> None:
    scenario_id = str(scenario.get("id", ""))
    with st.container(horizontal=True, vertical_alignment="center"):
        st.write(scenario.get("title") or scenario_id)
        st.caption(f"{scenario_id} · {scenario.get('canonical_status', 'available')}")
        if on_open:
            st.button("Open scenario", key=f"overview:scenario:{scenario_id}",
                      on_click=on_open, args=("scenario", scenario_id))


def _render_progress(tasks: list[dict], readiness: list[dict], model_tasks: dict) -> None:
    st.markdown("#### Task progress")
    if not tasks:
        st.caption("No task records are available.")
        return
    runtime_statuses, lifecycles = {}, {}
    for task in tasks:
        status = str(task.get("status", "not recorded")).replace("_", " ")
        runtime_statuses[status] = runtime_statuses.get(status, 0) + 1
        lifecycle = model_tasks.get(str(task.get("id")), {}).get("lifecycle", "not recorded")
        lifecycles[lifecycle] = lifecycles.get(lifecycle, 0) + 1
    readiness_counts = {}
    for task in readiness:
        value = str(task.get("status", "not recorded")).replace("_", " ")
        readiness_counts[value] = readiness_counts.get(value, 0) + 1
    st.caption("Task graph / runner: " + " · ".join(
        f"{label.title()} {count}" for label, count in sorted(runtime_statuses.items())))
    st.caption("Declared lifecycle: " + " · ".join(
        f"{label.title()} {count}" for label, count in sorted(lifecycles.items())))
    if readiness_counts:
        st.caption("Dependency readiness: " + " · ".join(
            f"{label.title()} {count}" for label, count in sorted(readiness_counts.items())))


def _render_attention(items: list[dict], nodes: dict, on_open) -> None:
    st.markdown("#### Needs attention")
    if not items:
        st.caption("No recorded blockers, open decisions, or other attention items.")
        return
    for item in items:
        identity, kind = str(item.get("id", "")), str(item.get("type", "record"))
        label = item.get("title") or nodes.get(identity, {}).get("title") or identity
        reason = item.get("reason", "Reason not recorded.")
        with st.container(horizontal=True, vertical_alignment="center"):
            st.write(f"{kind.title()} · {label}")
            st.caption(str(reason))
            if on_open:
                st.button("Open", key=f"overview:attention:{kind}:{identity}",
                          on_click=on_open, args=(kind, identity))


def _render_summaries(projection: dict, work_id: str, *, on_filter,
                      failed_result_ids: list[str] | None) -> None:
    records = summary_records(projection, failed_result_ids=failed_result_ids)
    labels = [("scenarios", "Scenarios"), ("tasks", "Tasks"),
              ("blocked", "Blocked tasks"), ("decisions", "Open decisions")]
    with st.container(horizontal=True, vertical_alignment="top", gap="small"):
        for kind, label in labels:
            with st.container(border=True):
                st.metric(label, len(records[kind] or []))
                if on_filter:
                    st.button(f"View {label.lower()}", key=f"overview:summary:{kind}",
                              on_click=on_filter, args=(kind, records[kind] or [], work_id))
        with st.container(border=True):
            value = len(records["failed-results"] or []) if records["failed-results"] is not None else "Not loaded"
            st.metric("Failed results", value)
            if records["failed-results"] is None:
                st.caption("Results are not loaded. Open a result to inspect recorded executions.")
            elif on_filter:
                st.button("View failed results", key="overview:summary:failed-results",
                          on_click=on_filter, args=("failed-results", records["failed-results"] or [], work_id))


def _render_filter(projection: dict, active_filter: dict, *, on_open, on_clear) -> None:
    kind = active_filter.get("kind")
    ids = set(active_filter.get("ids", []))
    tasks = {str(item.get("id")): item for item in projection.get("workbench", {}).get("tasks", [])}
    scenarios = {str(item.get("id")): item for item in projection.get("scenarios", [])}
    decisions = {str(item.get("id")): item for item in projection.get("model", {}).get("nodes", [])
                 if item.get("type") == "decision"}
    st.markdown(f"#### {str(kind or 'Filtered records').replace('-', ' ').title()}")
    if on_clear:
        st.button("Clear filter", key="overview:filter:clear", on_click=on_clear)
    if not ids:
        st.info("No records match this summary.")
        return
    records = scenarios if kind == "scenarios" else decisions if kind == "decisions" else tasks
    for identity in sorted(ids):
        item = records.get(identity)
        if item is None:
            st.warning(f"The filtered record {identity} is not available in this captured workstream.")
            continue
        label = item.get("title") or identity
        status = item.get("status") or item.get("lifecycle") or "not recorded"
        with st.container(horizontal=True, vertical_alignment="center"):
            st.write(label)
            st.caption(f"{identity} · {str(status).replace('_', ' ')}")
            if on_open:
                st.button("Open record", key=f"overview:filter:open:{kind}:{identity}",
                          on_click=on_open, args=(kind, identity))
