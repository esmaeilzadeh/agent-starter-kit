"""Task list and detail panel for the connected Engineering Workbench."""
from __future__ import annotations

import streamlit as st


def task_rows(projection: dict) -> list[dict]:
    """Return stable, display-ready task rows without inventing completion."""
    workbench = projection.get("workbench", {})
    projected = {str(item.get("id")): item for item in workbench.get("tasks", [])}
    states = {str(item.get("id")): item for item in projection.get("tasks", [])}
    nodes = {str(item.get("id")): item for item in projection.get("model", {}).get("nodes", [])}
    rows = []
    for identity, item in projected.items():
        product_node_id = str(item.get("product_node_id", identity))
        state = states.get(product_node_id, states.get(identity, {}))
        node = nodes.get(identity, {})
        if not node:
            node = nodes.get(product_node_id, {})
        status = item.get("status", state.get("status", "not recorded"))
        story_nodes = {str(candidate.get("id")): candidate for candidate in nodes.values()
                       if candidate.get("type") == "story"}
        rows.append({
            **item,
            "id": identity,
            "title": item.get("title") or node.get("title") or identity,
            "purpose": item.get("outcome") or node.get("description") or "",
            "lifecycle": item.get("lifecycle", node.get("lifecycle", "not recorded")),
            "status": status,
            "runtime_status": item.get("runtime_status", state.get("runtime_status")),
            "blockers": state.get("blockers", item.get("blockers", [])),
            "result_path": item.get("result_path") or state.get("result_path"),
            "verified": False,
            "result_reference_recorded": bool(item.get("result_path") or state.get("result_path")),
            "context": state.get("context", {}),
            "product_node_id": product_node_id,
            "related_stories": [
                {**link, "title": story_nodes.get(str(link.get("id")), {}).get("title", link.get("id")),
                 "purpose": story_nodes.get(str(link.get("id")), {}).get("description", "")}
                for link in item.get("related_stories", [])
            ],
        })
    return sorted(rows, key=lambda row: row["id"])


