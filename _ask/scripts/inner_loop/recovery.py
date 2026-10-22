"""Work-ID-scoped reconciliation before state initialization or writer admission."""
from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path
import subprocess


class RecoveryRequired(RuntimeError):
    """The runtime history cannot safely authorize a new or resumed attempt."""

    def __init__(self, report: dict):
        super().__init__("recovery_required")
        self.report = report


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def _commit_exists(root: Path, sha: str) -> bool:
    return bool(sha) and _git(root, "cat-file", "-e", sha + "^{commit}").returncode == 0


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    return bool(ancestor and descendant) and _git(
        root, "merge-base", "--is-ancestor", ancestor, descendant
    ).returncode == 0


def _task_map(graph: dict | None, state: dict | None) -> dict[str, dict]:
    tasks = (graph or {}).get("tasks") or []
    if isinstance(tasks, dict):
        return {str(key): value for key, value in tasks.items()}
    if tasks:
        return {str(task.get("id")): task for task in tasks if task.get("id")}
    return {
        str(task_id): {"id": str(task_id), "owned_paths": []}
        for task_id in ((state or {}).get("tasks") or {})
    }


def _accepted_anchor(root: Path, work_id: str) -> tuple[str | None, str | None]:
    path = root / "work" / work_id / "traceability-accepted.json"
    if not path.is_file():
        return None, None
    try:
        pin = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"{path.relative_to(root)}: invalid accepted contract pin: {exc}"
    if pin.get("work_id") != work_id:
        return None, f"{path.relative_to(root)}: accepted contract work_id mismatch"
    anchor = pin.get("contract_sha")
    if not isinstance(anchor, str) or not _commit_exists(root, anchor):
        return None, f"{path.relative_to(root)}: accepted contract anchor is missing or invalid"
    return anchor, None


def _accepted_anchor_at(root: Path, work_id: str, commit: str) -> tuple[str | None, str | None]:
    """Read the accepted contract identity recorded at a task's immutable base."""
    name = f"work/{work_id}/traceability-accepted.json"
    proc = _git(root, "show", f"{commit}:{name}")
    if proc.returncode:
        return None, f"{name} is unavailable at TaskResult base_sha"
    try:
        pin = json.loads(proc.stdout)
    except ValueError as exc:
        return None, f"{name} is invalid at TaskResult base_sha: {exc}"
    if not isinstance(pin, dict) or pin.get("work_id") != work_id:
        return None, f"{name} work_id is invalid at TaskResult base_sha"
    anchor = pin.get("contract_sha")
    if not isinstance(anchor, str) or not _commit_exists(root, anchor):
        return None, f"{name} has no valid contract_sha at TaskResult base_sha"
    return anchor, None


