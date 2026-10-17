"""Epic-root purpose, delivery summary and contextual attention."""
from __future__ import annotations

import streamlit as st
from workbench_navigation import build_outline


def summary_records(projection: dict, *, failed_result_ids: list[str] | None = None) -> dict[str, list[str] | None]:
    """Build stable-ID filters from captured projection data only."""
    workbench = projection.get("workbench", {})
    tasks = workbench.get("tasks", [])
    attention = projection.get("attention", [])
    counts = {}
    for task in tasks:
        identity = str(task.get("id", ""))
        counts[identity] = counts.get(identity, 0) + 1
    task_ids = {task_selection_id(task, counts[str(task.get("id", ""))] > 1): task
                for task in tasks}
    blocked = {identity for identity, task in task_ids.items() if task.get("status") == "blocked"}
    for item in attention:
        if item.get("type") == "task":
            product_id = str(item.get("id", ""))
            matched_product = False
            for identity, task in task_ids.items():
                product_identity = task.get("product_identity")
                product_node_id = (product_identity.get("node_id")
                                   if isinstance(product_identity, dict)
                                   else task.get("product_node_id"))
                if product_node_id and product_id == str(product_node_id):
                    blocked.add(identity)
                    matched_product = True
            # Legacy v1 task attention IDs already name the rendered task row.
            if not matched_product:
                blocked.update(identity for identity, task in task_ids.items()
                               if not isinstance(task.get("product_identity"), dict)
                               and str(task.get("id", "")) == product_id)
    return {
        "scenarios": sorted(str(item.get("id")) for item in projection.get("scenarios", [])),
        "tasks": sorted(task_ids),
        "blocked": sorted(blocked),
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
    feature = next((node for node in nodes.values() if node.get("type") == "feature"), None)
    purpose = epic or feature
    stories = projection.get("workbench", {}).get("stories", [])
    scenarios = projection.get("scenarios", [])
    tasks = projection.get("workbench", {}).get("tasks", [])

    st.subheader((purpose or {}).get("title") or "Workstream")
    st.caption("Choose a Story or Task from the outline, or follow a recorded Scenario to its delivery work.")
    if epic is None:
        st.caption("No recorded Epic")
    st.caption("Purpose")
    if purpose is None:
        st.info("No purpose record is available in this workstream.")
    elif purpose.get("description"):
        st.write(purpose["description"])
    else:
        st.write(purpose.get("title") or "Purpose is not recorded.")

    _render_flow(projection, on_open)
    _render_delivery(stories, scenarios, on_open)
    model_tasks = {str(node.get("id")): node for node in model.get("nodes", [])
                   if node.get("type") == "task"}
    _render_progress(tasks, projection.get("tasks", []), model_tasks)
    _render_attention(projection.get("attention", []), nodes, on_open)
    _render_summaries(projection, work_id, on_filter=on_filter,
                      failed_result_ids=failed_result_ids)
    if active_filter and active_filter.get("work_id") == work_id:
        _render_filter(projection, active_filter, on_open=on_open, on_clear=on_clear)


def _render_flow(projection: dict, on_open) -> None:
    """Show the actual recorded hierarchy as a connected, navigable flow."""
    st.markdown("#### End-to-end delivery path")
    st.caption("Follow each recorded link from purpose through delivery and verification.")
    entries = build_outline(projection)["entries"]
    visible = [entry for entry in entries if entry.get("kind") != "decision"]
    if not visible:
        st.info("No connected delivery records are available yet.")
        return
    for entry in visible:
        kind = str(entry.get("kind", "record"))
        label = str(entry.get("label") or entry.get("node_id") or kind.title())
        indent = int(entry.get("indent", 0))
        if kind == "group":
            st.caption(label)
            continue
        prefix = "　" * min(indent, 8) + ("↳ " if indent else "● ")
        display = f"{prefix}{kind.title()}  ·  {label}"
        if on_open:
            st.button(display, key=f"delivery-flow:route:{entry['route_id']}",
                      type="tertiary", width="stretch", on_click=on_open,
                      args=(kind, str(entry.get("selection_id", entry.get("node_id", "")))))
        else:
            st.write(display)


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
    task_items = projection.get("workbench", {}).get("tasks", [])
    counts = {}
    for task in task_items:
        identity = str(task.get("id", ""))
        counts[identity] = counts.get(identity, 0) + 1
    tasks = {task_selection_id(item, counts[str(item.get("id", ""))] > 1): item
             for item in task_items}
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
                open_identity = task_selection_id(item, counts[str(item.get("id", ""))] > 1) if kind in {"tasks", "blocked"} else identity
                st.button("Open record", key=f"overview:filter:open:{kind}:{identity}",
                          on_click=on_open, args=(kind, open_identity))
