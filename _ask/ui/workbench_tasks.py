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
        state = states.get(identity, {})
        node = nodes.get(identity, {})
        status = item.get("status", state.get("status", "not recorded"))
        rows.append({
            **item,
            "id": identity,
            "title": item.get("title") or node.get("title") or identity,
            "lifecycle": item.get("lifecycle", node.get("lifecycle", "not recorded")),
            "status": status,
            "runtime_status": item.get("runtime_status", state.get("runtime_status")),
            "blockers": state.get("blockers", item.get("blockers", [])),
            "result_path": item.get("result_path") or state.get("result_path"),
            "verified": bool(item.get("result_path") or state.get("result_path")) and status == "completed",
        })
    return sorted(rows, key=lambda row: row["id"])


def _detail(row: dict, *, on_open=None, context: str = "tasks") -> None:
    st.markdown(f"### {row['title']}")
    st.caption(f"{row['id']} · lifecycle: {row.get('lifecycle', 'not recorded')}")
    st.markdown("**Task status**")
    st.write(str(row.get("status", "not recorded")).replace("_", " ").title())
    runtime = row.get("runtime_status")
    st.caption("Runtime record: " + (str(runtime) if runtime else "not recorded"))
    if row.get("verified"):
        st.success("This task has a recorded completed result.")
    else:
        st.info("Lifecycle status is separate from verified completion; no completed result is attached to this task.")
    if row.get("outcome"):
        st.markdown("**Outcome**")
        st.write(row["outcome"])

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
        st.dataframe([{"Path": path} for path in paths], hide_index=True,
                     width="stretch")
    else:
        st.caption("No implementation paths are recorded.")


def render_tasks(projection: dict, *, context: str = "tasks", on_open=None) -> None:
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
              "Verified completion": "Yes" if row.get("verified") else "No"}
             for row in filtered]
    st.dataframe(table, hide_index=True, width="stretch")
    if not filtered:
        st.info("No tasks match the current filters.")
        return
    options = [row["id"] for row in filtered]
    labels = {row["id"]: f"{row['id']} · {row['title']} · {row.get('status', 'not recorded')}"
              for row in filtered}
    selected_id = st.selectbox("Selected task", options,
                               format_func=lambda identity: labels[identity],
                               key=f"tasks:selected:{context}")
    selected = next(row for row in filtered if row["id"] == selected_id)
    with st.container(border=True):
        _detail(selected, on_open=on_open, context=context)
