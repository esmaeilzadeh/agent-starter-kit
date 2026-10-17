"""Validate candidate-bound human comprehension records without certifying people."""
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
              admission=None, expected_admission=None):
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
    required_admission = {"canonical_flow", "source_identities", "evidence_identities"}
    if not isinstance(admission, dict) or not required_admission <= set(admission):
        reasons.append("representative admission identities are incomplete")
    elif admission != expected_admission:
        reasons.append("representative admission identities are stale")
    else:
        flow = admission.get("canonical_flow")
        sources = admission.get("source_identities")
        evidence = admission.get("evidence_identities")
        if not isinstance(flow, dict) or not all(_nonempty(flow.get(k)) for k in
               ("work_id", "plan_digest", "case_id", "executable_case_id")):
            reasons.append("selected canonical flow identity is incomplete")
        if not isinstance(sources, dict) or not all(_nonempty(sources.get(k)) for k in
               ("candidate_sha", "spec_digest", "plan_digest", "source_digest")):
            reasons.append("representative source identities are incomplete")
        if (not isinstance(evidence, dict)
                or not all(_nonempty(evidence.get(k)) for k in
                           ("report_digest", "contract_digest", "review_digest", "run_id"))
                or not _dependency_value(evidence, "log_digests")):
            reasons.append("genuine evidence identities are incomplete")
    return {"status": "blocked_context" if reasons else "context_ready",
            "task_node_id": task_node_id, "snapshot_digest": snapshot.identity["digest"],
            "context_blockers": reasons,
            "prerequisites": [
                {"id": "genuine_retained_result", "status": "not_evaluated"},
                {"id": "human_comprehension", "status": "not_recorded"},
            ],
            "demo_complete": False}


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _dependency_value(group, field):
    if not isinstance(group, dict):
        return False
    value = group.get(field)
    if field == "source_digests" or field == "log_digests":
        return isinstance(value, list) and bool(value) and all(_nonempty(item) for item in value)
    return _nonempty(value)
