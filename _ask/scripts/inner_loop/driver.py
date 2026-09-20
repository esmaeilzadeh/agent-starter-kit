"""Coordinator driver: run / resume / cancel / integrate_ready.

Hidden: ready-set scheduling, TaskResult TDD/exemption gate, CAS SHA fold.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from inner_loop.graph import _task_map, load_graph, validate_graph
from inner_loop.integrate import Escalate, resume as git_resume
from inner_loop.integrate import integrate as git_integrate
from inner_loop.state import cas_apply, cas_init, load_state, spawn_writer


class NotIntegrable(RuntimeError):
    pass


def result_path(root: Path, work_id: str, task_id: str) -> Path:
    return root / "work" / work_id / "inner-loop" / "results" / f"{task_id}.json"


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


def check_integrable(result: dict) -> None:
    exemption = result.get("exemption")
    tdd = result.get("tdd")
    if exemption:
        if not exemption.get("reviewer_ack"):
            raise NotIntegrable("exemption without reviewer_ack")
        return
    if not tdd:
        raise NotIntegrable("missing TDD evidence")
    red = tdd.get("red") or {}
    green = tdd.get("green") or {}
    if int(red.get("exit_code", 0)) == 0:
        raise NotIntegrable("red did not fail")
    if int(green.get("exit_code", 1)) != 0:
        raise NotIntegrable("green did not pass")


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


def integrate_ready(root: Path, work_id: str, task_id: str | None = None) -> str:
    doc = load_state(root, work_id)
    if task_id is None:
        running = _running(doc)
        if len(running) != 1:
            raise Escalate("no running task to integrate")
        task_id = running[0]
    path = result_path(root, work_id, task_id)
    if not path.is_file():
        raise NotIntegrable(f"missing TaskResult {path}")
    result = json.loads(path.read_text(encoding="utf-8"))
    check_integrable(result)
    branch = (doc.get("tasks") or {}).get(task_id, {}).get("task_branch") or ""
    if branch:
        sha = git_integrate(root, branch, "ff-only")
    else:
        sha = git_sha(root)
    observed = int(doc["revision"])
    rel = str(path)
    try:
        rel = str(path.relative_to(root))
    except ValueError:
        pass

    def mut(d: dict) -> None:
        d["tasks"][task_id]["status"] = "integrated"
        d["tasks"][task_id]["result_path"] = rel
        d["coordinator_sha"] = sha

    cas_apply(root, work_id, observed, mut)
    return sha


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


def run_until(root: Path, work_id: str) -> str:
    while True:
        out = run_once(root, work_id)
        if out.startswith("running=") or out.startswith("waiting="):
            return out
        if out in ("quiescent",):
            return out
        return out


def resume_from_state(root: Path, work_id: str) -> str:
    doc = ensure_state(root, work_id)
    sha = doc.get("coordinator_sha") or ""
    aborted = ""
    if sha and _is_git(root):
        aborted = git_resume(root, sha)
    nxt = run_until(root, work_id)
    if aborted == "aborted":
        return f"aborted\n{nxt}"
    return nxt


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
