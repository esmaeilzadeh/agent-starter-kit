"""Native filesystem observation, with periodic freshness fallback."""
from pathlib import Path

from .admission import admit, load_published


def observe_once(root, work_id):
    snapshot, diagnostics = admit(root, work_id)
    published = snapshot
    if diagnostics:
        try:
            published = load_published(root, work_id)
        except (OSError, ValueError, KeyError, TypeError):
            published = None
    return {"schema": "ask-engineering-observation/v1", "work_id": work_id,
            "valid": not diagnostics, "diagnostics": diagnostics,
            "snapshot": published.identity if published is not None else None,
            "current_input": snapshot.identity if snapshot is not None else None,
            "last_validated": bool(diagnostics and published is not None)}


def updates(root, work_id, *, once=False, stop_event=None):
    """Validate after filesystem changes; missed events get a full fallback check.

    No cached validation or UI business rule is involved. The optional Rust-backed
    watchfiles package is needed only for continuous native observation.
    """
    root = Path(root).resolve()
    initial = observe_once(root, work_id)
    yield initial
    if once:
        return
    try:
        from watchfiles import DefaultFilter, watch
    except ImportError as exc:
        raise RuntimeError("continuous observation requires the optional watchfiles package") from exc
    state = root / "work" / work_id / "traceability" / "model-state"
    default = DefaultFilter(ignore_paths=[state])
    relevant = {str(root / item["path"]) for item in (initial.get("current_input") or {}).get("inputs", [])}
    model = str(root / "work" / work_id / "engineering-model.json")
    def selected(change, path):
        return default(change, path) and (path == model or path in relevant or
                                          Path(path).is_relative_to(root / "specs/current"))
    previous = initial
    # Timeouts cover subscription startup gaps and missed filesystem events.
    for _events in watch(root, watch_filter=selected, stop_event=stop_event,
                         yield_on_timeout=True, rust_timeout=500, debounce=50, step=20):
        result = observe_once(root, work_id)
        relevant = {str(root / item["path"]) for item in (result.get("current_input") or {}).get("inputs", [])}
        if result != previous:
            yield result
            previous = result
