# Intent: implement durable continuation recovery

## What
Implement and verify the sealed continuation-recovery plan addressing all R1–R4
findings, isolated from the interrupted product workstream. Execute CR-1 through
CR-4 on `agent/continuation-recovery` against the accepted CR-01–CR-08 contract.

## Why
Missing/replaced runtime state must not erase real execution or restart a task
at its implemented candidate without reconciliation.

## Non-goals
Product adoption/integration and product scheduling. CR-4 is limited to the
read-only product audit and reviewed adoption proposal defined by the sealed
plan. Do not initialize or mutate the original product runtime state.

## Known assumptions
Local cooperative Git; existing coordinator admission and TDD gates remain
required. For this workstream's CR-3 recovery only, a human-approved,
independently reviewed coordinator upgrade may select an exact P1-authorized
verifier source after the P1 authority records its commit/tree and review
identity. The original task base remains `2c508ff`; historical report,
authority, candidate and runner identities remain immutable. The upgrade cannot
select arbitrary candidate code and must preserve normal static, semantic,
candidate, completion and integration checks.

## Human decisions
Explore skipped: destination already clear. The user approved the implementation
scope change on 2026-10-22; its record is in `spec-change-execution.md` and
`authorization.md`. The user approved the bounded CR-3 recovery package on
2026-10-23; see `cr3-scoped-decision-record.md`. The user approved the
coordinator-upgrade trust-boundary correction on 2026-10-23; see
`cr3-coordinator-upgrade-decision.md`.

## E2E
Applies: disposable Git repositories and bounded fresh processes, as specified
in `plan.md` and `test-plan.json`. Execute task-owned Red → Green → Refactor,
independent review, and coordinator integration evidence for each task. CR-3's
normal integration uses only the exact coordinator/verifier revisions bound
and independently reviewed in its accepted P1 migration record.
