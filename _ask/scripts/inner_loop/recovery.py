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


def _json_at(root: Path, commit: str, name: str) -> dict | None:
    proc = _git(root, "show", f"{commit}:{name}")
    if proc.returncode:
        return None
    try:
        value = json.loads(proc.stdout)
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def _accepted_contract_documents(root: Path, work_id: str, pin: dict) -> dict | None:
    """Load and digest-check the exact spec, plan and graph named by a pin."""
    from inner_loop.yaml_lite import parse_yaml

    contract_sha = pin.get("contract_sha")
    if not isinstance(contract_sha, str) or not _commit_exists(root, contract_sha):
        return None
    prefix = f"work/{work_id}/"
    spec = _json_at(root, contract_sha, f"specs/current/{work_id}.json")
    plan = _json_at(root, contract_sha, prefix + "test-plan.json")
    graph_proc = _git(root, "show", f"{contract_sha}:{prefix}inner-loop/tasks.yaml")
    if spec is None or plan is None or graph_proc.returncode:
        return None
    try:
        graph = parse_yaml(graph_proc.stdout)
    except (ValueError, TypeError):
        return None
    canonical = {"spec": spec, "plan": plan, "graph": graph}
    for name, value in canonical.items():
        expected = pin.get(name + "_digest")
        actual = hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        if not isinstance(expected, str) or expected != actual:
            return None
    return canonical


def _scope_test_ids(plan: dict, task_id: str) -> set[str] | None:
    scopes = plan.get("task_scopes")
    if not isinstance(scopes, list):
        return None
    matches = [scope for scope in scopes
               if isinstance(scope, dict) and scope.get("task_id") == task_id]
    if len(matches) != 1 or not isinstance(matches[0].get("test_ids"), list):
        return None
    ids = matches[0]["test_ids"]
    return set(ids) if all(isinstance(item, str) for item in ids) else None


