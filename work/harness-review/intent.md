# Intent: Harness reliability

## What

Confirm and fix candidate-evidence integration and concurrent state updates (R1/R2 in the handoff).

## Why

A stale or fabricated passing report must not advance tasks; competing coordinator processes must not lose updates or create multiple writers.

## Non-goals

R3–R5 implementation, security sandboxing, multi-host coordination, database migration, or weakening the existing verification, review and authority contracts.

## Known assumptions

Cooperative local POSIX processes and one filesystem. Coordinator-executed candidate checks are trusted execution; worker TDD fields describe history. Tests exercise public state and coordinator operations using actual Git/subprocesses. Runner checks can execute project code under existing delegated authority.

## Open questions

None blocking. Crash after Git FF and before state replacement is recovered by revalidating the same candidate on resume; this is not a cross-resource transaction or a power-loss durability guarantee.

## Human decisions

User: "commit and continue"; "update develop with main (preserve later inbox)"; "do not ask for permission I allowed all actions". Proceed with the stated scope and defaults without additional approval prompts. This does not turn unexecuted tests into evidence or authorize new semantic scope.

## E2E

Applicability: `not_applicable`. This kit has CLI and disposable-Git journeys in the ask-kit mandatory shell preset, with no product UI or production datastore. Subprocess contention and candidate integration are exercised there.
