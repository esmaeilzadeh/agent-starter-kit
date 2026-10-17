"""Task list and detail panel for the connected Engineering Workbench."""
from __future__ import annotations

import html
import re

import streamlit as st
from workbench_context import task_selection_id


_TABLE_SEPARATOR = re.compile(r"^:?-{3,}:?$")
_LINE_BREAK = re.compile(r"<br\s*/?>", re.IGNORECASE)
_CODE_SPAN = re.compile(r"`([^`]+)`")


def _table_cells(line: str) -> list[str]:
    """Split a Markdown table row while preserving escaped literal pipes."""
    value = line.strip()
    if value.startswith("|"):
        value = value[1:]
    if value.endswith("|"):
        value = value[:-1]
    if "|" not in value:
        return []
    cells = re.split(r"(?<!\\)\|", value)
    return [cell.strip().replace(r"\|", "|") for cell in cells]


def _table_markup(headers: list[str], rows: list[dict[str, str]]) -> str:
    """Build a safe, responsive HTML table from parsed Markdown cell text."""
    def cell_markup(value: str) -> str:
        chunks = []
        cursor = 0
        for match in _CODE_SPAN.finditer(value):
            chunks.append(html.escape(value[cursor:match.start()]).replace("\n", "<br>"))
            chunks.append(f"<code>{html.escape(match.group(1))}</code>")
            cursor = match.end()
        chunks.append(html.escape(value[cursor:]).replace("\n", "<br>"))
        return "".join(chunks)

    header_html = "".join(f"<th>{cell_markup(header)}</th>" for header in headers)
    row_html = "".join(
        "<tr>" + "".join(f"<td>{cell_markup(row.get(header, ''))}</td>" for header in headers) + "</tr>"
        for row in rows
    )
    return (
        '<div style="max-width:100%;overflow-x:auto">'
        '<table class="ask-passage-table" style="width:100%;table-layout:fixed;border-collapse:collapse">'
        '<thead><tr>' + header_html + '</tr></thead><tbody>' + row_html + '</tbody></table></div>'
        '<style>'
        '.ask-passage-table th,.ask-passage-table td{border:1px solid #d9e2e8;padding:.45rem;'
        'text-align:left;vertical-align:top;overflow-wrap:anywhere;white-space:normal}'
        '.ask-passage-table th{background:#f2f6f8;font-weight:600}'
        '.ask-passage-table code{white-space:normal;overflow-wrap:anywhere}'
        '</style>'
    )


def _render_markdown_passage(value: str) -> None:
    """Render prose as Markdown and pipe tables as scrollable workbench tables."""
    lines = value.splitlines()
    cursor = 0
    prose_start = 0
    while cursor + 1 < len(lines):
        headers = _table_cells(lines[cursor])
        separators = _table_cells(lines[cursor + 1])
        if (not headers or len(headers) != len(separators)
                or not all(_TABLE_SEPARATOR.fullmatch(cell.replace(" ", ""))
                           for cell in separators)):
            cursor += 1
            continue

        prose = "\n".join(lines[prose_start:cursor]).strip()
        if prose:
            st.markdown(prose)
        rows = []
        row_index = cursor + 2
        while row_index < len(lines):
            cells = _table_cells(lines[row_index])
            if len(cells) != len(headers):
                break
            rows.append({header: _LINE_BREAK.sub("\n", cell) for header, cell in zip(headers, cells)})
            row_index += 1
        if rows:
            st.markdown(_table_markup(headers, rows), unsafe_allow_html=True)
            cursor = row_index
            prose_start = row_index
        else:
            cursor += 2
            prose_start = cursor

    trailing = "\n".join(lines[prose_start:]).strip()
    if trailing:
        st.markdown(trailing)


