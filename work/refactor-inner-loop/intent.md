# Intent: Move Refactor into the inner task loop

## What

Make `08 Refactor` an explicit operation inside the current task's inner loop,
and remove its separate placement in the outer workstream sequence. Align the
canonical stage contracts, retry dispatch where necessary, workflow references,
and generated runtime bundles so they describe the same transition.

## Why

The Refactor contract already refers to the current task, while the outer path
still presents it as a separate stage and rejected-review dispatch returns
`implement` or `debug`. These mixed instructions obscure who fixes findings and
where execution resumes.

## Non-goals

Changing product requirements, removing review or verification, changing retry
limits or ownership boundaries, weakening candidate-bound evidence, redesigning
the entire workflow, or renumbering stage identifiers.

## Known assumptions

- Explore skipped: destination already clear.
- Refactor uses the current task and its owned paths; it does not spawn a second
  task or change acceptance criteria.
- A changed candidate requires fresh applicable review and verification before
  integration. Existing escalation and retry limits remain in force.
- Outer workstream review, verification, and acceptance retain their existing
  obligations; moving Refactor does not remove them.
- All generated runtime bundles derive from the updated canonical contracts.
- Required confirmations remain selectable questions; this change adds no
  per-task human approval gate.

## Open questions

Does Refactor run only to address actionable review findings (recommended), or
as a mandatory cleanup pass on every task? A selectable question is pending.

## Human decisions

Requested: move Refactor inside the inner loop. The trigger decision and complete
intent approval are pending; implementation has not started.

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: This changes protocol and CLI task transitions,
not a user-facing application journey. Verification will cover task dispatch,
review/correction transitions, evidence invalidation, and generated bundle parity.


