# RF-02 independent preparation review

- Workstream: refactor-inner-loop
- Task: RF-02
- Candidate: c479341b1ee2de41826291bbd5390bff194c41c6
- Task base: 2f911b7768e27bb4c7af480dcf0b58bef5840755
- Reviewer: independent RF-02 review subagent
- Runtime: codex
- Model: gpt-6.1-sol
- Parent model: not exposed
- Verdict: REJECTED
- Boundary: ok

## Scope

Reviewed the candidate diff from the task base, the accepted RF-02 plan and
RF-006 mapping, preparation implementation and override, PREP-01..06 assertions,
and task traceability records. Changed paths are `_ask/skills/prepare-skills.sh`,
`_ask/skills/tdd-override.md`, and `_ask/tests/test_tdd_preparation_overlay.py`;
all are within RF-02 owned paths.

## Findings

### RF02-C479-01: PREP-02 still does not cover replacement in both views or a stable rerun

Classification: local structural suggestion.

Location: `_ask/tests/test_tdd_preparation_overlay.py`,
`test_repeated_prepare_replaces_managed_override`.

The controlled installer correctly leaves files untouched after its first run,
so the second call now reaches the production managed-block replacement logic.
However, the test changes `STALE OVERRIDE` only in the `.agents` view. The Cursor
view retains a correct block from the initial run, so its post-run assertion
does not demonstrate replacement there. The test also does not verify that
surrounding upstream content survives replacement or that an unchanged third
prepare leaves both files byte-stable. This falls short of the previous review's
specific resolution for PREP-02 and leaves idempotence/replacement assertions
weaker than the accepted scenario's claim for both installed views.

Suggested fix: stale the managed body independently in both views while leaving
surrounding upstream canaries in place; after the second run, assert each view
has exactly one current managed block, no stale text, and intact canaries. Save
both resulting byte sequences, run prepare once more with the non-overwriting
installer, and assert byte equality.

### RF02-C479-02: PREP-02's updated behavior is not captured as a Red/Green cycle

Classification: local structural suggestion.

Location: RF-02 task traceability evidence (`inner-loop/results/RF-02.json` and
`traceability/runs/`).

The accepted plan requires behavior Red/Green for PREP-02. Run
`6877d909b752480bbd757ec3d676c169` is marked `red`, but the PREP-02 case passed
there; its only behavior-assertion failure was PREP-01. The earlier PREP-02
failure gap therefore remains for the stronger fixture now claimed to verify
replacement. The candidate's `final_green` run proves all six current cases
pass, but is not paired with a failing execution of the current PREP-02
assertions.

Suggested fix: after strengthening PREP-02, run its exact assertion against a
candidate where managed-block replacement is absent and record a behavior
assertion failure, then capture final-green at the corrected candidate. Do not
infer PREP-02 Red from a phase named `red` when that case passed.

## Suggested fixes

Complete both task-local findings above and obtain fresh review on the changed
candidate. The findings concern RF-02-owned test/evidence only.

## Parked refactor handoffs

None.

## Residual risks

- PREP-01 now requires both installed views and the override explicitly gives
  repository rules precedence over upstream text; those requested corrections
  are present.
- PREP-04 immediately treats a nonzero required installer exit as failure,
  regardless of stale outputs.
- PREP-05 preserves optional missing-skill behavior without fabricating views.
- PREP-06 rejects zero-exit installation when the required primary `.agents`
  output is absent, including when an old Cursor view exists.
- PREP-03 snapshots the prepared views and manifest around `SKIP_INSTALL=1`;
  all are unchanged.
- The candidate-bound final-green traceability run records all six cases
  passing. These positives do not resolve the PREP-02 coverage and TDD findings.

## Review verdict

REJECTED. Boundary is valid; no path is outside RF-02 ownership. Do not integrate
this candidate. Resolve the local findings, rerun applicable checks, commit the
corrected candidate, and request a fresh independent review.
