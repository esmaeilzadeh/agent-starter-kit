"""Collapsed, actionable technical provenance for the selected workbench item."""
from __future__ import annotations

import streamlit as st


def render_debug(*, work_id: str, snapshot_digest: str, candidate_sha: str | None = None,
                 source_path: str | None = None, context: str = "debug") -> None:
    details = st.expander("Technical details and identifiers", expanded=False,
                          on_change="rerun", key=f"debug:{context}")
    if not details.open:
        return
    with details:
        st.caption("The snapshot digest fingerprints admitted inputs; it is not a Git commit.")
        st.markdown("**Snapshot digest**")
        st.code(snapshot_digest or "unavailable")
        st.markdown("**Git revision**")
        st.code(candidate_sha or "unavailable")
        st.markdown("**Inspect commands**")
        commit = candidate_sha or "<commit-sha>"
        st.code(f"git show {commit}\n./ask model show --work-id {work_id} --candidate {commit}", language="bash")
        if source_path:
            st.caption(f"Selected source: `{source_path}`")
