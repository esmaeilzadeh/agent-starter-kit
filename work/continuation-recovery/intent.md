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
Local cooperative Git; existing coordinator admission, authority and TDD gates
remain required. The selected base is the original current product branch.

## Human decisions
Explore skipped: destination already clear. The user approved the implementation
scope change on 2026-10-22; its record is in `spec-change-execution.md` and
`authorization.md`. This intent still requires exact human confirmation before
implementation admission.

## E2E
Applies: disposable Git repositories and bounded fresh processes, as specified
in `plan.md` and `test-plan.json`. Execute task-owned Red → Green → Refactor,
independent review, and coordinator integration evidence for each task.
