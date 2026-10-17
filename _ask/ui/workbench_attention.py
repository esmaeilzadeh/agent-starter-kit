"""Contextual attention records for blockers, decisions, and evidence gaps."""
from __future__ import annotations

import streamlit as st


def attention_rows(projection: dict) -> list[dict]:
    """Normalize projection attention while retaining originating identities."""
    nodes = {str(item.get("id")): item for item in projection.get("model", {}).get("nodes", [])}
    rows = []
    for item in projection.get("attention", []):
        identity = str(item.get("id", ""))
        node = nodes.get(identity, {})
        rows.append({
            **item,
            "id": identity,
            "type": item.get("type", node.get("type", "record")),
            "title": item.get("title") or node.get("title") or identity,
            "reason": item.get("reason") or "Reason not recorded.",
            "options": node.get("options", []),
            "dependents": item.get("dependents", []),
        })
    return sorted(rows, key=lambda row: (str(row.get("type")), row["id"]))


def render_attention(projection: dict, *, context: str = "attention", on_open=None) -> None:
    """Render a selectable attention list and complete selected-record context."""
    rows = attention_rows(projection)
    st.subheader("Needs attention")
    if not rows:
        st.info("No blockers, open decisions, or evidence gaps are recorded.")
        return
    table = [{"ID": row["id"], "Type": row["type"], "Record": row["title"],
              "Reason": row["reason"]} for row in rows]
    st.dataframe(table, hide_index=True, width="stretch")
    ids = [row["id"] for row in rows]
    labels = {row["id"]: f"{row['type']} · {row['title']}" for row in rows}
    selected_id = st.selectbox("Selected attention record", ids,
                               format_func=lambda identity: labels[identity],
                               key=f"attention:selected:{context}")
    selected = next(row for row in rows if row["id"] == selected_id)
    with st.container(border=True):
        st.markdown(f"### {selected['title']}")
        st.caption(f"{selected['type']} · {selected['id']}")
        st.markdown("**Why it needs attention**")
        st.write(selected["reason"])
        if selected.get("options"):
            st.markdown("#### Declared options")
            st.table([{"ID": option.get("id", ""),
                       "Label": option.get("label", option.get("title", "")),
                       "Description": option.get("description", "")}
                      for option in selected["options"]])
        if selected.get("dependents"):
            st.markdown("#### Dependents")
            st.write(", ".join(str(item) for item in selected["dependents"]))
        if on_open:
            st.button("Open originating record", key=f"attention:open:{context}:{selected['id']}",
                      on_click=on_open, args=(selected["type"], selected["id"]))
