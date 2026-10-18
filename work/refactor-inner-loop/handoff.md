# Planning handoff: refactor-inner-loop

## Stop reached

Stage 05 Plan is complete. The user instructed: "go till finishing the plan and
stop". No implementation has started, no task runtime state has been initialized,
and no planned behavior test has been written or executed. No merge or push was
performed for this workstream.

## Reviewed contract

- Intent: work/refactor-inner-loop/intent.md.
- Specification: specs/current/refactor-inner-loop.md and .json, revision 1.
- Plan: work/refactor-inner-loop/plan.md.
- TaskGraph: work/refactor-inner-loop/inner-loop/tasks.yaml.
- Test map: work/refactor-inner-loop/test-plan.json, 13 declared cases.
- Independent challenge: work/refactor-inner-loop/spec-challenge.md, APPROVED.
- Exact-contract decision: work/refactor-inner-loop/plan-review.json, APPROVED.
- Reviewed source revision: d754f11c4a2b4568ae37f5753f41389edf14ae04.
- Coordinator pin: work/refactor-inner-loop/traceability-accepted.json and local
  refs/ask/accepted-tests/refactor-inner-loop.

## Execution sequence for a later authorized session

RF-01 defines canonical Red -> Green -> Refactor -> independent task review,
local/broad/redesign classification, coordinator parking, and source contracts.
RF-02 applies and tests the idempotent pinned-TDD override in both installed views.
RF-03 updates every runtime bundle/reference and verifies consumer delivery and
existing candidate integration gates. Execute serially on this workstream branch.

All valid local refactors are required. Broader horizontal refactors are proposals
parked with tag refactoring; they do not expand or block local implementation.
Required meaning/behavior/contract changes use Spec Change. Review and verification
must bind to the current candidate; existing bounded retries still block/escalate
unfinished work. Keep broad-card drafts in persisted runtime evidence during
resumable task work; materialize them only at the final safe no-writer boundary.

## Gates preserved

The planning instruction authorized document preparation, not implementation.
The complete-intent confirmation file is deliberately absent: no approval choice
was fabricated from an instruction to prepare a plan. Before a future Implement
stage, satisfy the existing check-workstream gate against the final intent using
an actual submitted approval choice if still required. Do not ask for that choice
now; the requested stopping point has been reached.

The accepted-tests authority ref is local Git metadata. A different clone must
recover/register the reviewed coordinator authority through the documented process;
a source acceptance file alone cannot create that authority. Do not fabricate a
new review or claim tests passed to work around a missing ref.

## Validation and limitations

TaskGraph validation, canonical spec/test-plan validation, independent semantic
classification review, and exact reviewed-contract pin checks pass. Four semantic
criteria use independently authorized review-only evidence; 13 executable cases
are future obligations, not completed test evidence. New preparation/consumer
behavior requires actual assertion Red/Green; unchanged safeguards are regression
coverage. Outer workstream Verify and Accept are not reached.
