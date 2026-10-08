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


def load_state(root: Path, work_id: str) -> dict:
    path = state_path(root, work_id)
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return json.loads(path.read_text(encoding="utf-8"))


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


@contextmanager
def state_transaction(root: Path, work_id: str, observed_revision: int | None = None):
    """Hold the lock through validation, side effects and one atomic state fold."""
    with state_lock(root, work_id):
        doc = load_state(root, work_id)
        stored = int(doc["revision"])
        if observed_revision is not None and stored != observed_revision:
            raise CasConflict(f"revision mismatch: observed={observed_revision} stored={stored}")
        yield doc
        doc["revision"] = stored + 1
        _write_state(state_path(root, work_id), doc)


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
            }
            for tid in task_ids
        },
    }
    path = state_path(root, work_id)
    with state_lock(root, work_id):
        if path.exists():
            return load_state(root, work_id)
        _write_state(path, doc)
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
        task["status"] = "running"
        task["base_sha"] = doc["coordinator_sha"]
    return doc
