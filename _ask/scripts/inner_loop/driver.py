"""Coordinator driver: run / resume / cancel / integrate_ready.

Hidden: ready-set scheduling, TaskResult TDD/exemption gate, CAS SHA fold.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from engineering_model.workflow import guarded_workflow

from inner_loop.evidence import (
    NotIntegrable, check_integrable, git, read_candidate, result_path,
    runtime_exclusions, source_changes, validate_review, verify_candidate,
)
from inner_loop.graph import _task_map, load_graph, validate_graph
from inner_loop.integrate import Escalate, resume as git_resume
from inner_loop.integrate import integrate as git_integrate
from inner_loop.state import cas_apply, cas_init, load_state, spawn_writer, state_lock, state_transaction


def git_sha(root: Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def _is_git(root: Path) -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "--git-dir"], cwd=root, capture_output=True, text=True
    )
    return proc.returncode == 0


def _depends(task: dict) -> list[str]:
    deps = task.get("depends_on") or []
    if deps is None:
        return []
    return [str(d) for d in deps]


def _running(doc: dict) -> list[str]:
    return [
        tid
        for tid, t in sorted((doc.get("tasks") or {}).items())
        if t.get("status") == "running"
    ]


def ready_ids(graph: dict, doc: dict) -> list[str]:
    tasks = _task_map(graph)
    st = doc.get("tasks") or {}
    integrated = {
        tid for tid, t in st.items() if t.get("status") == "integrated"
    }
    skip = {
        "running",
        "integrated",
        "cancelled",
        "blocked",
        "failed",
        "escalated",
    }
    ready: list[str] = []
    for tid in sorted(tasks):
        status = (st.get(tid) or {}).get("status") or "pending"
        if status in skip:
            continue
        deps = _depends(tasks[tid])
        if all(d in integrated for d in deps):
            ready.append(tid)
    return ready


@guarded_workflow
def ensure_state(root: Path, work_id: str) -> dict:
    graph = load_graph(root, work_id)
    status = validate_graph(graph)
    if status != "ok":
        raise ValueError(status)
    try:
        return load_state(root, work_id)
    except FileNotFoundError:
        ids = list(_task_map(graph))
        return cas_init(root, work_id, ids, coordinator_sha=git_sha(root))


@guarded_workflow
def integrate_ready(root: Path, work_id: str, task_id: str | None = None) -> str:
    # Hold the same process lock as cancellation/spawn through Git and evidence
    # side effects. A crash after FF leaves old valid state and is retryable.
    with state_transaction(root, work_id) as doc:
        running = _running(doc)
        if len(running) != 1:
            raise Escalate("no running task to integrate")
        task_id = task_id or running[0]
        candidate = read_candidate(root, work_id, task_id, doc)
        check_integrable(candidate.result)
        task = doc['tasks'][task_id]
        review = validate_review(root, task, candidate)
        if source_changes(root, work_id):
            raise NotIntegrable('dirty coordinator source; commit or resolve changes before integration')
        evidence = verify_candidate(root, candidate)
        # Checks can take time: ref/result/review or coordinator source drift
        # invalidates their applicability before any FF/state advancement.
        current = read_candidate(root, work_id, task_id, doc)
        if current != candidate or source_changes(root, work_id):
            raise NotIntegrable('candidate/result/source changed during verification')
        validate_review(root, task, current)
        sha = git_integrate(root, candidate.identity['candidate_sha'], 'ff-only', work_id=work_id)
        if sha != candidate.identity['candidate_sha'] or git(root, 'rev-parse', 'HEAD^{tree}') != evidence['tree_sha']:
            raise Escalate('integrated HEAD/tree differs from verified candidate')
        evidence['resulting_sha'] = sha
        evidence['review'] = review
        (root / evidence['record_path']).write_text(json.dumps(evidence, indent=2) + '\n')
        task['status'] = 'integrated'
        task['result_path'] = str(result_path(root, work_id, task_id).relative_to(root))
        task['evidence']['verification'] = evidence
        doc['coordinator_sha'] = sha
    return sha


@guarded_workflow
def run_once(root: Path, work_id: str) -> str:
    ensure_state(root, work_id)
    graph = load_graph(root, work_id)
    doc = load_state(root, work_id)
    running = _running(doc)
    if running:
        tid = running[0]
        if result_path(root, work_id, tid).is_file():
            integrate_ready(root, work_id, tid)
            return run_once(root, work_id)
        return f"waiting={tid}"
    ready = ready_ids(graph, doc)
    if not ready:
        return "quiescent"
    tid = ready[0]
    spawn_writer(root, work_id, tid)
    return f"running={tid}"


@guarded_workflow
def run_until(root: Path, work_id: str) -> str:
    while True:
        out = run_once(root, work_id)
        if out.startswith("running=") or out.startswith("waiting="):
            return out
        if out in ("quiescent",):
            return out
        return out


@guarded_workflow
def resume_from_state(root: Path, work_id: str) -> str:
    ensure_state(root, work_id)
    aborted = ""
    with state_lock(root, work_id):
        doc = load_state(root, work_id)
        sha = doc.get("coordinator_sha") or ""
        if sha and _is_git(root):
            git_dir = Path(git(root, 'rev-parse', '--absolute-git-dir'))
            in_progress = any((git_dir / n).exists() for n in ('MERGE_HEAD', 'CHERRY_PICK_HEAD'))
            # Runtime result/state/evidence changes are expected. In particular,
            # do not reset a verified FF candidate back to its pre-task base.
            if source_changes(root, work_id) or in_progress:
                aborted = git_resume(root, sha, preserve_paths=runtime_exclusions(work_id), work_id=work_id)
    nxt = run_until(root, work_id)
    if aborted == "aborted":
        return f"aborted\n{nxt}"
    return nxt


@guarded_workflow
def cancel(root: Path, work_id: str, target: str) -> str:
    doc = ensure_state(root, work_id)
    ids = list(doc.get("tasks") or {})
    if target == "all":
        chosen = ids
    else:
        if target not in ids:
            raise KeyError(target)
        chosen = [target]
    observed = int(doc["revision"])

    def mut(d: dict) -> None:
        for tid in chosen:
            d["tasks"][tid]["status"] = "cancelled"

    cas_apply(root, work_id, observed, mut)
    return "cancelled=" + ",".join(chosen)
