"""Coordinator-controlled task attempt transitions."""
from __future__ import annotations

import copy
import fcntl
import json
from pathlib import Path
import subprocess

from inner_loop.state import ProtocolViolation, state_transaction


def accepted_plan_ref(root: Path, work_id: str) -> str:
    ref = f"refs/ask/accepted-tests/{work_id}"
    proc = subprocess.run(["git", "rev-parse", "--verify", ref], cwd=root,
                          capture_output=True, text=True)
    if proc.returncode:
        return ""
    return proc.stdout.strip()


def _execution_runs(root: Path, work_id: str, task_id: str) -> list[dict]:
    directory = root / "work" / work_id / "traceability"
    ledger = directory / "executions.json"
    if not ledger.is_file():
        return []
    with (directory / "executions.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        try:
            rows = json.loads(ledger.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ProtocolViolation(f"cannot preserve traceability execution history: {exc}") from exc
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ProtocolViolation("traceability execution ledger has an unsupported shape")
    return [copy.deepcopy(row) for row in rows if row.get("task_id") == task_id]


def new_attempt(task_id: str, task: dict, root: Path, work_id: str, revision: int) -> dict:
    number = int(task.get("attempt_number") or 0) + 1
    return {
        "attempt_number": number,
        "attempt_id": f"{task_id}:attempt-{number}",
        "accepted_plan_ref": accepted_plan_ref(root, work_id),
        "attempt_started_revision": revision,
    }


def interrupt_task(root: Path, work_id: str, task_id: str, reason: str) -> dict:
    if not isinstance(reason, str) or not reason.strip():
        raise ProtocolViolation("attempt interruption requires a reason")
    with state_transaction(root, work_id) as doc:
        task = (doc.get("tasks") or {}).get(task_id)
        if not task or task.get("status") != "running":
            raise ProtocolViolation(f"task {task_id} is not the active running attempt")
        running = [tid for tid, item in doc["tasks"].items() if item.get("status") == "running"]
        if running != [task_id]:
            raise ProtocolViolation("attempt interruption requires the unique running task")
        if task.get("result_path"):
            raise ProtocolViolation("attempt has a recorded TaskResult; reconcile it before interruption")
        result = root / "work" / work_id / "inner-loop" / "results" / f"{task_id}.json"
        if result.is_file():
            raise ProtocolViolation("attempt has a TaskResult file; reconcile it before interruption")

        current_ref = accepted_plan_ref(root, work_id)
        number = int(task.get("attempt_number") or 1)
        existing_attempt_id = task.get("attempt_id") or ""
        attempt_id = existing_attempt_id or f"{task_id}:attempt-{number}"
        history = task.setdefault("attempt_history", [])
        history.append({
            "attempt_id": attempt_id,
            "attempt_number": number,
            "status": "interrupted",
            "reason": reason.strip(),
            "attempt_id_created_during_interrupt": not bool(existing_attempt_id),
            "base_sha": task.get("base_sha") or "",
            "task_branch": task.get("task_branch") or "",
            "result_path": task.get("result_path") or "",
            "evidence": copy.deepcopy(task.get("evidence") or {}),
            "accepted_plan_ref": task.get("accepted_plan_ref") or current_ref,
            "execution_runs": _execution_runs(root, work_id, task_id),
            "started_revision": task.get("attempt_started_revision"),
            "interrupted_revision": int(doc["revision"]) + 1,
        })
        task.update({
            "status": "interrupted",
            "attempt_number": number,
            "attempt_id": "",
            "accepted_plan_ref": "",
            "attempt_started_revision": None,
            "base_sha": "",
            "task_branch": "",
            "result_path": "",
            "review_round": 0,
            "debug_round": 0,
            "evidence": {},
        })
    return doc


def reopen_task(root: Path, work_id: str, task_id: str, reason: str) -> dict:
    if not isinstance(reason, str) or not reason.strip():
        raise ProtocolViolation("reopening an attempt requires a reason")
    with state_transaction(root, work_id) as doc:
        task = (doc.get("tasks") or {}).get(task_id)
        if not task or task.get("status") != "interrupted":
            raise ProtocolViolation(f"task {task_id} has no interrupted attempt to reopen")
        if any(item.get("status") == "running" for item in doc["tasks"].values()):
            raise ProtocolViolation("cannot reopen while another task is running")
        history = task.get("attempt_history") or []
        if not history:
            raise ProtocolViolation("interrupted attempt history is missing")
        current_ref = accepted_plan_ref(root, work_id)
        if not current_ref:
            raise ProtocolViolation("accepted test-plan ref is unavailable; cannot reopen this task")
        if current_ref == history[-1].get("accepted_plan_ref"):
            raise ProtocolViolation("accept the reviewed plan amendment before reopening this task")

        attempt = new_attempt(task_id, task, root, work_id, int(doc["revision"]) + 1)
        task.update({
            **attempt,
            "status": "running",
            "base_sha": doc.get("coordinator_sha") or "",
            "task_branch": "",
            "result_path": "",
            "boundary_reject": None,
            "review_round": 0,
            "debug_round": 0,
            "evidence": {},
            "reopened_from_attempt": history[-1]["attempt_id"],
            "reopen_reason": reason.strip(),
        })
    return doc
