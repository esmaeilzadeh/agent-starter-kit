# Specification Change Proposal

## Current specification

The accepted candidate-integrity requirement requires normal task integration to
run the recorded coordinator's verifier against the immutable task candidate and
to reject unreviewed changes to accepted obligations.

## Proposed change

Add criterion EM-019: if the coordinator approves a contract amendment after a
task's recorded base, integration must keep verifier code and imports pinned to
that base while deriving the CheckPlan and accepted obligations from the
candidate. The candidate's accepted-contract document must match coordinator
authority and candidate-only contract changes remain rejected.

## Why the change is needed

A reviewed ownership amendment was accepted while RWB-107 was blocked for that
amendment. The candidate and coordinator authority then held the same new pin,
but the recorded task base held the prior pin. Integration used the prior base
for both verifier code and accepted-contract lookup, rejecting the reviewed
candidate before its required checks ran.

## Impacted artifacts

`specs/current/revising-workbench.json`, `work/revising-workbench/test-plan.json`,
`work/revising-workbench/inner-loop/tasks.yaml`, the matching plan table,
traceability review and acceptance records, and RWB-107's candidate evidence.

## Impacted workstreams

RWB-107 only. The new obligation is assigned to its existing serialized task and
does not change later task dependencies.

## Migration / transition notes

Keep the verifier implementation snapshot pinned to the task base. Resolve
accepted obligations from the candidate pin and compare them with the external
coordinator authority ref. The source fix and regression test are already
committed on the workstream branch; integration will use a refreshed TaskResult
and exact-candidate review.

## Acceptance criteria for the change

- A candidate with a reviewed post-base amendment matching coordinator authority
  passes detached task verification with verifier code bound to the task base.
- The CheckPlan remains candidate-derived, and ordinary unamended integration
  passes.
- Candidate-only obligation changes remain rejected by the existing authority
  checks.

## Decision

Approved by the human instruction: “fix the main workflow first, then continue.”


## Additional workflow verification finding

The first detached integration attempt passed every static command but failed the
final candidate-integrity check. `_ask/tests/test-sync-runtime-agents.sh` ran with
`ASK_WORK_ID=revising-workbench`, so its final sync applied the work-specific
reviewer-model overlay and left `.codex/agents/kit-07-review.toml` modified in
the disposable candidate checkout. The candidate verifier correctly detected that
write and refused integration. This is test-fixture leakage: the script exercises
temporary model/risk overrides but did not restore generated outputs afterward.

## Additional proposed change

Add criterion EM-020 and test RWB-CANDIDATE-SYNC-CLEAN. Preserve all four
generated review-agent projections at test start and restore those exact files on
all exits. The new integration case runs the real shell check in a child detached
candidate worktree with the work-specific override active, then asserts both a
successful check and a clean worktree. Add `_ask/tests/test-sync-runtime-agents.sh`
to RWB-107 ownership and the integration case's source list.

## Additional impact and alternatives

Impacted artifacts are the canonical spec, test plan, TaskGraph, plan, this
proposal, `_ask/tests/test-sync-runtime-agents.sh`, and
`_ask/tests/test_traceability_entrypoints.py`. The change does not weaken the
immutable candidate gate or hide generated paths from it. Changing the verifier
to ignore generated paths would allow unrelated projection changes through, so
the test itself must restore its temporary outputs.

## Authority

The user's explicit instruction was “fix the main workflow first then continue.”
This additional change fixes the candidate-integrity false failure discovered
while executing the required integration gate for that repair.

## Second detached integration finding

After EM-020's sync check passed, detached verification found that
`_ask/tests/test-askit-first-run.sh` inherited the verifier's `ASK_ROOT` into a
temporary consumer. Its successful first-run overlay rewrote
`.codex/agents/kit-07-review.toml` in the candidate. This is a separate test
harness environment leak from the sync script's temporary generated outputs.

## Second proposed change

Extend EM-020 and RWB-CANDIDATE-SYNC-CLEAN to execute the first-run consumer test
in the disposable candidate with `ASK_ROOT` inherited, and assert that the
candidate remains clean. Update the test script to clear the verifier-only root
before interacting with its non-git and temporary consumer directories. Keep
sync projection restoration and its forced-failure case as already accepted.

Impacted artifacts are the canonical spec, test plan, TaskGraph, plan, this
proposal, `_ask/tests/test-askit-first-run.sh`, and
`_ask/tests/test_traceability_entrypoints.py`. The test must also bind
`ASK_ROOT` to its child worktree so nested sync commands cannot target the
outer verifier checkout.

The user's instruction remains: “fix the main workflow first then continue.”
This second additive change addresses another required static check that mutates
the candidate during the same detached integration gate.
