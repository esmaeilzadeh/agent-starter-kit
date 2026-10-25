"""Work-ID-scoped reconciliation before state initialization or writer admission."""
from __future__ import annotations

import ast
import fnmatch
import hashlib
import json
from pathlib import Path
import re
import subprocess


class RecoveryRequired(RuntimeError):
    """The runtime history cannot safely authorize a new or resumed attempt."""

    def __init__(self, report: dict):
        super().__init__("recovery_required")
        self.report = report


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def _git_bytes(root: Path, *args: str) -> bytes | None:
    proc = subprocess.run(["git", *args], cwd=root, capture_output=True)
    return proc.stdout if proc.returncode == 0 else None


def _historical_runner_identity(root: Path, candidate_sha: str) -> dict | None:
    init_path = ".agents/ask/verification/traceability/__init__.py"
    runner_path = ".agents/ask/verification/traceability/unittest_runner.py"
    init_bytes = _git_bytes(root, "show", f"{candidate_sha}:{init_path}")
    runner_bytes = _git_bytes(root, "show", f"{candidate_sha}:{runner_path}")
    if init_bytes is None or runner_bytes is None:
        return None
    try:
        module = ast.parse(init_bytes.decode("utf-8"))
    except (UnicodeDecodeError, SyntaxError):
        return None
    capability = None
    for statement in module.body:
        targets = ([statement.target] if isinstance(statement, ast.AnnAssign)
                   else statement.targets if isinstance(statement, ast.Assign) else [])
        if any(isinstance(target, ast.Name) and target.id == "CAPABILITY" for target in targets):
            value = statement.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                capability = value.value
                break
    if not capability:
        return None
    return {"capability": capability,
            "adapter_digest": hashlib.sha256(runner_bytes).hexdigest()}


def _historical_file_digest(root: Path, candidate_sha: str, name: str) -> str | None:
    if (not isinstance(name, str) or not name or "\\" in name
            or Path(name).is_absolute() or ".." in Path(name).parts):
        return None
    content = _git_bytes(root, "show", f"{candidate_sha}:{name}")
    return hashlib.sha256(content).hexdigest() if content is not None else None


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


def _checkpoint_artifact_with_digest(root: Path, work_id: str,
                                     checkpoint: tuple[str, dict, dict[str, bytes]] | None,
                                     relative: str, expected_digest: str) -> bytes | None:
    """Find exact artifact bytes in the authenticated checkpoint ancestry."""
    from inner_loop.checkpoint import read_checkpoint

    current = checkpoint or read_checkpoint(root, work_id)
    seen: set[str] = set()
    artifact_key = "artifacts/" + relative
    while current is not None:
        commit = current[0]
        if commit in seen:
            return None
        seen.add(commit)
        content = current[2].get(artifact_key)
        if (isinstance(content, bytes)
                and hashlib.sha256(content).hexdigest() == expected_digest):
            return content
        raw_manifest = _git_bytes(root, "show", f"{commit}:checkpoint.json")
        try:
            manifest = json.loads(raw_manifest) if raw_manifest is not None else None
        except (UnicodeDecodeError, ValueError):
            return None
        if not isinstance(manifest, dict) or manifest.get("work_id") != work_id:
            return None
        previous = manifest.get("previous_checkpoint")
        if previous is None:
            return None
        if not isinstance(previous, str):
            return None
        try:
            current = read_checkpoint(root, work_id, previous)
        except (OSError, ValueError, RuntimeError):
            return None
    return None


def _checkpointed_verification(root: Path, work_id: str, state: dict | None,
                               checkpoint: tuple[str, dict, dict[str, bytes]] | None = None) -> dict | None:
    """Return a passing verifier receipt whose bytes are bound to retained state."""
    retained = checkpoint[2] if checkpoint is not None else {}

    def retained_or_live(relative: str) -> bytes:
        checkpoint_key = "artifacts/" + relative
        if checkpoint_key in retained:
            return retained[checkpoint_key]
        return (root / relative).read_bytes()

    for task_id, task in ((state or {}).get("tasks") or {}).items():
        evidence = task.get("evidence") or {}
        verification = evidence.get("verification")
        record_digest = evidence.get("verification_record_digest")
        if (not isinstance(verification, dict) or verification.get("result") != "pass"
                or verification.get("work_id") != work_id
                or verification.get("task_id") != task_id):
            continue
        try:
            result_relative = f"work/{work_id}/inner-loop/results/{task_id}.json"
            result_raw = retained_or_live(result_relative)
            result = json.loads(result_raw)
        except (OSError, ValueError):
            continue
        if (not isinstance(result, dict)
                or verification.get("base_sha") != result.get("base_sha")
                or verification.get("candidate_sha") != result.get("candidate_sha")
                or verification.get("result_digest") != hashlib.sha256(result_raw).hexdigest()):
            continue
        record_path = verification.get("record_path")
        if not isinstance(record_path, str):
            continue
        try:
            raw = retained_or_live(record_path)
            if (not isinstance(record_digest, str)
                    or hashlib.sha256(raw).hexdigest() != record_digest
                    or json.loads(raw) != verification):
                continue
            completion_path = f"work/{work_id}/traceability/completion.json"
            completion = retained_or_live(completion_path)
            expected_completion_digest = verification.get("completion_digest")
            if (hashlib.sha256(completion).hexdigest() != expected_completion_digest
                    and isinstance(expected_completion_digest, str)):
                completion = _checkpoint_artifact_with_digest(
                    root, work_id, checkpoint, completion_path, expected_completion_digest,
                )
                if completion is None:
                    continue
            static = retained_or_live(
                f"work/{work_id}/traceability/static-{verification['candidate_sha']}.json")
        except (KeyError, OSError, ValueError):
            continue
        if (hashlib.sha256(completion).hexdigest() == verification.get("completion_digest")
                and hashlib.sha256(static).hexdigest() == verification.get("static_receipt_digest")):
            return verification
    return None


