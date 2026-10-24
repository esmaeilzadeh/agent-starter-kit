# CR-3 bug-fix route reassessment handoff

Updated: 2026-10-24. Workstream: `continuation-recovery`; task: `CR-3`.

## Why this note exists

The user challenged whether the corrected bug-fix approach should change how
CR-3 is handled. The concern is that a bug repair was treated as a feature
implementation, with a broad plan and guards being mistaken for defects that
must each produce a Red.

This note records that reassessment and the evidence to use next. It does not
amend the accepted intent, plan, test map, or authorization.

## Correct bug-fix route

For a reported bug, use the reporter's concrete context to reproduce the faulty
behavior against the existing contract. Add a focused failing assertion for
that reproduced behavior, make the smallest effective fix, and confirm Green.
Do not create Reds for passing guards or add tests for hypothetical failures.
When a request combines a bug repair with a behavior change, separate the
outcomes and route them independently.

## Keep the reproductions distinct

- `reproduction.md` records the original missing-state continuation bug: with
  retained TaskResult and review evidence, the scheduler restarted at the
  already implemented candidate instead of reconciling the missing state.
- CR-T60 is a separate reproduced consumed-receipt selection and stale-request
  atomicity defect. The handoff records valid behavior Reds for it in registered
  reports `e2a9dc4b3d5e41789117fae0b9623e93` and
  `f8207e36d1794b499e043ba263cacb32`.
- CR-T13 is a one-cycle reopen/history regression guard. It has no valid Red,
  claims no defect, and passes the current P0 Green. Do not manufacture a Red
  or use it to justify expanding CR-3.
- Other CR-3 cases have their own historical evidence. In particular, the
  incomplete report `b5e4fc3b34c14e5a93312d2744be9adf` collected only 8/12 cases
  and contributes no registered Reds. Use the per-case table in `handoff.md`;
  do not combine distinct cases into one bug without evidence that they are the
  same reported fault.

## Current plan and authorization boundary

The accepted CR-3 task covers coordinator finalization and historical evidence
recovery, including receipt lifecycle, read-only preflight, per-case Red
continuity, the narrow T21 exception, and a reviewed coordinator/verifier
upgrade. The user authorized continuing that plan through its normal task loop,
but the recorded authorization also says the approved What, Why, assumptions,
plan, and authority remain unchanged and excludes scope changes.

The latest discussion recommends reassessing whether this broad package is
needed for the actual reported fault. Do not silently replace the accepted plan
or discard contract-required evidence. Before changing CR-3 scope, identify the
specific reporter fault each retained behavior addresses, separate independent
defects from guards and integration evidence, and record the user's resulting
scope direction. Keep unrelated outcomes out of a focused bug repair.

## Observed state at handoff

- Branch: `agent/continuation-recovery`.
- CR-3 coordinator state: revision 29, `interrupted`, three interrupted
  attempts. `./ask status` labels the workstream stage `recorded`; that does not
  mean CR-3 reached its task terminal state.
- The prior P0 candidate has a registered 12/12 Green run, but the handoff
  records P1 acceptance/Green and read-only preflight, a fresh reviewed
  attempt-3-to-4 receipt and reopen/checkpoint, exact-candidate semantic review,
  and normal integration as remaining under the accepted plan.
- CR-4 remains pending. Do not admit it before CR-3 reaches its authorized
  terminal state.
- The task-routing later card is
  `.later/task-activity-routing-flows.md`; commit `f1bd714` added it.

## Resume checklist

1. Read this note, `handoff.md`, `continuation-authorization-2026-10-24.md`,
   `intent.md`, `plan.md`, and `.agents/ask/task-loop.md`.
2. Recheck the current branch, worktree, task state, run ledger, and exact
   candidate evidence before acting; the identities in older notes are not a
   substitute for live checks.
3. Do not target CR-T13 for Red. Do not label incomplete reports as valid Red.
4. Resolve the current bug-versus-plan question from concrete fault evidence.
   Preserve the accepted plan unless the user records a scope correction.
5. If the accepted plan remains in force, resume only its exact next authorized
   CR-3 gate. Do not broaden scope, start CR-4, or claim task completion early.

No tests were run for this documentation-only handoff.
