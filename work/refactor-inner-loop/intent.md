# Intent: Move Refactor into the inner task loop

## What

Place TDD and task code review inside the inner loop. For each behavioral slice,
use Red -> Green -> Refactor, keeping tests green through refactoring. After the
task's slices are complete, independently review its current candidate. Review
suggestions return the same task for correction and refactoring, then fresh code
review and applicable verification. Repeat until review has no unresolved
suggestions and the candidate passes verification; only then integrate it.

Remove Refactor's separate placement in the outer workstream sequence. Make
task code review explicitly part of the inner loop too. Align canonical stages,
retry dispatch where necessary, workflow references, repository-specific TDD
guidance, and every generated runtime bundle.

## Why

The Refactor contract refers to the current task, while the outer path lists it
as a separate stage. The prepared TDD skill explicitly excludes refactoring
from the red/green loop, and rejected-review dispatch returns `implement` or
`debug`. These conflicting instructions place TDD cleanup and review corrections
in the wrong part of execution.

## Non-goals

Changing product requirements, removing review or verification, changing retry
limits or ownership boundaries, weakening candidate-bound evidence, redesigning
the entire workflow, or renumbering stage identifiers.

## Known assumptions

- Explore skipped: destination already clear.
- Refactor uses the current task and its owned paths; it does not spawn a second
  task or change acceptance criteria.
- Behavioral review fixes use Red -> Green -> Refactor again; structural
  refactoring preserves behavior and keeps existing tests green.
- A changed candidate requires fresh independent code review and applicable
  verification before integration. Stale approval cannot authorize it.
- Review/refactor repeats until there are no unresolved suggestions. Existing
  retry limits remain safety stops: exhausting them blocks or escalates the
  task and never permits integration with unresolved findings.
- Task code review belongs inside the loop. Workstream-wide assessment,
  verification, and acceptance keep their aggregate responsibilities without
  requiring a duplicate task-level Refactor phase outside the loop.
- Reconcile conflicting prepared TDD instructions through repository-owned
  guidance or preparation overlays, preserving pinned upstream skill sources.
- All generated runtime bundles derive from the updated canonical contracts.
- Required confirmations remain selectable questions; this change adds no
  per-task human approval gate.
- Test the public inner-loop CLI transitions and integration gates, plus
  generated stage/bundle consistency; avoid tests of private helper structure.

## Open questions

None. The user clarified TDD placement and the review/correction exit condition.

## Human decisions

The user specified Red -> Green -> Refactor inside the inner loop, with code
review also inside the loop and corrections repeated until review has no
remaining suggestions. Complete intent approval is pending; implementation has
not started.

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: This changes protocol and CLI task transitions,
not a user-facing application journey. Verification will cover task dispatch,
review/correction transitions, evidence invalidation, and generated bundle parity.

