from __future__ import annotations

import json
import os
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def cas_apply(root: Path, work_id: str, observed_revision: int, mutator) -> dict:
    _require_coordinator()
    path = state_path(root, work_id)
    doc = load_state(root, work_id)
    stored = int(doc.get("revision", 0))
    if stored != observed_revision:
        raise CasConflict(f"revision mismatch: observed={observed_revision} stored={stored}")
    mutator(doc)
    doc["revision"] = stored + 1
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def spawn_writer(root: Path, work_id: str, task_id: str) -> dict:
    _require_coordinator()
    doc = load_state(root, work_id)
    running = [tid for tid, t in (doc.get("tasks") or {}).items() if t.get("status") == "running"]
    if running:
        raise SecondWriter(f"second writer refused; already running: {','.join(running)}")
    if task_id not in doc.get("tasks", {}):
        raise KeyError(task_id)

    def mut(d: dict) -> None:
        d["tasks"][task_id]["status"] = "running"

    return cas_apply(root, work_id, int(doc["revision"]), mut)
