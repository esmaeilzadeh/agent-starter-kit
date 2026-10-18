# Intent: Move Refactor into the inner task loop

## What

Place TDD and task code review inside the inner loop. For each behavioral slice,
use Red -> Green -> Refactor, keeping tests green through refactoring. After the
task's slices are complete, independently review its current candidate. Local review suggestions return the same task for correction and refactoring,
then fresh code review and applicable verification. Park broader horizontal
refactoring suggestions as later-inbox cards tagged refactoring. Repeat until
review has no unresolved local suggestions and the candidate passes verification; only then integrate it.

Remove Refactor's separate placement in the outer workstream sequence. Make
task code review explicitly part of the inner loop too. Align canonical stages,
retry dispatch where necessary, workflow references, repository-specific TDD
guidance, and every generated runtime bundle.

For every load-bearing Grill decision, present selectable answer options and
keep an optional free-text path available in the same response even when the
human selects an option. Use the active runtime's structured choice control
only when it can be called for the current mode and question type and can
preserve both selection and added text. If it cannot, offer numbered options
and accept a combined answer such as `2 — <additional context>`. During
continuation, ask for a missing or stale confirmation only when it blocks an
otherwise authorized next step. When the approved plan explicitly stops before
that step, report the authorized work as complete without describing the future
gate as missing.

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
- Complete all task-local refactor suggestions; broader horizontal refactors are
  suggested as parked .later cards tagged refactoring and do not block the task.
- Refactoring preserves behavior, meaning, and contracts. A necessary change to
  any of those is redesign and requires Spec Change before proceeding.
- Review/refactor repeats until there are no unresolved local suggestions. Existing
  retry limits remain safety stops: exhausting them blocks or escalates the
  task and never permits integration with unresolved findings.
- Task code review belongs inside the loop. Workstream-wide assessment,
  verification, and acceptance keep their aggregate responsibilities without
  requiring a duplicate task-level Refactor phase outside the loop.
- Reconcile conflicting prepared TDD instructions through repository-owned
  guidance or preparation overlays, preserving pinned upstream skill sources.
- All generated runtime bundles derive from the updated canonical contracts.
- Grill choices preserve both option selection and user-supplied nuance in one
  response; an exclusive “Other” option alone does not meet this requirement.
  Generated runtime prompts follow the same contract.
- Continuation distinguishes a missing gate for an authorized next action from
  an explicit plan stop.
- Required confirmations remain selectable questions; this change adds no
  per-task human approval gate.
- Test the public inner-loop CLI transitions and integration gates, plus
  generated stage/bundle consistency; avoid tests of private helper structure.

## Open questions

None. The user clarified TDD placement and the review/correction exit condition.

## Human decisions

The user specified Red -> Green -> Refactor and code review inside the inner
loop; all local refactors must be completed, while broader horizontal refactors
are parked as later cards tagged refactoring. Necessary changes to meaning,
behavior, or contracts require Spec Change. The exact instruction "go till
finishing the plan and stop" originally authorized preparing Spec, Challenge,
and Plan only. On 2026-10-19 the human approved a Spec Change proposal to add
selectable Grill decisions with a write-in path and correct explicit-stop
handling, then explicitly authorized implementation, pushing the work branch,
merging into `develop`, and pushing `develop`. This amended intent now includes
that work. Record the complete-intent choice against this exact intent before
implementation; no approval has been fabricated.

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: This changes protocol and CLI task transitions,
not a user-facing application journey. Verification will cover task dispatch,
review/correction transitions, evidence invalidation, and generated bundle parity.
