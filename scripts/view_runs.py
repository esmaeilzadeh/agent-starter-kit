#!/usr/bin/env python3
"""Streamlit viewer for results/RUN_REGISTRY.md and per-run config + SHA."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parents[1]
REG = REPO / "results" / "RUN_REGISTRY.md"


def _rows() -> list[dict]:
    if not REG.is_file():
        return []
    out = []
    for line in REG.read_text().splitlines():
        if not line.startswith("| ") or line.startswith("| run-id") or line.startswith("| ---"):
            continue
        parts = [c.strip().strip("`") for c in line.strip("|").split("|")]
        if len(parts) < 4:
            continue
        run_id, metric, sha, path = parts[0], parts[1], parts[2], parts[3]
        if run_id in {"run-id", "---"}:
            continue
        cfg = {}
        cfg_path = REPO / path / "config.yaml" if not path.startswith("/") else Path(path) / "config.yaml"
        if not cfg_path.is_file():
            cfg_path = REPO / "results" / run_id / "config.yaml"
        if cfg_path.is_file():
            try:
                import yaml

                cfg = yaml.safe_load(cfg_path.read_text()) or {}
            except Exception:
                cfg = {"_raw": cfg_path.read_text()}
        summary = {}
        sm = cfg_path.parent / "summary.json"
        if sm.is_file():
            try:
                summary = json.loads(sm.read_text())
            except json.JSONDecodeError:
                summary = {}
        out.append(
            {
                "run-id": run_id,
                "metric": metric,
                "git_sha": sha,
                "path": path,
                "config": cfg,
                "summary": summary,
            }
        )
    return out


st.set_page_config(page_title="Experiment runs", layout="wide")
st.title("SHA-bound experiment runs")
st.caption("Cite path + git_sha + metric. Config lives in each run directory.")
rows = _rows()
if not rows:
    st.info("No registry rows yet. Commit a `results/<run-id>/config.yaml`, train, then `./ask record-run`.")
else:
    st.dataframe(
        [{k: r[k] for k in ("run-id", "metric", "git_sha", "path")} for r in rows],
        use_container_width=True,
        hide_index=True,
    )
    choice = st.selectbox("Inspect run", [r["run-id"] for r in rows])
    picked = next(r for r in rows if r["run-id"] == choice)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("config.yaml")
        st.json(picked["config"])
    with c2:
        st.subheader("summary")
        st.json(picked["summary"])
