"""Session context for stable work selection and guarded form identity."""
from __future__ import annotations


STATE_ROUTE = "_engineering_route"
STATE_ROUTE_HISTORY = "_engineering_route_history"
STATE_FORM_IDENTITY = "_engineering_form_identity"
STATE_SOURCE = "_engineering_source_context"
STATE_SOURCE_SELECTION = "_engineering_source_selection"
STATE_COMMITTED_SOURCE_CACHE = "_engineering_committed_source_cache"


def identity_for(view: dict, work_id: str, source: str = "working-tree") -> dict | None:
    """Capture the exact admitted edit authority once for the selected source."""
    snapshot = view.get("snapshot") if isinstance(view, dict) else None
    if not isinstance(snapshot, dict):
        return None
    return {"work_id": work_id, "digest": snapshot.get("digest"),
            "editable": bool(view.get("editable"))}


def reset_for_work(session, work_id: str, view: dict, epic_id: str,
                   source: str = "working-tree", source_context: dict | None = None) -> None:
    """Reset selections and caches when the displayed work/source changes."""
    session[STATE_ROUTE] = epic_id
    session[STATE_ROUTE_HISTORY] = []
    session[STATE_FORM_IDENTITY] = identity_for(view, work_id, source)
    session[STATE_SOURCE] = {"kind": source, "work_id": work_id,
                             **(source_context or {})}
    for key in ("_engineering_candidate_projection", "_engineering_evidence_projection",
                "_engineering_overview_results", "_engineering_feedback"):
        session[key] = None if key != "_engineering_feedback" else []
    for key in ("option_id", "actor", "rationale"):
        session.pop(key, None)


def navigate(session, target: str) -> None:
    """Push the current node before opening another canonical route."""
    current = session.get(STATE_ROUTE)
    if current and current != target:
        history = list(session.get(STATE_ROUTE_HISTORY, []))
        history.append(current)
        session[STATE_ROUTE_HISTORY] = history
    session[STATE_ROUTE] = target


def back(session, fallback: str) -> None:
    history = list(session.get(STATE_ROUTE_HISTORY, []))
    session[STATE_ROUTE] = history.pop() if history else fallback
    session[STATE_ROUTE_HISTORY] = history


def route_to(session, target: str) -> None:
    session[STATE_ROUTE] = target
    session[STATE_ROUTE_HISTORY] = []
