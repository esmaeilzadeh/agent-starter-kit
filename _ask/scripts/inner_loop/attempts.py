"""Coordinator-controlled task attempt transitions."""
from __future__ import annotations

import copy
import fcntl
import fnmatch
import hashlib
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


def accepted_plan_digest(root: Path, work_id: str) -> str:
    ref = accepted_plan_ref(root, work_id)
    if not ref:
        return ""
    proc = subprocess.run(["git", "show", f"{ref}:accepted.json"], cwd=root,
                          capture_output=True, text=True)
    if proc.returncode:
        return ""
    try:
        decision = json.loads(proc.stdout)
        review = decision.get("plan_review") if isinstance(decision, dict) else None
        digest = review.get("plan_digest", "") if isinstance(review, dict) else ""
    except (TypeError, ValueError):
        return ""
    return digest if isinstance(digest, str) else ""


def accepted_plan_review_digest(root: Path, ref: str) -> str:
    if not ref:
        return ""
    proc = subprocess.run(["git", "show", f"{ref}:accepted.json"], cwd=root,
                          capture_output=True, text=True)
    if proc.returncode:
        return ""
    try:
        decision = json.loads(proc.stdout)
    except (TypeError, ValueError):
        return ""
    digest = decision.get("plan_review_digest", "") if isinstance(decision, dict) else ""
    return digest if isinstance(digest, str) else ""


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return bool(ancestor and descendant) and subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant], cwd=root,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def _reviewed_reconciliation(root: Path, work_id: str, task_id: str, doc: dict):
    """Validate an exact reviewed source postimage before reopening an attempt."""
    task = (doc.get("tasks") or {}).get(task_id)
    history = (task or {}).get("attempt_history") or []
    if not task or task.get("status") != "interrupted" or not history:
        raise ProtocolViolation("attempt reconciliation does not name an interrupted task")
    prior = history[-1]
    previous_number = int(prior.get("attempt_number") or 0)
    next_number = int(task.get("attempt_number") or previous_number) + 1
    directory = root / "work" / work_id / "inner-loop" / "evidence"
    path = directory / f"reconciliation-{task_id}-attempt-{previous_number}-to-{next_number}.json"
    # Keep the original attempt-1 -> attempt-2 receipt readable as immutable
    # history. Later transitions always select their own transition identity.
    legacy_path = directory / f"reconciliation-{task_id}.json"
    if not path.is_file() and previous_number == 1 and next_number == 2 and legacy_path.is_file():
        path = legacy_path
    if not path.is_file():
        return None
    try:
        raw = path.read_bytes()
        record = json.loads(raw)
    except (OSError, ValueError) as exc:
        raise ProtocolViolation(f"attempt reconciliation is unreadable: {exc}") from exc
    if not isinstance(record, dict) or record.get("schema") != "ask-inner-loop-reconciliation/v1":
        raise ProtocolViolation("attempt reconciliation has an unsupported schema")
    pin_ref = accepted_plan_ref(root, work_id)
    pin_digest = accepted_plan_digest(root, work_id)
    head = subprocess.run(["git", "rev-parse", "--verify", "HEAD^{commit}"], cwd=root,
                          capture_output=True, text=True)
    checkpoint = subprocess.run(
        ["git", "rev-parse", "--verify", f"refs/ask/inner-loop/{work_id}"], cwd=root,
        capture_output=True, text=True,
    )
    expected = {
        "work_id": work_id,
        "task_id": task_id,
        "previous_checkpoint_sha": checkpoint.stdout.strip() if checkpoint.returncode == 0 else "",
        "previous_revision": int(doc.get("revision", -1)),
        "previous_attempt_id": prior.get("attempt_id"),
        "interrupted_candidate_sha": prior.get("interrupted_candidate_sha"),
        "new_attempt_id": f"{task_id}:attempt-{int(task.get('attempt_number') or 0) + 1}",
        "accepted_plan_ref": pin_ref,
        "accepted_plan_digest": pin_digest,
        "new_attempt_base_sha": doc.get("coordinator_sha") or "",
        "candidate_sha": head.stdout.strip() if head.returncode == 0 else "",
    }
    if any(record.get(key) != value for key, value in expected.items()):
        raise ProtocolViolation("attempt reconciliation identity is stale or conflicts with coordinator state")
    if not pin_ref or not pin_digest:
        raise ProtocolViolation("attempt reconciliation requires an accepted plan ref and digest")
    if not _is_ancestor(root, expected["new_attempt_base_sha"], expected["interrupted_candidate_sha"]):
        raise ProtocolViolation("interrupted candidate is outside the recorded coordinator ancestry")
    if not _is_ancestor(root, expected["interrupted_candidate_sha"], expected["candidate_sha"]):
        raise ProtocolViolation("reconciled source postimage is outside the interrupted candidate ancestry")
    if subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True,
                      text=True).stdout.strip():
        raise ProtocolViolation("attempt reconciliation requires a clean source postimage")

    review = record.get("review")
    recorded_by = record.get("recorded_by")
    payload = {key: value for key, value in record.items() if key != "review"}
    payload_digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if (not isinstance(review, dict) or review.get("decision") != "APPROVED"
            or not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip()
            or not isinstance(recorded_by, str) or not recorded_by.strip()
            or review.get("reviewer") == recorded_by
            or review.get("candidate_sha") != expected["candidate_sha"]
            or review.get("payload_sha256") != payload_digest):
        raise ProtocolViolation("attempt reconciliation lacks an exact approved independent review")

    from inner_loop.graph import load_graph
    graph = load_graph(root, work_id)
    graph_tasks = graph.get("tasks") or []
    task_map = ({str(key): value for key, value in graph_tasks.items()}
                if isinstance(graph_tasks, dict)
                else {str(item.get("id")): item for item in graph_tasks if item.get("id")})
    owner_patterns = [str(item) for item in (task_map.get(task_id) or {}).get("owned_paths") or []]
    downstream_patterns: list[str] = []
    for dependent_id, dependent in task_map.items():
        pending = [dependent_id]
        seen = set()
        depends = False
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            current_task = task_map.get(current) or {}
            dependencies = [str(item) for item in current_task.get("depends_on") or []]
            if task_id in dependencies:
                depends = True
                break
            pending.extend(dependencies)
        if depends and (doc.get("tasks", {}).get(dependent_id) or {}).get("status") in {"pending", "ready"}:
            downstream_patterns.extend(str(item) for item in dependent.get("owned_paths") or [])
    changed = subprocess.run(
        ["git", "diff", "--name-only", "-z", expected["interrupted_candidate_sha"] + ".." + expected["candidate_sha"]],
        cwd=root, capture_output=True, text=True,
    )
    if changed.returncode:
        raise ProtocolViolation("cannot inspect committed changes after the interrupted candidate")
    changed_paths = {name for name in changed.stdout.split("\0") if name}
    allowed = {name for name in changed_paths
               if any(fnmatch.fnmatchcase(name, owner) for owner in owner_patterns)
               and any(fnmatch.fnmatchcase(name, dependent) for dependent in downstream_patterns)}
    postimage = record.get("source_postimage")
    if not isinstance(postimage, dict) or set(postimage) != allowed or not allowed:
        raise ProtocolViolation("attempt reconciliation must name every exact overlapping source change")
    for name, digest in postimage.items():
        blob = subprocess.run(["git", "show", f"{expected['candidate_sha']}:{name}"], cwd=root,
                              capture_output=True)
        if blob.returncode or hashlib.sha256(blob.stdout).hexdigest() != digest:
            raise ProtocolViolation(f"attempt reconciliation source postimage mismatch: {name}")
    return {"paths": allowed, "path": str(path.relative_to(root)),
            "digest": hashlib.sha256(raw).hexdigest(), "candidate_sha": expected["candidate_sha"]}