def _detail(row: dict, *, on_open=None, context: str = "tasks") -> None:
    st.markdown(f"### {row['title']}")
    st.caption(f"{row['id']} · lifecycle: {row.get('lifecycle', 'not recorded')}")
    st.markdown("**Task status**")
    st.write(str(row.get("status", "not recorded")).replace("_", " ").title())
    runtime = row.get("runtime_status")
    st.caption("Runtime record: " + (str(runtime) if runtime else "not recorded"))
    st.caption("Completion is not verified by this task view.")
    if row.get("result_reference_recorded"):
        st.info("A task result reference is recorded; this view does not verify its contents.")
    else:
        st.info("Lifecycle status is separate from result evidence; no result reference is recorded for this task.")
    if row.get("outcome"):
        st.markdown("**Purpose and outcome**")
        st.write(row["outcome"])
    elif row.get("purpose"):
        st.markdown("**Purpose**")
        st.write(row["purpose"])

    product = row.get("product_identity")
    execution = row.get("execution_identity")
    if isinstance(product, dict) or isinstance(execution, dict):
        product_label = (f"{product.get('work_id', 'unavailable')}:{product.get('node_id', 'unavailable')}"
                         if isinstance(product, dict) else "not recorded")
        execution_label = (f"{execution.get('work_id', 'unavailable')}:{execution.get('task_id', 'unavailable')}"
                           if isinstance(execution, dict) else "not recorded")
        st.caption("Task record: " + str(row.get("record_source", "recorded")) +
                   f" · product Task {product_label} · execution owner {execution_label}")

    st.markdown("#### Specification and plan context")
    context = row.get("context") if isinstance(row.get("context"), dict) else {}
    if not any(context.values()):
        st.info("No specification or plan passage is recorded for this Task.")
    for role in ("spec", "plan"):
        passages = context.get(role, [])
        if not passages:
            st.caption(f"No {role} passage is recorded.")
        for passage in passages:
            st.markdown(f"**{role.title()} passage · {passage.get('state', 'unavailable')}**")
            st.caption(str(passage.get("path", "Path not recorded")))
            if passage.get("text"):
                st.text(passage["text"])
            elif passage.get("message"):
                st.info(str(passage["message"]))

    st.markdown("#### Dependencies")
    dependencies = row.get("dependencies") or []
    if not dependencies:
        st.caption("No Task dependencies are recorded.")
    for identity in dependencies:
        st.write(str(identity))

    blockers = row.get("blockers") or []
    st.markdown("#### Blockers")
    if not blockers:
        st.caption("No blockers are recorded.")
    for blocker in blockers:
        st.warning(f"{blocker.get('id', 'unknown')} · {blocker.get('reason', 'Reason not recorded.')}")

    scenarios = row.get("related_scenarios") or []
    st.markdown("#### Related scenarios")
    if not scenarios:
        st.caption("No task-to-scenario mapping is recorded.")
    for link in scenarios:
        identity = str(link.get("id", ""))
        with st.container(horizontal=True, vertical_alignment="center"):
            st.write(identity)
            st.caption(str(link.get("via", "recorded mapping")))
            if on_open and identity:
                st.button("Open scenario", key=f"{context}:scenario:{row['id']}:{identity}",
                          on_click=on_open, args=("scenario", identity))

    stories = row.get("related_stories") or []
    st.markdown("#### Related Stories")
    if not stories:
        st.caption("No Task-to-Story relationship is recorded.")
    for story in stories:
        identity = str(story.get("id", ""))
        with st.container(horizontal=True, vertical_alignment="center"):
            st.write(story.get("title") or identity)
            if story.get("purpose"):
                st.caption(story["purpose"])
            if on_open and identity:
                st.button("Open Story", key=f"{context}:story:{row['id']}:{identity}",
                          on_click=on_open, args=("story", identity))

    test_ids = row.get("owned_test_ids") or []
    st.markdown("#### Related tests")
    if not test_ids:
        st.caption("No task-test ownership is recorded.")
    for identity in test_ids:
        with st.container(horizontal=True, vertical_alignment="center"):
            st.write(str(identity))
            if on_open:
                st.button("Open test", key=f"{context}:test:{row['id']}:{identity}",
                          on_click=on_open, args=("test", str(identity)))

    st.markdown("#### Implementation evidence")
    paths = row.get("owned_paths") or []
    if row.get("result_path"):
        st.caption(f"Recorded result: {row['result_path']}")
    if paths:
        st.markdown("**Owned paths**")
        st.dataframe([{"Path": path} for path in paths], hide_index=True,
                     width="stretch")
    else:
        st.caption("No implementation paths are recorded.")


def render_tasks(projection: dict, *, context: str = "tasks", on_open=None,
                 selected_id: str | None = None) -> None:
    """Render filterable task rows and a complete selected-task detail panel."""
    rows = task_rows(projection)
    st.subheader("Tasks")
    if not rows:
        st.info("No task records are available in this snapshot.")
        return
    statuses = ["All"] + sorted({str(row.get("status", "not recorded")) for row in rows})
    selected_status = st.selectbox("Status filter", statuses, key=f"tasks:status:{context}")
    query = st.text_input("Search tasks", key=f"tasks:search:{context}", placeholder="ID, title, or outcome")
    filtered = [row for row in rows
                if (selected_status == "All" or row.get("status") == selected_status)
                and (not query.strip() or query.casefold() in " ".join(
                    str(row.get(field, "")) for field in ("id", "title", "outcome")).casefold())]
    table = [{"ID": row["id"], "Task": row["title"],
              "Status": str(row.get("status", "not recorded")).replace("_", " "),
              "Lifecycle": row.get("lifecycle", "not recorded"),
              "Result reference": "Recorded" if row.get("result_reference_recorded") else "Unavailable"}
             for row in filtered]
    st.dataframe(table, hide_index=True, width="stretch")
    if not filtered:
        st.info("No tasks match the current filters.")
        return
    options = [row["id"] for row in filtered]
    labels = {row["id"]: f"{row['id']} · {row['title']} · {row.get('status', 'not recorded')}"
              for row in filtered}
    selection_key = f"tasks:selected:{context}"
    if st.session_state.get(selection_key) not in options:
        st.session_state[selection_key] = selected_id if selected_id in options else options[0]
    selected_task_id = st.selectbox("Selected task", options,
                                    format_func=lambda identity: labels[identity],
                                    key=selection_key)
    selected = next(row for row in filtered if row["id"] == selected_task_id)
    with st.container(border=True):
        _detail(selected, on_open=on_open, context=context)
