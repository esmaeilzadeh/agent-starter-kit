"""Session context for stable work selection and guarded form identity."""
from __future__ import annotations


STATE_ROUTE = "_engineering_route"
STATE_ROUTE_HISTORY = "_engineering_route_history"
STATE_FORM_IDENTITY = "_engineering_form_identity"
STATE_SOURCE = "_engineering_source_context"
STATE_SOURCE_SELECTION = "_engineering_source_selection"
STATE_COMMITTED_SOURCE_CACHE = "_engineering_committed_source_cache"
STATE_SUBJECT_ENTRY = "_engineering_subject_entry"


def identity_for(view: dict, work_id: str, source: str = "working-tree") -> dict | None:
    """Capture the exact admitted edit authority once for the selected source."""
    snapshot = view.get("snapshot") if isinstance(view, dict) else None
    if not isinstance(snapshot, dict):
        return None
    return {"work_id": work_id, "digest": snapshot.get("digest"),
            "editable": bool(view.get("editable"))}


def task_selection_id(item: dict, duplicate: bool = False) -> str:
    """Return a stable selection key that preserves product/execution identity."""
    identity = str(item.get("id", ""))
    if not duplicate:
        return identity
    product = item.get("product_identity")
    if isinstance(product, dict):
        return f"product:{product.get('work_id', '')}:{product.get('node_id', identity)}"
    execution = item.get("execution_identity")
    if isinstance(execution, dict):
        return f"execution:{execution.get('work_id', '')}:{execution.get('task_id', identity)}"
    return identity


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
    # A refreshed/work-switched snapshot must re-evaluate selected source and evidence.
    session.pop("_engineering_selected_detail_cache", None)
    for key in ("option_id", "actor", "rationale"):
        session.pop(key, None)
    session[STATE_SUBJECT_ENTRY] = None


def resolve_subject_route(outline: dict, projection: dict, subject: str) -> tuple[str, list[str]] | None:
    """Resolve an explicit Story or Task URL to one admitted route and ancestry."""
    if not isinstance(subject, str) or ":" not in subject:
        return None
    kind, identity = subject.split(":", 1)
    if not identity or kind not in {"story", "task"}:
        return None
    entries = outline.get("entries", [])
    if kind == "story":
        matches = [entry for entry in entries
                   if entry.get("kind") == "story" and str(entry.get("node_id")) == identity]
    else:
        rows = projection.get("workbench", {}).get("tasks", [])
        id_counts = {}
        for row in rows:
            key = str(row.get("id", ""))
            id_counts[key] = id_counts.get(key, 0) + 1
        selected = []
        for row in rows:
            key = task_selection_id(row, id_counts.get(str(row.get("id", "")), 0) > 1)
            product = row.get("product_identity") or {}
            execution = row.get("execution_identity") or {}
            candidates = {key, str(row.get("id", ""))}
            candidates.add(str(row.get("product_node_id") or ""))
            if isinstance(product, dict):
                candidates.add(f"product:{product.get('work_id')}:{product.get('node_id')}")
            if isinstance(execution, dict):
                candidates.add(f"execution:{execution.get('work_id')}:{execution.get('task_id')}")
            if identity in candidates:
                selected.append((row, key))
        if len(selected) != 1:
            return None
        selected_key = selected[0][1]
        matches = [entry for entry in entries if entry.get("kind") == "task"
                   and entry.get("selection_id", entry.get("node_id")) == selected_key]
    if not matches:
        return None
    if kind == "task" and len({entry.get("selection_id", entry.get("node_id")) for entry in matches}) != 1:
        return None
    selected = min(matches, key=lambda entry: (len(entry.get("path", [])), entry["route_id"]))
    route_ids = [identity for identity, _ in selected.get("path", []) if identity]
    if route_ids and route_ids[-1] == selected["route_id"]:
        route_ids.pop()
    return selected["route_id"], route_ids


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