def _execution_runs(root: Path, work_id: str, task_id: str,
                    plan_digest: str = "") -> list[dict]:
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
    return [copy.deepcopy(row) for row in rows
            if row.get("task_id") == task_id
            and (not plan_digest or row.get("plan_digest") == plan_digest)]


def new_attempt(task_id: str, task: dict, root: Path, work_id: str, revision: int) -> dict:
    number = int(task.get("attempt_number") or 0) + 1
    return {
        "attempt_number": number,
        "attempt_id": f"{task_id}:attempt-{number}",
        "accepted_plan_ref": accepted_plan_ref(root, work_id),
        "accepted_plan_digest": accepted_plan_digest(root, work_id),
        "attempt_started_revision": revision,
    }


def interrupt_task(root: Path, work_id: str, task_id: str, reason: str) -> dict:
    if not isinstance(reason, str) or not reason.strip():
        raise ProtocolViolation("attempt interruption requires a reason")
    with state_transaction(root, work_id, archive_attempt_evidence=True) as doc:
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
        current_digest = accepted_plan_digest(root, work_id)
        candidate = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD^{commit}"], cwd=root,
            capture_output=True, text=True,
        )
        if candidate.returncode:
            raise ProtocolViolation("cannot identify the interrupted candidate commit")
        candidate_sha = candidate.stdout.strip()
        base_sha = task.get("base_sha") or doc.get("coordinator_sha") or ""
        if base_sha and subprocess.run(
            ["git", "merge-base", "--is-ancestor", base_sha, candidate_sha], cwd=root,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode:
            raise ProtocolViolation("interrupted candidate is outside its task base ancestry")
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
            "base_sha": base_sha,
            "interrupted_candidate_sha": candidate_sha,
            "task_branch": task.get("task_branch") or "",
            "result_path": task.get("result_path") or "",
            "evidence": copy.deepcopy(task.get("evidence") or {}),
            "accepted_plan_ref": task.get("accepted_plan_ref") or current_ref,
            "accepted_plan_digest": task.get("accepted_plan_digest") or current_digest,
            "execution_runs": _execution_runs(
                root, work_id, task_id,
                task.get("accepted_plan_digest") or current_digest,
            ),
            "started_revision": task.get("attempt_started_revision"),
            "interrupted_revision": int(doc["revision"]) + 1,
        })
        task.update({
            "status": "interrupted",
            "attempt_number": number,
            "attempt_id": "",
            "accepted_plan_ref": "",
            "accepted_plan_digest": "",
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
    reconciliation: dict | None = None

    def validate_reconciliation(doc: dict) -> set[str] | None:
        nonlocal reconciliation
        reconciliation = _reviewed_reconciliation(root, work_id, task_id, doc)
        return set(reconciliation["paths"]) if reconciliation else None

    with state_transaction(root, work_id,
                           reconciliation_validator=validate_reconciliation) as doc:
        task = (doc.get("tasks") or {}).get(task_id)
        if not task or task.get("status") != "interrupted":
            raise ProtocolViolation(f"task {task_id} has no interrupted attempt to reopen")
        if any(item.get("status") == "running" for item in doc["tasks"].values()):
            raise ProtocolViolation("cannot reopen while another task is running")
        history = task.get("attempt_history") or []
        if not history:
            raise ProtocolViolation("interrupted attempt history is missing")
        current_ref = accepted_plan_ref(root, work_id)
        current_digest = accepted_plan_digest(root, work_id)
        if not current_ref:
            raise ProtocolViolation("accepted test-plan ref is unavailable; cannot reopen this task")
        if not current_digest:
            raise ProtocolViolation("accepted plan digest is unavailable; cannot reopen this task")
        previous_ref = history[-1].get("accepted_plan_ref") or ""
        previous_digest = history[-1].get("accepted_plan_digest") or ""
        previous_review_digest = accepted_plan_review_digest(root, previous_ref)
        current_review_digest = accepted_plan_review_digest(root, current_ref)
        if (current_ref == previous_ref
                or (current_digest == previous_digest
                    and current_review_digest == previous_review_digest)):
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
        if reconciliation:
            task["source_reconciliation"] = {
                "path": reconciliation["path"],
                "digest": reconciliation["digest"],
                "candidate_sha": reconciliation["candidate_sha"],
                "paths": sorted(reconciliation["paths"]),
            }
    return doc