def _scope_compatible_result(root: Path, work_id: str, task_id: str,
                             result: dict, current_anchor: str,
                             state: dict | None) -> bool:
    """Prove an integrated result still covers an unchanged subset of its old scope."""
    task_state = ((state or {}).get("tasks") or {}).get(task_id) or {}
    if task_state.get("status") != "integrated":
        return False
    base = result.get("base_sha")
    old_anchor, error = _accepted_anchor_at(root, work_id, base) if isinstance(base, str) else (None, "")
    if error or old_anchor != result.get("contract_sha"):
        return False
    if not _is_ancestor(root, old_anchor or "", current_anchor):
        return False

    old_pin = _json_at(root, base, f"work/{work_id}/traceability-accepted.json")
    try:
        current_pin = json.loads(
            (root / "work" / work_id / "traceability-accepted.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError):
        return False
    if not isinstance(current_pin, dict):
        return False
    if not old_pin or not current_pin or current_pin.get("contract_sha") != current_anchor:
        return False
    previous = _accepted_contract_documents(root, work_id, old_pin)
    current = _accepted_contract_documents(root, work_id, current_pin)
    if previous is None or current is None:
        return False
    if previous["spec"] != current["spec"]:
        return False

    old_ids = _scope_test_ids(previous["plan"], task_id)
    current_ids = _scope_test_ids(current["plan"], task_id)
    if old_ids is None or current_ids is None or not current_ids.issubset(old_ids):
        return False
    old_tests = {item.get("id"): item for item in previous["plan"].get("tests", [])
                 if isinstance(item, dict) and isinstance(item.get("id"), str)}
    current_tests = {item.get("id"): item for item in current["plan"].get("tests", [])
                     if isinstance(item, dict) and isinstance(item.get("id"), str)}
    if any(current_tests.get(test_id) != old_tests.get(test_id) for test_id in current_ids):
        return False

    ledger = root / "work" / work_id / "traceability" / "executions.json"
    try:
        executions = json.loads(ledger.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    if not isinstance(executions, list):
        return False
    old_plan_digest = old_pin.get("plan_digest")
    old_scope = _scope_test_ids(previous["plan"], task_id)
    if old_scope is None or not old_scope:
        return False
    reports = root / "work" / work_id / "traceability" / "runs"
    for row in executions:
        if not (isinstance(row, dict)
                and row.get("scope") == "task"
                and row.get("task_id") == task_id
                and row.get("phase") == "final_green"
                and row.get("candidate_sha") == result.get("candidate_sha")
                and row.get("plan_digest") == old_plan_digest
                and row.get("spec_digest") == old_pin.get("spec_digest")):
            continue
        run_id = row.get("run_id")
        if not isinstance(run_id, str) or not run_id or "/" in run_id or "\\" in run_id:
            continue
        try:
            from inner_loop.checkpoint import CheckpointError, read_checkpoint
            checkpoint = read_checkpoint(root, work_id)
        except ImportError:
            return False
        except CheckpointError:
            return False
        if checkpoint is None or not _traceability_matches_checkpoint(
            root, work_id, checkpoint, expected_row=row, expected_run_id=run_id
        ):
            continue
        report_path = reports / run_id / "results.json"
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
            raw = json.dumps(report, sort_keys=True, separators=(",", ":")).encode()
        except (OSError, ValueError, TypeError):
            continue
        if (not isinstance(report, dict)
                or row.get("digest") != hashlib.sha256(raw).hexdigest()
                or report.get("schema") != "ask-test-results/v1"
                or report.get("run_id") != run_id
                or report.get("candidate_sha") != result.get("candidate_sha")
                or report.get("scope") != "task"
                or report.get("task_id") != task_id
                or report.get("plan_digest") != old_plan_digest
                or report.get("spec_digest") != old_pin.get("spec_digest")):
            continue
        if _valid_final_green_scope(report, previous["plan"], task_id,
                                    old_scope, result.get("candidate_sha")):
            return True
    return False


def _valid_final_green_scope(report: dict, plan: dict, task_id: str,
                             required_ids: set[str], candidate_sha: str) -> bool:
    """Check successful collection and exact one-to-one final case bindings."""
    tests = {item.get("id"): item for item in plan.get("tests", [])
             if isinstance(item, dict) and isinstance(item.get("id"), str)}
    if not required_ids or not required_ids.issubset(tests):
        return False
    expected = {test_id: tests[test_id] for test_id in required_ids}
    if any(test.get("task_id") != task_id or not isinstance(test.get("case_id"), str)
           or not isinstance(test.get("runner_id"), str) for test in expected.values()):
        return False

    runs = report.get("executions")
    cases = report.get("cases")
    if not isinstance(runs, list) or not runs or not isinstance(cases, list):
        return False
    by_id = {}
    for run in runs:
        if not isinstance(run, dict):
            return False
        run_id = run.get("id")
        if not isinstance(run_id, str) or not run_id or run_id in by_id:
            return False
        if (run.get("phase") != "final_green" or run.get("collection_status") != "ok"
                or type(run.get("exit_code")) is not int or run.get("exit_code") != 0
                or not isinstance(run.get("runner_id"), str)
                or run.get("source_sha") != candidate_sha):
            return False
        by_id[run_id] = run

    seen_tests = set()
    seen_cases = set()
    used_executions = set()
    for case in cases:
        if not isinstance(case, dict):
            return False
        test_id = case.get("test_id")
        test = expected.get(test_id)
        if test is None or test_id in seen_tests:
            return False
        identity = (case.get("runner_id"), case.get("case_id"))
        if identity in seen_cases or identity != (test.get("runner_id"), test.get("case_id")):
            return False
        execution = by_id.get(case.get("execution_id"))
        if (execution is None or execution.get("runner_id") != test.get("runner_id")
                or case.get("phase") != "final_green" or case.get("outcome") != "passed"
                or case.get("source_sha") != candidate_sha):
            return False
        seen_tests.add(test_id)
        seen_cases.add(identity)
        used_executions.add(case["execution_id"])
    return seen_tests == required_ids and used_executions == set(by_id)


def _traceability_matches_checkpoint(root: Path, work_id: str,
                                     checkpoint: tuple[str, dict, dict[str, bytes]], *,
                                     expected_row: dict | None = None,
                                     expected_run_id: str | None = None) -> bool:
    """Preserve checkpointed evidence exactly while allowing append-only runs."""
    prefix = f"work/{work_id}/traceability/"
    retained = {name[len("artifacts/"):]: content
                for name, content in checkpoint[2].items()
                if name.startswith("artifacts/" + prefix)}
    directory = root / "work" / work_id / "traceability"
    live = {}
    if directory.is_dir():
        for path in directory.rglob("*"):
            if path.is_symlink():
                return False
            if path.is_file():
                live[path.relative_to(root).as_posix()] = path.read_bytes()
    ledger_path = prefix + "executions.json"
    retained_ledger = retained.get(ledger_path)
    live_ledger = live.get(ledger_path)
    try:
        old_rows = json.loads(retained_ledger) if retained_ledger is not None else []
        current_rows = json.loads(live_ledger) if live_ledger is not None else []
    except (UnicodeDecodeError, ValueError):
        return False
    if (not isinstance(old_rows, list) or not isinstance(current_rows, list)
            or current_rows[:len(old_rows)] != old_rows):
        return False
    if expected_row is not None and expected_row not in old_rows:
        return False
    for name, content in retained.items():
        if name == ledger_path:
            continue
        if live.get(name) != content:
            return False
    allowed_new = {ledger_path}
    for name in live.keys() - retained.keys():
        relative = name[len(prefix):] if name.startswith(prefix) else ""
        parts = relative.split("/") if relative else []
        if name == prefix + "executions.lock":
            allowed_new.add(name)
            continue
        if (len(parts) == 3 and parts[0] == "runs"
                and parts[1] and all(char.isalnum() or char in "-_" for char in parts[1])
                and (parts[2] == "results.json" or parts[2].endswith((".json", ".log")))):
            allowed_new.add(name)
            continue
        return False
    if expected_run_id is not None:
        report_name = prefix + f"runs/{expected_run_id}/results.json"
        if report_name not in retained or live.get(report_name) != retained[report_name]:
            return False
    return set(live) - set(retained) <= allowed_new


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


def _depends_on(tasks: dict[str, dict], task_id: str, prerequisite: str) -> bool:
    seen: set[str] = set()
    pending = [task_id]
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        task = tasks.get(current) or {}
        dependencies = task.get("depends_on") or []
        if prerequisite in {str(item) for item in dependencies}:
            return True
        pending.extend(str(item) for item in dependencies)
    return False


def _interrupted_paths(root: Path, work_id: str, tasks: dict[str, dict], state: dict,
                       head: str, target_task_id: str) -> set[str]:
    """Return candidate paths safely attributable to interrupted prerequisites."""
    coordinator = state.get("coordinator_sha") or ""
    target = tasks.get(target_task_id) or {}
    target_patterns = [str(pattern) for pattern in target.get("owned_paths") or []]
    owned: set[str] = set()
    for interrupted_id, task_state in (state.get("tasks") or {}).items():
        if task_state.get("status") != "interrupted" or not _depends_on(tasks, target_task_id, interrupted_id):
            continue
        history = task_state.get("attempt_history") or []
        if not history:
            continue
        attempt = history[-1]
        base = attempt.get("base_sha") or ""
        candidate = attempt.get("interrupted_candidate_sha") or ""
        if (attempt.get("status") != "interrupted" or base != coordinator
                or not _commit_exists(root, candidate)
                or not _is_ancestor(root, base, candidate)
                or not _is_ancestor(root, candidate, head)):
            continue
        interrupted = tasks.get(interrupted_id) or {}
        interrupted_patterns = [str(pattern) for pattern in interrupted.get("owned_paths") or []]
        at_candidate = set(_changed_paths(root, base, candidate))
        after_candidate = set(_changed_paths(root, candidate, head))
        for name in at_candidate - after_candidate:
            if (any(fnmatch.fnmatchcase(name, pattern) for pattern in interrupted_patterns)
                    and any(fnmatch.fnmatchcase(name, pattern) for pattern in target_patterns)):
                owned.add(name)
    return owned


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

    checkpoint = None
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
        try:
            from inner_loop.checkpoint import CheckpointError, read_checkpoint
        except ImportError:
            checkpoint = None
        else:
            try:
                checkpoint = read_checkpoint(root, work_id)
            except CheckpointError as exc:
                checkpoint = None
                conflicts.append(f"checkpoint is invalid: {exc}")
                paths.add(str(state_path.relative_to(root)))
        if checkpoint is not None and checkpoint[1] != state:
            conflicts.append("state.json is newer or divergent from the retained checkpoint")
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
            elif contract_sha != anchor and not _scope_compatible_result(
                root, work_id, task_id, result, anchor or "", state
            ):
                conflicts.append(f"{relative}: TaskResult contract identity mismatch")
                if checkpoint is not None and not _traceability_matches_checkpoint(root, work_id, checkpoint):
                    conflicts.append("runtime traceability evidence differs from the retained checkpoint")
                    paths.add(str((root / "work" / work_id / "traceability").relative_to(root)))
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
            attributed = _interrupted_paths(root, work_id, tasks, state, head, task_id)
            changed = [name for name in changed if name not in attributed]
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
