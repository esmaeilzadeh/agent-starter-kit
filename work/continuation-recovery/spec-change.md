# Proposed change: recover task execution across continuations

Status: accepted requirements for the requested planning seal; execution stopped.
Revision 2 applies review R1–R4 under the explicit human sealing direction.
This is the single requirements baseline for the supplemental recovery plan.

## Current specification

`.agents/ask/task-loop.md` requires real Red → Green → Refactor, exact candidate
review and evidence-gated integration. `_ask/docs/inner-loop-evidence.md` defines
local runtime state, results and evidence. The product specification remains
`specs/current/shorter-hashes.json`, revision 7; none of its criteria changes.

State writes are atomic and locked, but `ensure_state`/`run_once` initialize a
missing state at current HEAD. Neither reconciles retained results and previous
execution before starting a pending task. Runtime evidence can be ignored by
Git. Atomic local storage alone does not make a continuation recoverable after
loss or replacement of that storage.

## Evidence and diagnosis

`reproduction.md` records a failing disposable-repository replay of the actual
scheduler: preserve TaskResult/review, remove state, run again. The task restarts
at its implemented candidate. No production files were changed for the replay.

Ranked explanations considered:

1. Missing state causes fresh initialization at HEAD: predicts the replay starts
   the executed task with its Green candidate as base. Observed.
2. All earlier execution evidence was lost: predicts no retained TaskResult or
   review. Contradicted by both the replay and current workstream evidence.
3. The test was always a regression: predicts no earlier failing behavior run.
   Contradicted by Task 2's retained review and implementation commits.

The demonstrated defect is missing reconciliation and durable recovery, not an
absence of historical Red or a requirement to loosen the integration gate.
Legacy artifacts alone still do not prove current integration eligibility.

## Accepted repair requirements

Canonical acceptance criteria are CR-01–CR-08 in
`specs/current/continuation-recovery.json`. Revision 3 isolates the repair under
its own work ID and branch after the user selected the current product branch
as base. `bootstrap.md` replaces the earlier combined-queue design with normal
repair initialization and a later explicit reviewed product adoption handoff.
`checkpoint-design.md` fixes retention and coordinator finalization boundaries.

This planning revision resolves R1–R4 without changing the approved product
intent or authorizing implementation. The user's explicit scope and stop are
recorded in `authorization.md`. Only continuation-recovery is registered.