def task_rows(projection: dict) -> list[dict]:
    """Return stable, display-ready task rows without inventing completion."""
    workbench = projection.get("workbench", {})
    projected = [item for item in workbench.get("tasks", []) if isinstance(item, dict)]
    states = {str(item.get("id")): item for item in projection.get("tasks", [])}
    nodes = {str(item.get("id")): item for item in projection.get("model", {}).get("nodes", [])}
    decisions = {identity: node for identity, node in nodes.items()
                 if node.get("type") == "decision"}
    is_v2 = projection.get("model", {}).get("schema") == "ask-engineering-model/v2"
    id_counts = {}
    for item in projected:
        identity = str(item.get("id"))
        id_counts[identity] = id_counts.get(identity, 0) + 1
    rows = []
    for item in projected:
        identity = str(item.get("id"))
        product_identity = item.get("product_identity")
        product_node_id = (product_identity.get("node_id")
                           if isinstance(product_identity, dict) else
                           item.get("product_node_id") if is_v2 else identity)
        if is_v2:
            state = states.get(str(product_node_id), {}) if product_node_id else {}
            node = nodes.get(str(product_node_id), {}) if product_node_id else {}
        else:
            state = states.get(identity, {})
            node = nodes.get(identity, {})
        status = item.get("status", state.get("status", "not recorded"))
        story_nodes = {str(candidate.get("id")): candidate for candidate in nodes.values()
                       if candidate.get("type") == "story"}
        execution_identity = item.get("execution_identity")
        selection_id = task_selection_id(item, id_counts[identity] > 1)
        blockers = []
        raw_blockers = state.get("blockers") or item.get("blockers") or item.get("readiness_blockers", [])
        for blocker in raw_blockers:
            if not isinstance(blocker, dict):
                continue
            decision = decisions.get(str(blocker.get("id")), {})
            blockers.append({**blocker,
                             "title": decision.get("title") or blocker.get("id"),
                             "options": decision.get("options", []),
                             "history": decision.get("history", []),
                             "resolution": decision.get("resolution", {})})
        rows.append({
            **item,
            "id": identity,
            "selection_id": selection_id,
            "title": item.get("title") or node.get("title") or identity,
            "purpose": item.get("outcome") or node.get("description") or "",
            "lifecycle": item.get("lifecycle", node.get("lifecycle", "not recorded")),
            "status": status,
            "runtime_status": item.get("runtime_status", state.get("runtime_status")),
            "blockers": blockers,
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
        for passage_index, passage in enumerate(passages):
            st.markdown(f"**{role.title()} passage · {passage.get('state', 'unavailable')}**")
            st.caption(f"{passage.get('path', 'Path not recorded')} · revision {passage.get('revision', 'not recorded')} · selector {passage.get('selector', 'not recorded')}")
            if passage.get("text"):
                _render_markdown_passage(passage["text"])
                if passage.get("surrounding_text"):
                    with st.expander(f"Show surrounding {role} text · {passage.get('path', '')}",
                                     expanded=False,
                                     key=f"{context}:passage:{row['selection_id']}:{role}:{passage_index}"):
                        _render_markdown_passage(passage["surrounding_text"])
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
        st.warning(f"{blocker.get('title') or blocker.get('id', 'unknown')} · "
                   f"{blocker.get('reason', 'Reason not recorded.')}")
        if blocker.get("options"):
            st.caption("Available choices: " + "; ".join(
                f"{option.get('label', option.get('id', ''))} ({option.get('id', '')})"
                for option in blocker["options"] if isinstance(option, dict)))
        history = blocker.get("history") or []
        if history:
            latest = history[-1]
            if isinstance(latest, dict):
                st.caption("Last decision update by " + str(latest.get("actor") or "unavailable"))
                if latest.get("rationale"):
                    st.write("Decision rationale: " + str(latest["rationale"]))
        resolution = blocker.get("resolution")
        if isinstance(resolution, dict) and resolution:
            option_id = resolution.get("option_id")
            st.caption("Resolved option: " + str(option_id or "unavailable") +
                       " · actor: " + str(resolution.get("actor") or "unavailable"))
            if resolution.get("rationale"):
                st.write("Resolution rationale: " + str(resolution["rationale"]))

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
    options = [row["selection_id"] for row in filtered]
    rows_by_selection = {row["selection_id"]: row for row in filtered}
    labels = {row["selection_id"]: f"{row['id']} · {row['title']} · {row.get('status', 'not recorded')}"
              for row in filtered}
    selection_key = f"tasks:selected:{context}"
    if st.session_state.get(selection_key) not in options:
        st.session_state[selection_key] = selected_id if selected_id in options else options[0]
    selected_task_id = st.selectbox("Selected task", options,
                                    format_func=lambda identity: labels[identity],
                                    key=selection_key)
    selected = rows_by_selection[selected_task_id]
    with st.container(border=True):
        _detail(selected, on_open=on_open, context=context)
