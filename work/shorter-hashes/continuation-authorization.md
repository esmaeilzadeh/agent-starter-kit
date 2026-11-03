# Continuation authorization

## Decision

On 2026-10-21, the user directed: “go till and all accepted”. This explicitly
extends the workstream endpoint from the sealed Plan to implementation,
verification, and final acceptance. The user also approved the Task 5
classification proposal with “approved”.

## Scope

This direction changes the execution endpoint. The product What, Why, and
technical assumptions in the approved intent remain in force. The Task 5
classification change is recorded in `spec-change-task5-classification.md` and
its revised plan was independently reviewed and registered in the coordinator
accepted-tests ref.

The approved `intent.md` is preserved byte-for-byte at SHA-256
`8784f3748505fe0ac51ccb9a7dfe78de0c04f79cd26dac58689fdee10cb084e6`. Its
existing complete-intent confirmation remains bound to that exact digest. The
execution endpoint is recorded here and in `plan.md`, rather than by rewriting
the approved intent.

## Temporary self-recovery authorization

On 2026-10-26, the user authorized temporarily bypassing a kit rule that blocks
work on the kit's own recovery mechanism, provided the resulting system is
consistent. This permits a narrowly scoped, recorded reconciliation of the
accepted continuation-recovery integration and continuation under Task 2's
registered regression classification without manufacturing a failing Red run.

Preserve all existing attempt and receipt bytes. Keep Task 2's Green, Refactor,
review, and integration milestones incomplete until their evidence is recorded.
Keep every other pending task pending, and preserve the approved `intent.md`
bytes. End the exception only after ordinary coordinator recovery and status
checks pass against the reconciled state.
