# Specification Change Proposal: record unchanged baseline tests honestly

## Current state

The accepted contract pin is `722fe3002253e473de0689823c3fe35052d458a1`; the current WB-001 coordinator base is `92c43e541ee244add20e02eb65082348add716ad`. The task maps 25 cases. Three WB-specific cases have genuine assertion-red history. The other 22 foundation cases are assigned as `new`, but their test source files predate the accepted task baseline and are byte-identical to the current candidate. Their prior task run passed those cases; it did not record assertion-red outcomes. The accepted plan already says this gap must remain visible at final workstream Verify and must not be hidden by relabeling them as regressions.

Under the current Verify evaluator, task completion requires red-and-green history for every `new` case. Therefore the unchanged foundation cases prevent WB-001 integration despite their purpose as regression protection and the plan's explicit requirement to retain the historical gap as a final partial result. The task cannot proceed honestly by creating failures in old tests or inventing red reports.

## Proposed change

Add an accepted test-plan list of the 22 WB-001 foundation test IDs that may receive a typed `baseline-regression` acknowledgment for task integration. A candidate review may use this acknowledgment only when all of the test's accepted source paths existed at the accepted contract revision and are byte-identical to the candidate. The independent reviewer must approve the rationale and acknowledge that the acknowledgment does not claim behavior-red history.

The evaluator accepts this type only for a task-scoped review, only for listed IDs, only while their classification remains `new`, and only when the accepted-source identity check passes. Workstream-scoped review rejects this exemption. Final workstream Verify continues to require actual red history for all 57 accepted cases, so this amendment preserves the known 22-case partial result.

## Required artifacts

- `work/<work-id>/test-plan.json`: explicitly list the 22 permitted WB-001 IDs without changing any ID, assertion, task assignment, or change classification.
- `work/<work-id>/plan.md`: define the task-only rule and preserve the final partial condition.
- `work/<work-id>/inner-loop/tasks.yaml`: include the bounded verification-support paths in WB-001 ownership and completion evidence.
- Traceability contract validation, semantic review, and completion evaluator changes plus focused tests for valid acknowledgment, changed-source rejection, and workstream rejection.
- Independent exact-candidate review and a new accepted pin before coordinator use. Cancel/archive the pending WB-001 attempt and restart from a fresh coordinator base containing that pin.

## Scope and non-goals

This affects only task-scoped verification for the explicitly listed WB-001 cases. It does not modify product criteria or behavior, create historical red results, change test classification, admit future-task sources, or permit a final workstream pass without real red evidence. Existing WB-001 behavior reds, prior approvals, and the current 25-case green run remain preserved.

## Acceptance criteria

1. The accepted test-plan validator rejects exemptions for unassigned IDs, unknown tasks, or tests not classified `new`.
2. A task review accepts a reviewer-acknowledged exemption for a listed test only when every source path is present and byte-identical at the accepted contract and candidate revisions.
3. Changing any referenced test source, changing the test classification, or applying the exemption in workstream review is rejected.
4. WB-001 task Verify can finish with all 25 assigned cases green and semantically reviewed while preserving the 22 missing-red entries as an explicit TDD-history gap.
5. Final workstream Verify does not accept the task-scoped exemption and continues to report the genuine red-history gap as partial.
6. The exact implementation and contract receive independent review and pinning before the fresh WB-001 coordinator uses them.

## Decision

Authorized by the human in chat on 2026-10-09: “do not wait run all task I will review the final result.” This is the verification amendment required to continue the explicitly ordered task sequence while preserving the known final gap for the user's review.
