"""Validate candidate-bound human comprehension records without certifying people."""
from datetime import datetime

SCHEMA = "ask-workbench-comprehension/v1"
PROMPTS = ("purpose", "spec_context", "plan_context", "concrete_flow", "setup",
           "action", "expected_observation", "assertion", "actual_outcome", "applicability")


def validate_record(record, expected):
    """Return valid/failed/stale/invalid; never create or infer human answers."""
    if not isinstance(record, dict) or record.get("schema") != SCHEMA:
        return {"status": "invalid", "diagnostics": ["record schema is invalid"]}
    if not isinstance(expected, dict):
        return {"status": "invalid", "diagnostics": ["expected binding must be an object"]}
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


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())
