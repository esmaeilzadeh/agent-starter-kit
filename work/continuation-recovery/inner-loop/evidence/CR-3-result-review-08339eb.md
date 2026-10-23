# CR-3 result review and coder handoff

Date: 2026-10-23. Verdict: **REQUEST CHANGES**.
Reviewed executable candidate: `08339eb5bf9802cf815819bf3168f13c5296d9bd`.
Comparison: `5444191643ec050a6ed685fe22a93773bcae49ed...08339eb5bf9802cf815819bf3168f13c5296d9bd`.
Reviewer: `/root`, with independent read-only Standards and Spec reviews from
`/root/result_standards_review` and `/root/result_spec_review`. The primary
reviewer participated in the implementation; this report is not independent
overall implementation approval.

This note supersedes the preceding recommendation to introduce a broad
baseline-Green exception. That proposed user choice was premature and should
be disregarded. No such exception or acceptance change was approved.

## Exact continuation state

- Branch: `agent/continuation-recovery`; tracked worktree clean before this note.
- State revision: `27`; coordinator: `2c508ff4248f16a3e3121d33a0fae7297c9b378e`.
- CR-1/CR-2 integrated; CR-3 interrupted; CR-4 pending.
- Both `CR-3:attempt-1` and `CR-3:attempt-2` remain in interrupted history.
- Accepted plan digest: `a8c13188a26489e67173333ca4f69ac572f00836a3f32e77929ee82a1ff99025`.
- Source corrections are committed: `abead28` (T19 fixture runtime ownership)
  and `08339eb` (T10 process-exit coverage).
- Attempt 2 retains mapped Red `dab908b39596441086d57106b8c816ec` at `8e61c14`
  (T19 behavior assertion failed), Green `6b6471cfb6704129afaa5bb587f71f0d`
  at `abead28`, and Green `861e66d1fbce42859354f5b7a5b80317` at `08339eb`.
  The latest Green passed all eight selected CR-3 cases. This does not establish
  their missing historical Red obligations or authorize integration.

The later commit containing this note is documentation only. Its executable
review target remains the SHA above. This review did not change task state,
accepted authority, source, or integration status.

## Findings and required corrections

### R1 / P1: unsupported baseline diagnosis repeats the continuation trap

Current Green does not prove that the same behavior and assertions passed at
the original task baseline. The attempted T11 baseline probe copied the current
test file onto coordinator `2c508ff` and failed importing `checkpoint_run`.
That is neither baseline Green nor a valid behavior Red. Withdraw the claim
that all remaining mapped tests were proved Green at the task baseline.

CR-04 requires resuming the first unmet valid milestone. CR-05 prohibits
inferring Red from passing tests or source presence. The original handoff,
lines 32-35, explicitly forbids treating implemented current code as a fresh
task baseline. A continuation must not demand a new failure solely because
its current implementation is already Green.

Coder: build a per-case ledger for T10/T11/T12/T13/T21 identifying the original
task/slice base, immutable assertion source, relevant implementation commits,
registered run IDs, phase, outcome, failure kind, contract applicability and
assertion continuity. Distinguish retained/recoverable Red, genuinely missing
provenance, and newly discovered behavior defects. Current Green alone cannot
choose among these. Preserve every original report and its phase. In
particular, T12's failed `final_green` run `6a96d09a0d4c4394951b47fa33a14dd7`
cannot be relabeled Red, and all-pass Red `517f864631a845e082f9a73fa888ef30`
does not supply Red. Do not manufacture failures, weaken assertions, or
automatically reclassify tests to bypass the gate.

Only if that audit establishes a remaining contract conflict should a concrete,
case-specific independently reviewed amendment be proposed. Do not start with
a blanket baseline-Green waiver or ask the user to choose one before the audit.

### R2 / P1: consumed reconciliation blocks the next reopen

`_ask/scripts/inner_loop/attempts.py:50-87` always loads the fixed
`reconciliation-<task>.json` and checks it against the current transition.
`reopen_task()` invokes this before its normal reopen checks. The consumed
record still describes revision 22 and attempt 1 -> 2; state is now revision
27 with attempt 2 interrupted. A read-only call to `_reviewed_reconciliation`
on the current state reproduces `ProtocolViolation: attempt reconciliation
identity is stale or conflicts with coordinator state`.

Coder: distinguish an immutable historical receipt from a newly submitted
transition request, using attempt-specific identity and lifecycle. Keep prior
approved evidence intact. A consumed receipt must not block a later valid
reopen; a stale new request must still be refused. Add authentic regression
coverage for interrupt -> reopen -> interrupt -> reopen under valid reviewed
plan changes. Do not solve this by manually deleting accepted evidence.

### R3 / P2: T10 checks an outdated ledger snapshot

`_ask/tests/inner_loop_recovery.py:353` reads the ledger before the child starts.
Line 360 checks the child's newly generated run ID against that old list, so
the assertion passes even if the child inserted the entry before exiting.

Coder: reload the ledger after the report-publication crash and check its
actual contents. Preserve the existing real child exits and exact run identity,
phase, source and digest assertions. Establish that the assertion detects an
incorrect publication boundary rather than trusting the failpoint label.

### R4 / P2: reconciliation implementation exceeds accepted CR-3 ownership

The result modifies `attempts.py`, which CR-2 owns and the accepted CR-3
`owned_paths` list excludes (`inner-loop/tasks.yaml:28-49`). Stage 06 requires
work within the reviewed task assignment. Shared CR-07 requirements do not
themselves amend that assignment.

Coder: prepare the narrow ownership correction through the reviewed plan and
accepted-contract path. Preserve prior attempts and their original plan-bound
evidence. Do not broaden intent, waive TDD, or treat the old whole-plan evidence
as newly executed evidence under a new digest.

## Completion boundary

The T19 fix and T10's process-exit scenarios address real findings, but the
candidate is not approved overall. After the corrections, obtain fresh exact
candidate review, semantic traceability review and passing applicable checks;
integrate only through normal coordinator gates. CR-4 remains pending until
CR-3 integration. Product adoption and scheduling remain outside this handoff.

Continue already-authorized local diagnosis and correction without repeating
intent approvals. Ask the human only for an actual unresolved acceptance or
meaning change, with a concrete proposal and consequences.
