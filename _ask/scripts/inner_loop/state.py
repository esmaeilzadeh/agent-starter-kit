from __future__ import annotations

import json
import os
import fcntl
import tempfile
from contextlib import contextmanager
from pathlib import Path


SCHEMA = "ask-inner-loop-state/v1"


class ProtocolViolation(RuntimeError):
    pass


class CasConflict(RuntimeError):
    pass


class SecondWriter(RuntimeError):
    pass


def state_path(root: Path, work_id: str) -> Path:
    return root / "work" / work_id / "inner-loop" / "state.json"


def _require_coordinator() -> None:
    role = os.environ.get("ASK_INNER_LOOP_ROLE", "coordinator")
    if role == "worker":
        raise ProtocolViolation("worker must not write state.json (protocol violation)")


def _require_reconciled(root: Path, work_id: str, state: dict | None,
                        task_ids: list[str] | None = None) -> None:
    """Apply the recovery guard at every state mutation boundary."""
    from inner_loop.graph import load_graph
    from inner_loop.recovery import require_safe

    graph_path = root / "work" / work_id / "inner-loop" / "tasks.yaml"
    if graph_path.is_file():
        graph = load_graph(root, work_id)
    else:
        graph = {
            "work_id": work_id,
            "tasks": [{"id": task_id, "depends_on": [], "owned_paths": []}
                      for task_id in (task_ids or (state or {}).get("tasks", {}))],
        }
    require_safe(root, work_id, graph, state)


def load_state(root: Path, work_id: str) -> dict:
    path = state_path(root, work_id)
    from inner_loop.checkpoint import CheckpointError, restore_cache
    from inner_loop.recovery import RecoveryRequired

    if not path.is_file():
        try:
            restored = restore_cache(root, work_id)
        except CheckpointError as exc:
            raise RecoveryRequired({
                "status": "recovery_required", "work_id": work_id,
                "evidence_paths": [str(path.relative_to(root))], "conflicts": [str(exc)],
            }) from exc
        if restored is None:
            raise FileNotFoundError(str(path))
        return restored
    raw = path.read_bytes()
    try:
        cached = json.loads(raw)
    except json.JSONDecodeError:
        # Preserve corrupt bytes for explicit reconciliation; they cannot be
        # proven to be an exact older generation.
        raise
    try:
        restored = restore_cache(root, work_id, cached)
    except CheckpointError as exc:
        raise RecoveryRequired({
            "status": "recovery_required", "work_id": work_id,
            "evidence_paths": [str(path.relative_to(root))], "conflicts": [str(exc)],
        }) from exc
    return restored if restored is not None else cached


@contextmanager
def state_lock(root: Path, work_id: str):
    """Serialize cooperative local processes; keep the lock inode across writes."""
    _require_coordinator()
    path = state_path(root, work_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def _write_state(path: Path, doc: dict) -> None:
    running = [tid for tid, t in doc["tasks"].items() if t.get("status") == "running"]
    if len(running) > 1:
        raise SecondWriter("second writer refused; running: " + ",".join(running))
    # Replacement is atomic for readers. File fsync is not a promise of power-loss
    # durability for the directory entry on every filesystem.
    name = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".state-", suffix=".tmp", delete=False) as tmp:
            name = tmp.name
            tmp.write(json.dumps(doc, indent=2) + "\n")
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(name, path)
    finally:
        if name is not None:
            Path(name).unlink(missing_ok=True)


def _publish_state(root: Path, work_id: str, doc: dict) -> None:
    # Red phase: retain pre-checkpoint state publication behavior.
    _write_state(state_path(root, work_id), doc)


@contextmanager
def state_transaction(root: Path, work_id: str, observed_revision: int | None = None):
    """Hold the lock through validation, side effects and one atomic state fold."""
    with state_lock(root, work_id):
        doc = load_state(root, work_id)
        stored = int(doc["revision"])
        if observed_revision is not None and stored != observed_revision:
            raise CasConflict(f"revision mismatch: observed={observed_revision} stored={stored}")
        _require_reconciled(root, work_id, doc)
        yield doc
        doc["revision"] = stored + 1
        _publish_state(root, work_id, doc)


def cas_init(root: Path, work_id: str, task_ids: list[str], coordinator_sha: str = "") -> dict:
    _require_coordinator()
    doc = {
        "schema": SCHEMA,
        "work_id": work_id,
        "revision": 0,
        "coordinator_sha": coordinator_sha,
        "coordinator_branch": f"agent/{work_id}",
        "tasks": {
            tid: {
                "status": "pending",
                "base_sha": "",
                "task_branch": "",
                "result_path": "",
                "boundary_reject": None,
                "review_round": 0,
                "debug_round": 0,
                "evidence": {},
                "attempt_number": 0,
                "attempt_id": "",
                "accepted_plan_ref": "",
                "accepted_plan_digest": "",
                "attempt_started_revision": None,
                "attempt_history": [],
            }
            for tid in task_ids
        },
    }
    path = state_path(root, work_id)
    with state_lock(root, work_id):
        if path.exists():
            try:
                doc = load_state(root, work_id)
            except json.JSONDecodeError:
                _require_reconciled(root, work_id, None, task_ids)
                raise
            # Existing state owns its task identities. Caller-supplied IDs are
            # only initialization input and must not make an idempotent retry
            # look like a conflicting graph when no accepted graph file exists.
            _require_reconciled(root, work_id, doc)
            return doc
        from inner_loop.checkpoint import CheckpointError, restore_cache
        try:
            restored = restore_cache(root, work_id)
        except CheckpointError as exc:
            from inner_loop.recovery import RecoveryRequired
            raise RecoveryRequired({
                "status": "recovery_required", "work_id": work_id,
                "evidence_paths": [str(path.relative_to(root))], "conflicts": [str(exc)],
            }) from exc
        if restored is not None:
            _require_reconciled(root, work_id, restored)
            return restored
        _require_reconciled(root, work_id, None, task_ids)
        _publish_state(root, work_id, doc)
        return doc


def cas_apply(root: Path, work_id: str, observed_revision: int, mutator) -> dict:
    with state_transaction(root, work_id, observed_revision) as doc:
        mutator(doc)
    return doc


def spawn_writer(root: Path, work_id: str, task_id: str) -> dict:
    with state_transaction(root, work_id) as doc:
        running = [tid for tid, t in doc["tasks"].items() if t.get("status") == "running"]
        if running:
            raise SecondWriter(f"second writer refused; already running: {','.join(running)}")
        task = doc["tasks"][task_id]
        if task["status"] not in ("pending", "ready"):
            raise ProtocolViolation(f"cannot start {task_id}: {task['status']}")
        from inner_loop.attempts import new_attempt
        task.update(new_attempt(task_id, task, root, work_id, int(doc["revision"]) + 1))
        task["status"] = "running"
        task["base_sha"] = doc["coordinator_sha"]
    return doc
