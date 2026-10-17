"""Validate candidate-bound human comprehension records without certifying people."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from datetime import datetime

SCHEMA = "ask-workbench-comprehension/v1"
PROMPTS = ("purpose", "spec_context", "plan_context", "concrete_flow", "setup",
           "action", "expected_observation", "assertion", "actual_outcome", "applicability")

# These are the inputs that can change what the returning developer sees or
# what the evidence means. Requiring named groups prevents a caller from
# accidentally treating a partial dependency list as a complete binding.
DEPENDENCY_GROUPS = {
    "inspected_sources": ("candidate_sha",),
    "spec": ("selector_digest", "bytes_digest"),
    "plan": ("selector_digest", "bytes_digest"),
    "test": ("source_digest",),
    "helpers": ("source_digests",),
    "fixtures": ("source_digests",),
    "evidence": ("report_digest", "log_digests", "contract_digest", "review_digest"),
}
REPRESENTATIVE_RUN_ID = "799924ec199b4717a3eabf4fb39a1bdc"


def validate_record(record, expected):
    """Return valid/failed/stale/invalid; never create or infer human answers."""
    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        return {"status": "invalid", "diagnostics": ["record schema is invalid"]}
    if not isinstance(expected, dict):
        return {"status": "invalid", "diagnostics": ["expected binding must be an object"]}
    required_bindings = {"candidate_sha", "snapshot_digest", "task", "scenario", "test", "dependencies"}
    if not required_bindings <= set(expected):
        return {"status": "invalid", "diagnostics": ["expected binding must include candidate, snapshot, Task, Scenario, Test, and dependencies"]}
    dependencies = expected["dependencies"]
    if not isinstance(dependencies, dict):
        return {"status": "invalid", "diagnostics": ["dependencies must be an object"]}
    missing = [f"{group}.{field}" for group, fields in DEPENDENCY_GROUPS.items()
               for field in fields if not _dependency_value(dependencies.get(group), field)]
    if missing:
        return {"status": "invalid", "diagnostics": ["dependencies omit required identities: " + ", ".join(missing)]}
    for key, value in expected.items():
        if record.get(key) != value:
            return {"status": "stale", "diagnostics": [f"record binding differs: {key}"]}
    if (record.get("chat_assistance") is not False
            or not _nonempty(record.get("participant"))
            or not _nonempty(record.get("assessor"))):
        return {"status": "failed", "diagnostics": ["record requires a returning human, independent assessor, and chat_assistance=false"]}
    try:
        timestamp = datetime.fromisoformat(record.get("timestamp", "").replace("Z", "+00:00"))
        if timestamp.tzinfo is None or timestamp.utcoffset().total_seconds() != 0:
            raise ValueError
    except (AttributeError, TypeError, ValueError):
        return {"status": "invalid", "diagnostics": ["timestamp must be ISO-8601 UTC"]}
    answers = record.get("answers")
    if (not isinstance(answers, list) or len(answers) != len(PROMPTS)
            or any(not isinstance(answer, dict) for answer in answers)
            or [answer.get("prompt") for answer in answers] != list(PROMPTS)):
        return {"status": "invalid", "diagnostics": ["record must contain the ten required prompts exactly once in order"]}
    failed = []
    for prompt, answer in zip(PROMPTS, answers):
        if any(not _nonempty(answer.get(field)) for field in ("answer", "assessor_reason", "evidence")):
            return {"status": "invalid", "diagnostics": [f"{prompt} needs answer, assessor reason, and evidence"]}
        if answer.get("assessment") not in {"pass", "fail"}:
            return {"status": "invalid", "diagnostics": [f"{prompt} assessment must be pass or fail"]}
        if answer["assessment"] != "pass":
            failed.append(prompt)
    if record.get("chat_assistance") is not False:
        failed.append("chat_assistance")
    return {"status": "failed" if failed else "valid", "failed_prompts": failed,
            "diagnostics": ["one or more comprehension assessments failed"] if failed else []}


def demo_gate(root, snapshot, task_node_id, *, expected_snapshot_digest=None,
              retained_root=None):
    """Gate context locally and report genuine evidence/human work still required.

    Resolving context alone never marks a demonstration complete. The actual
    retained-result evaluator and returning-human exercise remain separate.
    """
    from .passages import required_task_passages
    from .snapshot import is_current

    reasons = []
    diagnostics = snapshot.diagnostics(root)
    if (not is_current(snapshot, root)
            or (expected_snapshot_digest is not None
                and snapshot.identity["digest"] != expected_snapshot_digest)):
        reasons.append("snapshot is stale")
    if diagnostics:
        reasons.append("captured model or required context is invalid")
    try:
        missing = required_task_passages(snapshot, task_node_id)
    except ValueError as exc:
        missing = ["task"]
        reasons.append(str(exc))
    if missing:
        reasons.append("required passages unresolved: " + ", ".join(missing))
    spec_records = [row for row in snapshot.passages.values()
                    if row.get("node_id") == task_node_id and row.get("kind") == "context"
                    and row.get("role") == "spec"]
    selected_sections = {tuple(row.get("resolution", {}).get("selector", {}).get("path", []))
                         for row in spec_records
                         if row.get("resolution", {}).get("state") == "available"}
    if not {("Specification: Engineering Model and local workbench", "Projections and evidence"),
            ("Specification: Engineering Model and local workbench", "Interactive UI")} <= selected_sections:
        reasons.append("required representative specification passages are incomplete")
    retained_root = Path(retained_root or os.environ.get("ASK_RWB_RETAINED_ROOT", root)).resolve()
    admission, admission_error = _captured_demo_identities(root, retained_root, snapshot, task_node_id)
    if admission_error:
        reasons.append(admission_error)
    return {"status": "blocked_context" if reasons else "context_ready",
            "task_node_id": task_node_id, "snapshot_digest": snapshot.identity["digest"],
            "admission_identities": admission,
            "context_blockers": reasons,
            "prerequisites": [
                {"id": "genuine_retained_result", "status": "identity_verified_authority_not_evaluated"
                 if admission else "unavailable"},
                {"id": "human_comprehension", "status": "not_recorded"},
            ],
            "demo_complete": False}


def _captured_demo_identities(root, retained_root, snapshot, task_node_id):
    """Coordinate exact graph selection and retained identity checks."""
    try:
        candidate_sha = _clean_candidate_sha(root)
        task, case, selected_test, plan_digest, raw_plan = _resolve_captured_flow(snapshot, task_node_id)
        execution = task.get("execution")
        if not isinstance(execution, dict) or set(execution) != {"work_id", "task_id"}:
            raise ValueError("Task has no qualified execution owner")
        owner = execution["work_id"]
        task_id = execution["task_id"]
        identities = _verify_retained_evidence(retained_root, owner, task_id, case, selected_test)
        return {
            "canonical_flow": {"work_id": case["work_id"], "plan_digest": plan_digest,
                               "case_id": case["case_id"], "executable_case_id": selected_test["case_id"]},
            "source_identities": {"candidate_sha": candidate_sha,
                                  "model_digest": snapshot.identity["model"]["sha256"],
                                  "snapshot_digest": snapshot.identity["digest"],
                                  "selected_source_digest": hashlib.sha256(raw_plan).hexdigest(),
                                  **identities.pop("source_identities"),
                                  "spec_plan_context_digests": {
                                      f"{row.get('role')}:{row.get('selector')}": row.get("sha256")
                                      for row in snapshot.passages.values()
                                      if row.get("node_id") == task_node_id and row.get("kind") == "context"}},
            "evidence_identities": identities["evidence_identities"],
        }, None
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError) as exc:
        return None, f"representative admission identities could not be verified: {exc}"


def _clean_candidate_sha(root):
    status = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                            cwd=root, capture_output=True, text=True)
    if status.returncode:
        raise ValueError("candidate checkout is unavailable")
    if status.stdout.strip():
        raise ValueError("candidate has uncommitted source")
    head = subprocess.run(["git", "rev-parse", "--verify", "HEAD"],
                          cwd=root, capture_output=True, text=True)
    if head.returncode:
        raise ValueError("candidate commit is unavailable")
    return head.stdout.strip()


def _resolve_captured_flow(snapshot, task_node_id):
    """Resolve one Task→Scenario→Test chain from captured model and plan bytes."""
    document = snapshot.document
    nodes = {node.get("id"): node for node in document.get("nodes", [])
             if isinstance(node, dict)}
    task = nodes.get(task_node_id)
    if not isinstance(task, dict) or task.get("type") != "task":
        raise ValueError("selected node is not a captured Task")
    scenarios = [edge.get("target") for edge in document.get("edges", [])
                 if isinstance(edge, dict) and edge.get("type") == "contributes_to"
                 and edge.get("source") == task_node_id
                 and nodes.get(edge.get("target"), {}).get("type") == "scenario"]
    if len(scenarios) != 1:
        raise ValueError("Task must select exactly one representative Scenario")
    scenario_id = scenarios[0]
    case = nodes[scenario_id].get("case")
    if not isinstance(case, dict) or set(case) != {"work_id", "plan_digest", "case_id"}:
        raise ValueError("representative Scenario has no qualified canonical case")
    tests = [edge.get("source") for edge in document.get("edges", [])
             if isinstance(edge, dict) and edge.get("type") == "covers"
             and edge.get("target") == scenario_id
             and nodes.get(edge.get("source"), {}).get("type") == "test"]
    if len(tests) != 1:
        raise ValueError("representative Scenario must select exactly one Test")
    reference = nodes[tests[0]].get("reference")
    if not isinstance(reference, dict) or (reference.get("work_id"), reference.get("plan_digest"),
                                            reference.get("id")) != (
            case.get("work_id"), case.get("plan_digest"), case.get("case_id")):
        raise ValueError("selected Test and Scenario canonical case differ")
    raw_plan = snapshot.files.get(f"work/{case['work_id']}/test-plan.json")
    if raw_plan is None:
        raise ValueError("selected canonical test plan was not captured")
    plan = json.loads(raw_plan.decode("utf-8"))
    plan_digest = _canonical_digest(plan)
    if plan_digest != case["plan_digest"] or plan.get("work_id") != case["work_id"]:
        raise ValueError("selected canonical test plan is stale")
    rows = [row for row in plan.get("tests", []) if isinstance(row, dict)
            and row.get("id") == case["case_id"]]
    if len(rows) != 1:
        raise ValueError("selected canonical Test is missing or ambiguous")
    return task, case, rows[0], plan_digest, raw_plan


def _verify_retained_evidence(root, work_id, task_id, case, selected_test):
    """Verify the exact historical TaskResult, reviews, contract and green run."""
    from .readable_tests import read_test
    from .workbench_evidence import _blob, execution_history

    task_result, result_raw = _read_json(
        root / "work" / work_id / "inner-loop" / "results" / f"{task_id}.json", root)
    state, _state_raw = _read_json(root / "work" / work_id / "inner-loop" / "state.json", root)
    if (task_result.get("schema") != "ask-task-result/v2" or task_result.get("work_id") != work_id
            or task_result.get("task_id") != task_id):
        raise ValueError("retained TaskResult identity is invalid")
    candidate_sha = task_result.get("candidate_sha")
    task_state = state.get("tasks", {}).get(task_id, {})
    review = task_state.get("evidence", {}).get("review", {})
    verification = task_state.get("evidence", {}).get("verification", {})
    result_digest = hashlib.sha256(result_raw).hexdigest()
    if (review.get("candidate_sha") != candidate_sha or review.get("verdict") != "APPROVED"
            or review.get("result_digest") != result_digest
            or verification.get("result") != "pass"
            or verification.get("result_digest") != result_digest):
        raise ValueError("retained coordinator review or integration receipt is stale")
    _verify_integration_checks(root, verification.get("checks"))

    envelope, review_raw = _read_json(
        root / "work" / work_id / "traceability" / "reviews" / f"{candidate_sha}.json", root)
    test_review = envelope.get("review", {})
    if (envelope.get("review_digest") != _canonical_digest(test_review)
            or test_review.get("decision") != "APPROVED"
            or test_review.get("scope") != "task" or test_review.get("task_id") != task_id
            or test_review.get("candidate_sha") != candidate_sha
            or selected_test.get("id") not in test_review.get("test_ids", [])):
        raise ValueError("retained independent test review does not bind the selected Test")
    actual_sources = {path: hashlib.sha256(_blob(root, candidate_sha, path)).hexdigest()
                      for path in selected_test.get("source_paths", [])}
    if actual_sources != test_review.get("source_digests"):
        raise ValueError("retained Test source digests differ from independent review")
    if read_test(root, selected_test, candidate_sha).get("context_status") != "complete":
        raise ValueError("retained selected Test helper and fixture context is incomplete")

    spec_digest = test_review.get("spec_digest")
    contract_plan_digest = test_review.get("plan_digest")
    history = execution_history(root, work_id, selected_test, spec_digest=spec_digest,
                                plan_digest=contract_plan_digest, candidate_sha=candidate_sha)
    matching_runs = [row for row in history.get("runs", [])
                     if row.get("run_id") == REPRESENTATIVE_RUN_ID
                     and row.get("outcome") == "passed" and row.get("phase") == "final_green"
                     and row.get("output_status") == "valid" and row.get("source_status") == "historical"]
    if len(matching_runs) != 1:
        raise ValueError("retained successful historical report/log identity is missing or ambiguous")
    run = matching_runs[0]
    report_raw = _read_bytes(root / "work" / work_id / "traceability" / "runs"
                             / run["run_id"] / "results.json", root)
    accepted, _accepted_raw = _read_json_at_revision(
        root, candidate_sha, f"work/{work_id}/traceability-accepted.json")
    _validate_accepted_contract(root, work_id, case, spec_digest, contract_plan_digest,
                                candidate_sha, accepted)
    _verify_coordinator_review(root, review)
    return {
        "source_identities": {"test_source_digests": test_review.get("source_digests"),
                              "test_source_sha": candidate_sha},
        "evidence_identities": {"task_result_digest": result_digest,
                                "coordinator_review_digest": review.get("evidence_digest"),
                                "integration_result_digest": verification.get("result_digest"),
                                "test_review_digest": hashlib.sha256(review_raw).hexdigest(),
                                "report_digest": hashlib.sha256(report_raw).hexdigest(),
                                "log_digest": run["output_digest"],
                                "contract_digest": accepted["contract_sha"],
                                "run_id": run["run_id"]},
    }


def _verify_integration_checks(root, checks):
    if not isinstance(checks, list) or not checks:
        raise ValueError("retained integration receipt has no checks")
    for check in checks:
        if (not isinstance(check, dict)
                or not all(_nonempty(check.get(key)) for key in
                           ("id", "command", "evidence", "output_digest"))
                or type(check.get("exit_code")) is not int):
            raise ValueError("retained integration check identity is incomplete")
        raw = _read_bytes(root / check["evidence"], root)
        if (check.get("status") != "pass" or check.get("exit_code") != 0
                or hashlib.sha256(raw).hexdigest() != check.get("output_digest")):
            raise ValueError("retained integration check evidence is invalid")


def _verify_coordinator_review(root, review):
    raw = _read_bytes(root / review["evidence"], root)
    if hashlib.sha256(raw).hexdigest() != review.get("evidence_digest"):
        raise ValueError("retained coordinator review evidence digest is invalid")


def _read_json(path, root):
    raw = _read_bytes(path, root)
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"retained JSON is not an object: {path.name}")
    return value, raw


def _read_json_at_revision(root, revision, relative_path):
    result = subprocess.run(["git", "show", f"{revision}:{relative_path}"], cwd=root,
                            capture_output=True)
    if result.returncode:
        raise FileNotFoundError(f"retained contract is missing at {revision}: {relative_path}")
    value = json.loads(result.stdout.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"retained JSON is not an object: {relative_path}")
    return value, result.stdout


def _read_bytes(path, root):
    root = Path(root).resolve()
    path = Path(path)
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("retained evidence path escapes its repository")
    cursor = root
    for part in path.relative_to(root).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("retained evidence path traverses a symlink")
    if not resolved.is_file():
        raise FileNotFoundError(f"retained evidence is missing: {path}")
    return resolved.read_bytes()


def _canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _validate_accepted_contract(root, work_id, case, expected_spec_digest,
                                expected_contract_plan_digest, candidate_sha, accepted):
    contract_sha = accepted.get("contract_sha")
    if (accepted.get("schema") != "ask-accepted-tests/v1"
            or accepted.get("capability") != "ask-traceability/v1"
            or accepted.get("work_id") != work_id
            or accepted.get("spec_digest") != expected_spec_digest
            or accepted.get("plan_digest") != expected_contract_plan_digest
            or not isinstance(contract_sha, str) or not re.fullmatch(r"[0-9a-f]{40}", contract_sha)
            or not _nonempty(accepted.get("reviewer")) or not _nonempty(accepted.get("recorded_by"))
            or accepted.get("reviewer") == accepted.get("recorded_by")):
        raise ValueError("retained accepted contract does not bind the selected work and flow")
    plan_review = accepted.get("plan_review")
    if (not isinstance(plan_review, dict)
            or accepted.get("plan_review_digest") != _canonical_digest(plan_review)
            or plan_review.get("decision") != "APPROVED"
            or plan_review.get("reviewer") != accepted.get("reviewer")
            or plan_review.get("spec_digest") != expected_spec_digest
            or plan_review.get("plan_digest") != expected_contract_plan_digest):
        raise ValueError("retained accepted plan review is stale")
    root = Path(root).resolve()
    from sys import path as python_path
    verification_root = root / ".agents" / "ask"
    if str(verification_root) not in python_path:
        python_path.insert(0, str(verification_root))
    from verification.traceability.evidence import contracts_at
    contracts = contracts_at(root, work_id, contract_sha)
    for name, value in contracts.items():
        if accepted.get(name + "_digest") != _canonical_digest(value):
            raise ValueError(f"retained accepted {name} digest is stale")
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", contract_sha,
                               candidate_sha],
                              cwd=root, capture_output=True)
    if ancestor.returncode:
        raise ValueError("retained accepted contract is not an ancestor of the historical candidate")


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _dependency_value(group, field):
    if not isinstance(group, dict):
        return False
    value = group.get(field)
    if field == "source_digests" or field == "log_digests":
        return isinstance(value, list) and bool(value) and all(_nonempty(item) for item in value)
    return _nonempty(value)
