"""Recorded story details; never synthesize missing story records."""
from __future__ import annotations

import streamlit as st


def story_summaries(projection: dict) -> list[dict]:
    scenarios = {str(item.get("id")): item for item in projection.get("scenarios", [])}
    return [{**story, "scenarios": [scenarios[str(identity)] for identity in story.get("scenario_ids", [])
                                    if str(identity) in scenarios]}
            for story in projection.get("workbench", {}).get("stories", [])]


def render_story(projection: dict, story_id: str, *, on_open=None) -> None:
    story = next((item for item in story_summaries(projection)
                  if str(item.get("id")) == str(story_id)), None)
    if story is None:
        st.warning("This story is not present in the captured workstream.")
        return
    st.subheader(story.get("title") or story.get("id"))
    model_node = next((node for node in projection.get("model", {}).get("nodes", [])
                       if str(node.get("id")) == str(story_id)
                       and node.get("type") == "story"), {})
    st.caption("Recorded Story in the Engineering Model")
    if model_node.get("description"):
        st.markdown("#### Outcome")
        st.write(model_node["description"])
    st.markdown("#### Related scenarios")
    if not story["scenarios"]:
        st.info("No scenarios are recorded under this story.")
    for scenario in story["scenarios"]:
        scenario_id = str(scenario.get("id", ""))
        with st.container(horizontal=True, vertical_alignment="center"):
            st.write(scenario.get("title") or scenario_id)
            st.caption(scenario_id)
            if on_open:
                st.button("Open scenario", key=f"story:{story_id}:scenario:{scenario_id}",
                          on_click=on_open, args=("scenario", scenario_id))