def _changed_paths(root: Path, base: str, head: str) -> list[str]:
    names: set[str] = set()
    if base and head and _commit_exists(root, base) and _commit_exists(root, head):
        proc = _git(root, "diff", "--name-only", "-z", base + ".." + head)
        if proc.returncode == 0:
            names.update(proc.stdout.split("\0"))
    for args in (
        ("diff", "--name-only", "-z"),
        ("diff", "--cached", "--name-only", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
    ):
        proc = _git(root, *args)
        if proc.returncode == 0:
            names.update(proc.stdout.split("\0"))
    return sorted(name for name in names if name)


def _owned_changes(root: Path, task: dict, base: str, head: str) -> list[str]:
    patterns = [str(path) for path in (task.get("owned_paths") or [])]
    return [
        name for name in _changed_paths(root, base, head)
        if any(fnmatch.fnmatchcase(name, pattern) for pattern in patterns)
    ]


def _result_files(root: Path, work_id: str) -> list[Path]:
    directory = root / "work" / work_id / "inner-loop" / "results"
    return sorted(directory.glob("*.json")) if directory.is_dir() else []


def _review_files(root: Path, work_id: str, task_id: str) -> list[str]:
    directory = root / "work" / work_id / "inner-loop" / "evidence"
    if not directory.is_dir():
        return []
    found = []
    for path in sorted(directory.rglob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(doc, dict) and doc.get("work_id") == work_id and doc.get("task_id") == task_id:
            found.append(str(path.relative_to(root)))
    return found


def _report(work_id: str, task_ids: set[str], paths: set[str], conflicts: list[str]) -> dict:
    return {
        "status": "recovery_required",
        "work_id": work_id,
        "task_ids": sorted(task_ids),
        "evidence_paths": sorted(paths),
        "conflicts": sorted(set(conflicts)),
        "next_actions": [
            "inspect the listed state, result, review, and source history",
            "write an explicit reconciliation record that preserves every prior attempt",
            "resume only after the reconciled state and evidence are reviewed",
        ],
    }


def inspect(root: Path, work_id: str, graph: dict, state: dict | None = None) -> dict | None:
    """Return recovery evidence when runtime state conflicts with retained history."""
    root = Path(root).resolve()
    tasks = _task_map(graph, state)
    task_ids: set[str] = set()
    paths: set[str] = set()
    conflicts: list[str] = []
    state_path = root / "work" / work_id / "inner-loop" / "state.json"
    state_exists = state_path.is_file()

    if state is None and state_exists:
        conflicts.append("state.json exists but could not be loaded")
        paths.add(str(state_path.relative_to(root)))

    if state is not None:
        if state.get("work_id") != work_id:
            conflicts.append("state.json work_id does not match the selected workstream")
            paths.add(str(state_path.relative_to(root)))
        recorded = set((state.get("tasks") or {}).keys())
        expected = set(tasks)
        if recorded != expected:
            conflicts.append(
                "state task identities differ from the accepted task graph "
                f"(missing={','.join(sorted(expected-recorded)) or '-'}; "
                f"unexpected={','.join(sorted(recorded-expected)) or '-'})"
            )
            paths.add(str(state_path.relative_to(root)))
        coordinator = state.get("coordinator_sha") or ""
        if coordinator and not _commit_exists(root, coordinator):
            conflicts.append("state coordinator_sha is missing from this Git object database")
            paths.add(str(state_path.relative_to(root)))

    result_docs: list[tuple[str, dict, bytes]] = []
    for path in _result_files(root, work_id):
        relative = str(path.relative_to(root))
        paths.add(relative)
        task_id = path.stem
        task_ids.add(task_id)
        try:
            raw = path.read_bytes()
            result = json.loads(raw)
        except (OSError, ValueError) as exc:
            conflicts.append(f"{relative}: invalid TaskResult: {exc}")
            continue
        if not isinstance(result, dict):
            conflicts.append(f"{relative}: TaskResult must be a JSON object")
            continue
        result_docs.append((relative, result, raw))
        if task_id not in tasks:
            conflicts.append(f"{relative}: result filename names a task absent from the accepted graph")
        if result.get("schema") != "ask-task-result/v2":
            conflicts.append(f"{relative}: unsupported TaskResult schema")
        if result.get("work_id") != work_id:
            conflicts.append(f"{relative}: TaskResult work_id mismatch")
        if result.get("task_id") != task_id:
            conflicts.append(f"{relative}: TaskResult task_id does not match its file name")
        base = result.get("base_sha")
        candidate = result.get("candidate_sha")
        if not isinstance(base, str) or not _commit_exists(root, base):
            conflicts.append(f"{relative}: TaskResult base_sha is missing from Git")
        if not isinstance(candidate, str) or not _commit_exists(root, candidate):
            conflicts.append(f"{relative}: TaskResult candidate_sha is missing from Git")
        if isinstance(base, str) and isinstance(candidate, str):
            if not _is_ancestor(root, base, candidate):
                conflicts.append(f"{relative}: candidate is outside the TaskResult base ancestry")
            if state is not None:
                task_state = (state.get("tasks") or {}).get(task_id)
                if task_state is None:
                    conflicts.append(f"{relative}: TaskResult task is absent from state.json")
                else:
                    recorded_base = task_state.get("base_sha") or ""
                    if recorded_base != base:
                        conflicts.append(f"{relative}: TaskResult base_sha conflicts with state.json")
                    selected_branch = task_state.get("task_branch") or ""
                    if selected_branch:
                        selected = _git(root, "rev-parse", "--verify", selected_branch + "^{commit}")
                        if selected.returncode or selected.stdout.strip() != candidate:
                            conflicts.append(f"{relative}: candidate differs from the selected task branch")
                        if not _is_ancestor(root, state.get("coordinator_sha") or "", candidate):
                            conflicts.append(f"{relative}: candidate is outside selected checkout ancestry")
                    elif task_state.get("status") == "running":
                        current = _git(root, "rev-parse", "--verify", "HEAD^{commit}")
                        if current.returncode or current.stdout.strip() != candidate:
                            conflicts.append(f"{relative}: candidate differs from the selected checkout HEAD")
        anchor, anchor_error = _accepted_anchor(root, work_id)
        if anchor_error:
            conflicts.append(anchor_error)
        elif "contract_sha" in result:
            contract_sha = result.get("contract_sha")
            if not isinstance(contract_sha, str) or not contract_sha:
                conflicts.append(f"{relative}: TaskResult contract_sha is invalid")
            elif contract_sha != anchor:
                conflicts.append(f"{relative}: TaskResult contract identity mismatch")
        elif isinstance(result.get("base_sha"), str):
            base_anchor, base_error = _accepted_anchor_at(root, work_id, result["base_sha"])
            if base_error:
                conflicts.append(f"{relative}: contract identity cannot be proven: {base_error}")
            elif base_anchor != anchor:
                conflicts.append(f"{relative}: accepted contract changed since TaskResult base_sha")
        else:
            conflicts.append(f"{relative}: contract identity cannot be proven without contract_sha")

        if state is None or not state_exists:
            task_ids.add(task_id)
            for review_path in _review_files(root, work_id, task_id):
                paths.add(review_path)
        elif task_id in (state.get("tasks") or {}):
            status = state["tasks"][task_id].get("status")
            if status in {"pending", "ready", "cancelled"}:
                conflicts.append(f"{relative}: execution evidence exists while task status is {status}")
            review = (state["tasks"][task_id].get("evidence") or {}).get("review") or {}
            if review:
                for key in ("work_id", "task_id", "base_sha"):
                    if review.get(key) != result.get(key):
                        conflicts.append(f"{relative}: recorded review identity conflicts with TaskResult")
                review_candidate = review.get("candidate_sha")
                result_candidate = result.get("candidate_sha")
                stale_review = (
                    status == "running"
                    and isinstance(review_candidate, str)
                    and isinstance(result_candidate, str)
                    and review_candidate != result_candidate
                    and _is_ancestor(root, review_candidate, result_candidate)
                )
                if review.get("candidate_sha") != result_candidate and not stale_review:
                    conflicts.append(f"{relative}: recorded review candidate conflicts with TaskResult")
                if (review.get("result_digest") != hashlib.sha256(raw).hexdigest()
                        and not stale_review):
                    conflicts.append(f"{relative}: recorded review result digest conflicts with TaskResult")

    if not state_exists and result_docs:
        conflicts.append("state.json is missing while retained task execution results exist")
        paths.add(str(state_path.relative_to(root)))
    if state is not None:
        running_tasks = [
            tasks[task_id]
            for task_id, task_state in (state.get("tasks") or {}).items()
            if task_state.get("status") == "running" and task_id in tasks
        ]
        running_paths = [
            str(pattern)
            for task in running_tasks
            for pattern in (task.get("owned_paths") or [])
        ]
        for task_id, task_state in (state.get("tasks") or {}).items():
            status = task_state.get("status")
            if status not in {"pending", "ready"}:
                continue
            task = tasks.get(task_id)
            if not task:
                continue
            base = state.get("coordinator_sha") or ""
            head_proc = _git(root, "rev-parse", "--verify", "HEAD^{commit}")
            head = head_proc.stdout.strip() if head_proc.returncode == 0 else ""
            changed = _owned_changes(root, task, base, head)
            # A dependent task may intentionally share files with its active
            # predecessor. Attribute those candidate changes to the running
            # task; unrelated changes remain unexplained and require recovery.
            changed = [
                name for name in changed
                if not any(fnmatch.fnmatchcase(name, pattern) for pattern in running_paths)
            ]
            if changed:
                task_ids.add(task_id)
                paths.update(changed)
                paths.add(str(state_path.relative_to(root)))
                conflicts.append(
                    f"task {task_id} is {status} but task-owned source changed after coordinator_sha: "
                    + ", ".join(changed)
                )

    if state is None and not state_exists and not result_docs:
        anchor, anchor_error = _accepted_anchor(root, work_id)
        if anchor_error:
            conflicts.append(anchor_error)
            paths.add(f"work/{work_id}/traceability-accepted.json")
        elif anchor:
            head_proc = _git(root, "rev-parse", "--verify", "HEAD^{commit}")
            head = head_proc.stdout.strip() if head_proc.returncode == 0 else ""
            if not head or not _is_ancestor(root, anchor, head):
                conflicts.append("accepted contract anchor is outside the selected checkout ancestry")
                paths.add(f"work/{work_id}/traceability-accepted.json")
            else:
                ready = next(
                    (task for task in (graph.get("tasks") or [])
                     if not (task.get("depends_on") or [])),
                    None,
                )
                if ready:
                    changed = _owned_changes(root, ready, anchor, head)
                    if changed:
                        task_id = str(ready["id"])
                        task_ids.add(task_id)
                        paths.update(changed)
                        paths.add(f"work/{work_id}/traceability-accepted.json")
                        conflicts.append(
                            f"task {task_id} has task-owned source changes after the accepted anchor "
                            "but no runtime attempt record: " + ", ".join(changed)
                        )

    if not conflicts:
        return None
    if not paths:
        paths.add(str(state_path.relative_to(root)))
    return _report(work_id, task_ids, paths, conflicts)


def require_safe(root: Path, work_id: str, graph: dict, state: dict | None = None) -> None:
    report = inspect(root, work_id, graph, state)
    if report is not None:
        raise RecoveryRequired(report)