def _scope_compatible_result(root: Path, work_id: str, task_id: str,
                             result: dict, current_anchor: str,
                             state: dict | None) -> bool:
    """Prove an integrated result still covers an unchanged subset of its old scope."""
    task_state = ((state or {}).get("tasks") or {}).get(task_id) or {}
    if task_state.get("status") != "integrated":
        return False
    base = result.get("base_sha")
    old_anchor, error = _accepted_anchor_at(root, work_id, base) if isinstance(base, str) else (None, "")
    contract_sha = result.get("contract_sha")
    candidate_sha = result.get("candidate_sha")
    if error or not isinstance(contract_sha, str) or not isinstance(candidate_sha, str):
        return False
    if old_anchor != contract_sha:
        # A coordinator may accept a reviewed contract amendment after task
        # start. In that case the immutable result candidate carries the pin
        # actually used for its runs; validate that exact contract and bound
        # it between the original task base and candidate.
        if (not old_anchor or not _is_ancestor(root, old_anchor, contract_sha)
                or not _is_ancestor(root, contract_sha, candidate_sha)):
            return False
        old_pin = _json_at(root, candidate_sha, f"work/{work_id}/traceability-accepted.json")
        if not isinstance(old_pin, dict) or old_pin.get("contract_sha") != contract_sha:
            return False
        old_anchor = contract_sha
    else:
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
    review = current_pin.get("plan_review")
    contract_source = current_pin.get("contract_source_sha")
    if not isinstance(contract_source, str) and isinstance(review, dict):
        contract_source = review.get("contract_source_sha")
    if not isinstance(contract_source, str):
        # The normal accept-plan record pins the reviewed contract source in
        # contract_sha. Older authority formats may keep it in the review.
        contract_source = current_pin.get("contract_sha")
    review_digest = hashlib.sha256(json.dumps(
        review, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest() if isinstance(review, dict) else None
    if (not isinstance(review, dict)
            or current_pin.get("plan_review_digest") != review_digest
            or review.get("decision") != "APPROVED"
            or review.get("reviewer") != current_pin.get("reviewer")
            or current_pin.get("reviewer") == current_pin.get("recorded_by")
            or review.get("spec_digest") != current_pin.get("spec_digest")
            or review.get("plan_digest") != current_pin.get("plan_digest")):
        return False
    # Acceptance authority commits are immutable records and may intentionally
    # have no Git parents. Scope carry-forward follows the bound contract
    # source, whose ancestry proves how the accepted documents evolved.
    if (not isinstance(contract_source, str)
            or not _commit_exists(root, contract_source)
            or not _is_ancestor(root, old_anchor or "", contract_source)):
        return False
    previous = _accepted_contract_documents(root, work_id, old_pin)
    current = _accepted_contract_documents(root, work_id, current_pin)
    source_pin = dict(current_pin, contract_sha=contract_source)
    source = _accepted_contract_documents(root, work_id, source_pin)
    if previous is None or current is None or source is None or source != current:
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
        if checkpoint is None:
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
        runs = report.get("executions")
        output_artifacts = ([run.get("output_artifact") for run in runs]
                            if isinstance(runs, list) and all(isinstance(run, dict) for run in runs)
                            else None)
        if output_artifacts is None or not _traceability_matches_checkpoint(
            root, work_id, checkpoint, expected_row=row, expected_run_id=run_id,
            expected_artifacts=output_artifacts,
            expected_verification=_checkpointed_verification(root, work_id, state, checkpoint),
        ):
            continue
        if _valid_final_green_scope(root, work_id, report, previous["plan"], task_id,
                                    old_scope, result.get("candidate_sha")):
            return True
    return False


def _valid_final_green_scope(root: Path, work_id: str, report: dict, plan: dict, task_id: str,
                             required_ids: set[str], candidate_sha: str) -> bool:
    """Check historical runner, output, source and exact final case bindings."""
    if report.get("runner_identity") != _historical_runner_identity(root, candidate_sha):
        return False
    tests = {item.get("id"): item for item in plan.get("tests", [])
             if isinstance(item, dict) and isinstance(item.get("id"), str)}
    if not required_ids or not required_ids.issubset(tests):
        return False
    expected = {test_id: tests[test_id] for test_id in required_ids}
    if any(test.get("task_id") != task_id or not isinstance(test.get("case_id"), str)
           or not isinstance(test.get("runner_id"), str) for test in expected.values()):
        return False
    runner_configs = {}
    runners = plan.get("runners")
    if not isinstance(runners, list):
        return False
    for runner in runners:
        if not isinstance(runner, dict) or not isinstance(runner.get("id"), str):
            return False
        if runner["id"] in runner_configs:
            return False
        runner_configs[runner["id"]] = runner
    if any(test.get("runner_id") not in runner_configs for test in expected.values()):
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
        runner = runner_configs.get(run.get("runner_id"))
        if (run.get("phase") != "final_green" or run.get("collection_status") != "ok"
                or type(run.get("exit_code")) is not int or run.get("exit_code") != 0
                or not isinstance(run.get("runner_id"), str)
                or run.get("source_sha") != candidate_sha or runner is None
                or run.get("argv") != runner.get("argv")
                or run.get("adapter") != runner.get("adapter")
                or not _valid_historical_output(root, work_id, report.get("run_id"), run)):
            return False
        by_id[run_id] = run

    seen_tests = set()
    seen_cases = set()
    used_executions = set()
    cases_by_execution = {run_id: set() for run_id in by_id}
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
                or case.get("source_sha") != candidate_sha
                or case.get("output_artifact") != execution.get("output_artifact")
                or case.get("output_digest") != execution.get("output_digest")):
            return False
        source_paths = test.get("source_paths")
        if not isinstance(source_paths, list) or any(not isinstance(path, str) for path in source_paths):
            return False
        expected_sources = {path: _historical_file_digest(root, candidate_sha, path)
                            for path in source_paths}
        if (any(digest is None for digest in expected_sources.values())
                or case.get("source_digests") != expected_sources):
            return False
        seen_tests.add(test_id)
        seen_cases.add(identity)
        used_executions.add(case["execution_id"])
        cases_by_execution[case["execution_id"]].add(case["case_id"])
    if seen_tests != required_ids or used_executions != set(by_id):
        return False
    for run_id, run in by_id.items():
        planned = {test["case_id"] for test in expected.values()
                   if test.get("runner_id") == run.get("runner_id")}
        if not planned or cases_by_execution[run_id] != planned:
            return False
    return True


def _valid_historical_output(root: Path, work_id: str, run_id: str, execution: dict) -> bool:
    relative = execution.get("output_artifact")
    prefix = f"work/{work_id}/traceability/runs/{run_id}/"
    if (not isinstance(relative, str) or not relative.startswith(prefix)
            or "\\" in relative or ".." in Path(relative).parts):
        return False
    path = root / relative
    run_directory = root / "work" / work_id / "traceability" / "runs" / run_id
    try:
        if path.is_symlink() or not path.resolve().is_relative_to(run_directory.resolve()):
            return False
        content = path.read_bytes()
    except OSError:
        return False
    return execution.get("output_digest") == hashlib.sha256(content).hexdigest()


def _traceability_matches_checkpoint(root: Path, work_id: str,
                                     checkpoint: tuple[str, dict, dict[str, bytes]], *,
                                     expected_row: dict | None = None,
                                     expected_run_id: str | None = None,
                                     expected_artifacts: list[str] | None = None,
                                     expected_verification: dict | None = None) -> bool:
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
    verified_replacements = {}
    if expected_verification is not None:
        candidate = expected_verification.get("candidate_sha")
        completion_digest = expected_verification.get("completion_digest")
        static_digest = expected_verification.get("static_receipt_digest")
        if (not isinstance(candidate, str) or not isinstance(completion_digest, str)
                or not isinstance(static_digest, str)):
            return False
        verified_replacements = {
            prefix + f"static-{candidate}.json": static_digest,
        }
    for name, content in retained.items():
        if name == ledger_path:
            continue
        # The completion report is a current projection. Its historical bytes
        # are authenticated above from the retained checkpoint, so later
        # verification may legitimately replace this live projection.
        if name == prefix + "completion.json":
            if name not in live:
                return False
            try:
                if not isinstance(json.loads(live[name]), dict):
                    return False
            except (UnicodeDecodeError, ValueError):
                return False
            continue
        expected_digest = verified_replacements.get(name)
        if live.get(name) != content and (expected_digest is None
                                          or hashlib.sha256(live.get(name, b"")).hexdigest() != expected_digest):
            return False
    allowed_new = {ledger_path}
    for name in live.keys() - retained.keys():
        relative = name[len(prefix):] if name.startswith(prefix) else ""
        parts = relative.split("/") if relative else []
        if name == prefix + "executions.lock":
            allowed_new.add(name)
            continue
        if (name in verified_replacements
                and hashlib.sha256(live[name]).hexdigest() == verified_replacements[name]):
            allowed_new.add(name)
            continue
        if (len(parts) == 3 and parts[0] == "runs"
                and parts[1] and all(char.isalnum() or char in "-_" for char in parts[1])
                and (parts[2] == "results.json" or parts[2].endswith((".json", ".log")))):
            allowed_new.add(name)
            continue
        if (len(parts) == 1 and parts[0].startswith(
                ("static-", "verification-", "review-input", "plan-review-"))
                and parts[0].endswith(".json")):
            allowed_new.add(name)
            continue
        if (len(parts) == 1 and parts[0].startswith("plan-review-")
                and parts[0].endswith(".md")):
            allowed_new.add(name)
            continue
        if (len(parts) == 2 and parts[0] in {"reviews", "static-runs"}
                and all(part and all(char.isalnum() or char in "-_." for char in part)
                        for part in parts)
                and parts[1].endswith((".json", ".log"))):
            allowed_new.add(name)
            continue
        if (len(parts) == 3 and parts[0] == "static-runs" and parts[1]
                and all(char.isalnum() or char in "-_." for char in parts[1])
                and parts[2].endswith((".json", ".log"))):
            allowed_new.add(name)
            continue
        return False
    if expected_run_id is not None:
        report_name = prefix + f"runs/{expected_run_id}/results.json"
        if report_name not in retained or live.get(report_name) != retained[report_name]:
            return False
    if expected_artifacts is not None:
        if any(not isinstance(name, str) or name not in retained or live.get(name) != retained[name]
               for name in expected_artifacts):
            return False
    if expected_verification is not None:
        if any(name not in live or hashlib.sha256(live[name]).hexdigest() != expected
               for name, expected in verified_replacements.items()):
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


def inspect(root: Path, work_id: str, graph: dict, state: dict | None = None,
            *, allowed_source_paths: set[str] | None = None) -> dict | None:
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
            if allowed_source_paths:
                changed = [name for name in changed if name not in allowed_source_paths]
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


def require_safe(root: Path, work_id: str, graph: dict, state: dict | None = None,
                 *, allowed_source_paths: set[str] | None = None) -> None:
    report = inspect(root, work_id, graph, state, allowed_source_paths=allowed_source_paths)
    if report is not None:
        raise RecoveryRequired(report)


def _legacy_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _legacy_ref_bytes(root: Path, commit: str, path: str) -> bytes | None:
    if (not path or "\\" in path or Path(path).is_absolute()
            or ".." in Path(path).parts):
        return None
    return _git_bytes(root, "show", f"{commit}:{path}")


def _legacy_artifact(root: Path, commit: str, path: str) -> tuple[bytes | None, str]:
    """Read a pinned artifact first, then expose a checkout-only copy as such."""
    if (not path or "\\" in path or Path(path).is_absolute()
            or ".." in Path(path).parts):
        return None, "missing"
    pinned = _legacy_ref_bytes(root, commit, path)
    if pinned is not None:
        return pinned, "product_ref"
    try:
        checkout_path = (root / path).resolve()
        if not checkout_path.is_relative_to(root.resolve()):
            return None, "missing"
        return checkout_path.read_bytes(), "checkout_only"
    except (OSError, RuntimeError):
        return None, "missing"


def _legacy_json(raw: bytes | None) -> dict | None:
    if raw is None:
        return None
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _legacy_run_id(record: dict | None) -> str | None:
    if not isinstance(record, dict):
        return None
    run_id = record.get("run_id")
    if isinstance(run_id, str) and re.fullmatch(r"[A-Za-z0-9_-]{8,64}", run_id):
        return run_id
    command = record.get("command")
    match = re.search(r"\brun_id=([A-Za-z0-9_-]{8,64})\b", command) if isinstance(command, str) else None
    return match.group(1) if match else None


def _legacy_run_candidate(record: dict | None, fallback: str) -> str:
    if not isinstance(record, dict):
        return fallback
    candidate = record.get("candidate_sha")
    if isinstance(candidate, str) and candidate:
        return candidate
    command = record.get("command")
    match = re.search(r"--candidate-sha\s+([0-9a-f]{40,64})", command) if isinstance(command, str) else None
    return match.group(1) if match else fallback


def _legacy_run_evidence(root: Path, commit: str, work_id: str, task_id: str,
                          phase: str, candidate_sha: str, run_id: str | None,
                          result_source: str) -> dict:
    if not run_id:
        return {"status": "missing", "run_id": None}
    ledger_path = f"work/{work_id}/traceability/executions.json"
    report_path = f"work/{work_id}/traceability/runs/{run_id}/results.json"
    ledger_raw, ledger_source = _legacy_artifact(root, commit, ledger_path)
    report_raw, report_source = _legacy_artifact(root, commit, report_path)
    ledger = None
    if ledger_raw is not None:
        try:
            ledger = json.loads(ledger_raw)
        except (UnicodeDecodeError, ValueError):
            ledger = None
    rows = [row for row in ledger if isinstance(row, dict) and row.get("run_id") == run_id] \
        if isinstance(ledger, list) else []
    row = rows[0] if len(rows) == 1 else None
    report = _legacy_json(report_raw)
    identity_ok = bool(
        row and report
        and row.get("task_id") == task_id
        and row.get("phase") == phase
        and row.get("candidate_sha") == candidate_sha
        and row.get("digest") == _legacy_digest(report)
        and report.get("run_id") == run_id
        and report.get("task_id") == task_id
        and report.get("candidate_sha") == candidate_sha
        and isinstance(report.get("cases"), list)
    )
    cases = report.get("cases") if report else []
    if phase == "red":
        outcome_ok = any(case.get("outcome") == "failed"
                         and case.get("failure_kind") == "behavior_assertion"
                         for case in cases if isinstance(case, dict))
    else:
        outcome_ok = bool(cases) and all(
            case.get("outcome") in {"passed", "pass"}
            for case in cases if isinstance(case, dict)
        ) and all(isinstance(case, dict) for case in cases)
    if not identity_ok or not outcome_ok:
        status = "unverified" if row is not None or report_raw is not None else "missing"
    elif result_source == ledger_source == report_source == "product_ref":
        status = "verified"
    else:
        status = "available_checkout_only"
    return {
        "status": status,
        "run_id": run_id,
        "candidate_sha": candidate_sha,
        "ledger_path": ledger_path,
        "ledger_source": ledger_source,
        "ledger_sha256": hashlib.sha256(ledger_raw).hexdigest() if ledger_raw is not None else None,
        "report_path": report_path,
        "report_source": report_source,
        "report_sha256": hashlib.sha256(report_raw).hexdigest() if report_raw is not None else None,
        "identity_matches": identity_ok,
        "outcome_matches": outcome_ok,
    }


def _legacy_verifier_snapshot(root: Path, commit_sha: str | None) -> dict:
    paths = (
        ".agents/ask/verification/traceability/__init__.py",
        ".agents/ask/verification/traceability/unittest_runner.py",
        ".agents/ask/verification/traceability/adapters.py",
        ".agents/ask/verification/traceability/contracts.py",
        ".agents/ask/verification/traceability/coverage.py",
        ".agents/ask/verification/traceability/evidence.py",
        ".agents/ask/verification/traceability/service.py",
        ".agents/ask/verification/traceability/completion.py",
        ".agents/ask/verification/traceability/cli.py",
        ".agents/ask/verification/run.py",
    )
    if not commit_sha or not _commit_exists(root, commit_sha):
        return {"commit": commit_sha, "status": "missing_commit", "files": {},
                "missing": list(paths), "source_sha256": None}
    files = {}
    missing = []
    for path in paths:
        raw = _legacy_ref_bytes(root, commit_sha, path)
        if raw is None:
            missing.append(path)
        else:
            files[path] = hashlib.sha256(raw).hexdigest()
    identity = _historical_runner_identity(root, commit_sha)
    return {
        "commit": commit_sha,
        "status": "complete" if not missing else "incomplete",
        "capability": identity.get("capability") if identity else None,
        "unittest_adapter_sha256": identity.get("adapter_digest") if identity else None,
        "files": files,
        "missing": missing,
        "source_sha256": _legacy_digest(files) if files else None,
    }


def audit_legacy_workstream(root: Path, work_id: str, product_ref: str) -> dict:
    """Inventory a pre-checkpoint workstream without changing it or admitting work."""
    root = Path(root).resolve()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", work_id):
        raise ValueError("legacy work_id has an unsupported form")
    if not (re.fullmatch(r"refs/(?:heads|tags)/[A-Za-z0-9._/-]+", product_ref)
            or re.fullmatch(r"[0-9a-f]{40,64}", product_ref)):
        raise ValueError("product ref must be a full branch/tag ref or commit SHA")
    if product_ref.startswith("refs/") and _git(root, "check-ref-format", product_ref).returncode:
        raise ValueError("product ref has an invalid Git ref format")
    ref = _git(root, "rev-parse", "--verify", product_ref + "^{commit}")
    if ref.returncode:
        raise ValueError(f"product ref is unavailable: {product_ref}")
    commit = ref.stdout.strip()
    state_path = f"work/{work_id}/inner-loop/state.json"
    state_raw = _legacy_ref_bytes(root, commit, state_path)
    state = _legacy_json(state_raw)
    if state_raw is None or state is None or state.get("work_id") != work_id:
        raise ValueError(f"{state_path} is missing or invalid at {product_ref}")

    pin_path = f"work/{work_id}/traceability-accepted.json"
    pin_raw = _legacy_ref_bytes(root, commit, pin_path)
    pin = _legacy_json(pin_raw)
    authority_ref = f"refs/ask/accepted-tests/{work_id}"
    authority_proc = _git(root, "rev-parse", "--verify", authority_ref)
    authority_sha = authority_proc.stdout.strip() if authority_proc.returncode == 0 else ""
    authority_raw = _git_bytes(root, "show", f"{authority_sha}:accepted.json") if authority_sha else None
    authority = _legacy_json(authority_raw)
    identity_keys = ("contract_sha", "spec_digest", "plan_digest", "graph_digest")
    identity_differences = [key for key in identity_keys
                            if (pin or {}).get(key) != (authority or {}).get(key)]
    authority_review = (authority or {}).get("plan_review") or {}
    model_policy_path = f"work/{work_id}/models.yaml"
    model_policy_raw = _legacy_ref_bytes(root, commit, model_policy_path)
    verifier_snapshots = {
        "tracked_pin_contract": _legacy_verifier_snapshot(root, (pin or {}).get("contract_sha")),
        "accepted_authority_contract": _legacy_verifier_snapshot(
            root, (authority or {}).get("contract_sha")),
    }
    conflicts: list[str] = []
    active_tasks = [task_id for task_id, task in (state.get("tasks") or {}).items()
                    if isinstance(task, dict) and task.get("status") == "running"]
    if active_tasks:
        conflicts.append("legacy state has active writers: " + ", ".join(sorted(active_tasks)))
    if not pin or pin.get("schema") != "ask-accepted-tests/v1":
        conflicts.append("tracked accepted pin has an unsupported or missing schema")
    if state.get("schema") != "ask-inner-loop-state/v1":
        conflicts.append("legacy state has an unsupported or missing schema")
    if not authority or authority.get("schema") != "ask-accepted-tests/v1":
        conflicts.append("accepted-tests authority has an unsupported or missing schema")
    if authority and authority.get("capability") != "ask-traceability/v1":
        conflicts.append("accepted-tests authority names an unsupported verifier capability")
    if identity_differences:
        conflicts.append("tracked accepted pin differs from accepted-tests authority: "
                         + ", ".join(identity_differences))

    ledger_path = f"work/{work_id}/traceability/executions.json"
    ledger_raw, ledger_source = _legacy_artifact(root, commit, ledger_path)
    try:
        ledger = json.loads(ledger_raw) if ledger_raw is not None else []
    except (UnicodeDecodeError, ValueError):
        ledger = None
    ledger_rows = ledger if isinstance(ledger, list) else []
    tasks: list[dict] = []
    for number in range(1, 6):
        task_id = str(number)
        task_state = (state.get("tasks") or {}).get(task_id)
        if not isinstance(task_state, dict):
            task_state = None
        result_path = f"work/{work_id}/inner-loop/results/{task_id}.json"
        result_raw, result_source = _legacy_artifact(root, commit, result_path)
        result = _legacy_json(result_raw)
        result_sha = hashlib.sha256(result_raw).hexdigest() if result_raw is not None else None
        result_valid = bool(result and result.get("schema") == "ask-task-result/v2"
                            and result.get("work_id") == work_id
                            and result.get("task_id") == task_id)
        base_sha = result.get("base_sha") if result_valid else (task_state or {}).get("base_sha")
        candidate_sha = result.get("candidate_sha") if result_valid else None
        ancestry_ok = bool(base_sha and candidate_sha
                           and _commit_exists(root, base_sha)
                           and _commit_exists(root, candidate_sha)
                           and _is_ancestor(root, base_sha, candidate_sha))
        task_conflicts: list[str] = []
        if result_valid and task_state and task_state.get("base_sha") and task_state["base_sha"] != base_sha:
            task_conflicts.append("TaskResult base differs from legacy state")
        if result_valid and task_state and task_state.get("result_path") != result_path:
            task_conflicts.append("TaskResult exists outside the state result_path")
        if result_valid and not ancestry_ok:
            task_conflicts.append("TaskResult base/candidate ancestry is unavailable")
        candidate_in_product_ref = bool(candidate_sha and _is_ancestor(root, candidate_sha, commit))
        if result_valid and not candidate_in_product_ref:
            task_conflicts.append("TaskResult candidate is not in the product ref ancestry")
        tdd = (result.get("tdd") or {}) if result_valid else {}
        red_candidate = _legacy_run_candidate(tdd.get("red"), candidate_sha or "")
        green_candidate = _legacy_run_candidate(tdd.get("green"), candidate_sha or "")
        red = _legacy_run_evidence(root, commit, work_id, task_id, "red", red_candidate,
                                   _legacy_run_id(tdd.get("red")), result_source)
        green = _legacy_run_evidence(root, commit, work_id, task_id, "final_green", green_candidate,
                                     _legacy_run_id(tdd.get("green")), result_source)
        refactor = result.get("refactor") if result_valid else None
        refactor_ok = bool(isinstance(refactor, dict)
                           and refactor.get("status") in {"pass", "passed"}
                           and refactor.get("candidate_sha") == candidate_sha)
        state_evidence = (task_state or {}).get("evidence") or {}
        review = state_evidence.get("review") or {}
        review_path = review.get("evidence") if isinstance(review, dict) else None
        review_raw, review_source = (
            _legacy_artifact(root, commit, review_path)
            if isinstance(review_path, str) and review_path.startswith(
                f"work/{work_id}/inner-loop/evidence/"
            ) else (None, "missing")
        )
        review_doc = _legacy_json(review_raw)
        review_digest = hashlib.sha256(review_raw).hexdigest() if review_raw is not None else None
        review_evidence_ok = bool(
            result_valid and review_doc
            and review.get("work_id") == work_id
            and review.get("task_id") == task_id
            and review.get("base_sha") == base_sha
            and review.get("candidate_sha") == candidate_sha
            and review.get("result_digest") == result_sha
            and review.get("verdict") == "APPROVED"
            and isinstance(review.get("reviewer"), str)
            and bool(review["reviewer"].strip())
            and review.get("evidence_digest") == review_digest
            and review_doc.get("reviewer") == review.get("reviewer")
            and review_doc.get("decision") == "APPROVED"
            and review_doc.get("base_sha") == base_sha
            and review_doc.get("candidate_sha") == candidate_sha
        )
        if review_evidence_ok and result_source == review_source == "product_ref":
            review_status = "independence_unverifiable"
        elif review_evidence_ok:
            review_status = "available_checkout_only"
        elif review_raw is not None or review:
            review_status = "unverified"
        else:
            review_status = "missing"
        integration = state_evidence.get("integration") or {}
        integration_ok = bool(integration and integration.get("candidate_sha") == candidate_sha
                              and integration.get("result_digest") == result_sha
                              and integration.get("result") == "pass")
        integration_status = "verified" if integration_ok else "missing"
        milestones = {
            "red": red["status"],
            "green": green["status"],
            "refactor": ("verified" if refactor_ok and result_source == "product_ref"
                         else "available_checkout_only" if refactor_ok else "missing"),
            "review": review_status,
            "integration": integration_status,
        }
        ordered = ("red", "green", "refactor", "review", "integration")
        first_unmet = next((name for name in ordered if milestones[name] != "verified"), None)
        attempt_rows = [
            {key: row.get(key) for key in ("run_id", "phase", "candidate_sha", "digest", "plan_digest")}
            for row in ledger_rows if isinstance(row, dict) and row.get("task_id") == task_id
        ]
        graph_changes: list[str] = []
        if ancestry_ok:
            changed = _git(root, "diff", "--name-only", "-z", base_sha + ".." + candidate_sha)
            if changed.returncode == 0:
                graph_changes = sorted(name for name in changed.stdout.split("\0") if name)
        tasks.append({
            "task_id": task_id,
            "state_status": (task_state or {}).get("status", "missing"),
            "state_record_sha256": _legacy_digest(task_state) if task_state else None,
            "result": {
                "path": result_path,
                "source": result_source,
                "sha256": result_sha,
                "schema_valid": result_valid,
                "base_sha": base_sha,
                "candidate_sha": candidate_sha,
                "base_candidate_ancestry_valid": ancestry_ok,
                "candidate_in_product_ref": candidate_in_product_ref,
                "changed_paths": graph_changes,
                "tdd_red": red,
                "tdd_green": green,
                "refactor_is_structured": refactor_ok,
                "review_evidence": {
                    "path": review_path,
                    "source": review_source,
                    "sha256": review_digest,
                    "identity_matches": review_evidence_ok,
                    "recorded_by": review.get("recorded_by") if isinstance(review, dict) else None,
                    "status": review_status,
                },
            },
            "milestones": milestones,
            "first_unmet_milestone": first_unmet,
            "state_claims_integration_without_receipt": (
                (task_state or {}).get("status") == "integrated" and not integration_ok
            ),
            "conflicts": task_conflicts,
            "attempt_rows": attempt_rows,
        })
        conflicts.extend(f"task {task_id}: {message}" for message in task_conflicts)

    pending = {
        task_id: task.get("status")
        for task_id, task in (state.get("tasks") or {}).items()
        if task_id in {str(i) for i in range(6, 11)} and isinstance(task, dict)
    }
    return {
        "schema": "ask-legacy-reconciliation/v1",
        "work_id": work_id,
        "product": {"ref": product_ref, "commit": commit,
                    "state_path": state_path,
                    "state_sha256": hashlib.sha256(state_raw).hexdigest(),
                    "state_revision": state.get("revision")},
        "accepted_authority": {
            "tracked_pin_path": pin_path,
            "tracked_pin_sha256": hashlib.sha256(pin_raw).hexdigest() if pin_raw else None,
            "tracked_pin": {key: (pin or {}).get(key) for key in (*identity_keys, "schema", "capability")},
            "authority_ref": authority_ref,
            "authority_commit": authority_sha or None,
            "authority_document_sha256": hashlib.sha256(authority_raw).hexdigest() if authority_raw else None,
            "authority": {key: (authority or {}).get(key) for key in (*identity_keys, "schema", "capability")},
            "independent_plan_review": {key: authority_review.get(key) for key in (
                "reviewer", "runtime", "model", "reasoning_effort", "parent_model",
                "reviewed_commit", "plan_digest")},
            "reviewed_input_digests": authority_review.get("file_digests", {}),
            "identity_differences": identity_differences,
        },
        "model_and_verifier": {
            "model_policy_path": model_policy_path,
            "model_policy_sha256": hashlib.sha256(model_policy_raw).hexdigest() if model_policy_raw else None,
            "accepted_plan_model": authority_review.get("model"),
            "accepted_plan_runtime": authority_review.get("runtime"),
            "verifier_snapshots": verifier_snapshots,
        },
        "task_audit": tasks,
        "tasks_6_to_10": pending,
        "legacy_ledger": {
            "path": ledger_path,
            "source": ledger_source,
            "sha256": hashlib.sha256(ledger_raw).hexdigest() if ledger_raw is not None else None,
            "rows_for_tasks_1_to_5": len([row for row in ledger_rows if isinstance(row, dict)
                                          and row.get("task_id") in {"1", "2", "3", "4", "5"}]),
        },
        "preflight": {"active_tasks": active_tasks,
                      "conflicts": conflicts,
                      "read_only": True,
                      "task_scheduling": False},
        "limitations": [
            "Legacy state has no attempt-history collection.",
            "TaskResult notes do not bind Refactor as a structured milestone.",
            "A task status of integrated is not accepted as integration proof without a receipt.",
            "Checkout-only artifacts are inventoried but are not durable product-ref evidence.",
            "Legacy run reports do not consistently retain the verifier source identity; accepted contract snapshots are recorded separately.",
            "Legacy task review state does not record who persisted the review, so reviewer independence cannot be established from the retained record.",
        ],
    }


def legacy_adoption_proposal(audit: dict) -> dict:
    """Prepare a reviewable proposal only; this function never adopts or schedules."""
    if audit.get("schema") != "ask-legacy-reconciliation/v1":
        raise ValueError("unsupported legacy reconciliation report")
    tasks = audit.get("task_audit") or []
    return {
        "schema": "ask-legacy-adoption-proposal/v1",
        "audit_sha256": _legacy_digest(audit),
        "product_preimage": audit.get("product"),
        "authority_preimage": audit.get("accepted_authority"),
        "task_preimages": [
            {"task_id": task["task_id"], "state_status": task["state_status"],
             "state_record_sha256": task["state_record_sha256"],
             "result": task["result"], "milestones": task["milestones"],
             "first_unmet_milestone": task["first_unmet_milestone"],
             "state_claims_integration_without_receipt": task["state_claims_integration_without_receipt"],
             "conflicts": task["conflicts"], "attempt_rows": task["attempt_rows"]}
            for task in tasks
        ],
        "tasks_6_to_10": audit.get("tasks_6_to_10"),
        "decision": "proposal_only_review_required",
        "preserve_original_attempts": True,
        "rewrite_product_state": False,
        "change_authority": False,
        "reclassify_tests": False,
        "schedule_product_tasks": False,
        "review": {"decision": "PENDING", "reviewer": None,
                   "recorded_by": None, "proposal_sha256": None},
    }


def validate_legacy_adoption_proposal(root: Path, audit: dict, proposal: dict) -> dict:
    """Validate exact preimages and independent review without performing adoption."""
    errors: list[str] = []
    if proposal.get("schema") != "ask-legacy-adoption-proposal/v1":
        errors.append("unsupported proposal schema")
    if proposal.get("audit_sha256") != _legacy_digest(audit):
        errors.append("proposal does not bind the exact reconciliation report")
    expected = legacy_adoption_proposal(audit)
    if any(proposal.get(key) != expected.get(key) for key in (
        "product_preimage", "authority_preimage", "task_preimages", "tasks_6_to_10",
        "preserve_original_attempts", "rewrite_product_state", "change_authority",
        "reclassify_tests", "schedule_product_tasks", "decision",
    )):
        errors.append("proposal changes a captured product, authority, or task preimage")
    product = audit.get("product") or {}
    current = _git(Path(root), "rev-parse", "--verify", str(product.get("ref", "")) + "^{commit}")
    if current.returncode or current.stdout.strip() != product.get("commit"):
        errors.append("product ref moved since the audit")
    authority = audit.get("accepted_authority") or {}
    authority_now = _git(Path(root), "rev-parse", "--verify", str(authority.get("authority_ref", "")))
    if authority_now.returncode or authority_now.stdout.strip() != authority.get("authority_commit"):
        errors.append("accepted-tests authority moved since the audit")
    if audit.get("preflight", {}).get("active_tasks"):
        errors.append("legacy state has an active task writer")
    if audit.get("preflight", {}).get("conflicts"):
        errors.extend(audit["preflight"]["conflicts"])
    review = proposal.get("review") or {}
    payload = {key: value for key, value in proposal.items() if key != "review"}
    if (review.get("decision") != "APPROVED"
            or not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip()
            or not isinstance(review.get("recorded_by"), str) or not review["recorded_by"].strip()
            or review.get("reviewer") == review.get("recorded_by")
            or review.get("proposal_sha256") != _legacy_digest(payload)):
        errors.append("proposal lacks an exact independent review")
    return {"status": "refused" if errors else "preconditions_validated",
            "errors": sorted(set(errors)), "product_mutated": False,
            "authority_mutated": False, "tasks_scheduled": False}
