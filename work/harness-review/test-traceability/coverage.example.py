"""PLAN SKETCH ONLY: structural coverage, not an integrated completion gate.

The real implementation must additionally validate JSON field types, reviews,
TDD, runner reports, source/commit identities, task scopes and trusted evidence.
This sketch does not run tests or establish that assertions satisfy the spec.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Violation:
    code: str
    criterion_id: str | None = None
    test_id: str | None = None
    required_type: str | None = None


def validate_coverage(
    spec: dict[str, Any], plan: dict[str, Any]
) -> list[Violation]:
    """Check already type-validated contracts for missing or orphan coverage."""
    criteria = {item["id"] for item in spec["criteria"]}
    testable = {
        item["id"]
        for item in spec["criteria"]
        if item["verification_mode"] == "tests"
    }
    obligations = {
        item["criterion_id"]: set(item["required_types"])
        for item in plan["obligations"]
    }
    violations = [
        Violation("missing_obligation", criterion_id)
        for criterion_id in sorted(testable - obligations.keys())
    ]
    for criterion_id, required_types in obligations.items():
        if criterion_id not in testable:
            violations.append(Violation("invalid_obligation", criterion_id))
        if not required_types:
            violations.append(Violation("empty_required_types", criterion_id))
        mapped_types = {
            test["type"]
            for test in plan["tests"]
            if criterion_id in test["criterion_ids"]
        }
        for missing in sorted(required_types - mapped_types):
            violations.append(
                Violation("missing_test_type", criterion_id, required_type=missing)
            )

    for test in plan["tests"]:
        if not test["criterion_ids"]:
            violations.append(Violation("orphan_test", test_id=test["id"]))
        for criterion_id in test["criterion_ids"]:
            if criterion_id not in criteria:
                violations.append(
                    Violation("unknown_criterion", criterion_id, test["id"])
                )
        if not test["scenario"]["then"] or not test["expected_assertions"]:
            violations.append(Violation("empty_behavior", test_id=test["id"]))
    return violations


def check_final_cases(
    plan: dict[str, Any], outcomes: dict[str, str]
) -> list[Violation]:
    """Sketch: every planned case needs an actual pass, not a process exit code.

    The production evaluator first validates adapter output, unique case IDs,
    exact final-candidate identity and workstream scope before calling this step.
    """
    return [
        Violation("required_case_not_passed", test_id=test["id"])
        for test in plan["tests"]
        if outcomes.get(test["id"]) != "passed"
    ]
