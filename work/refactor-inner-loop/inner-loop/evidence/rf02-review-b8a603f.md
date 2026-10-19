# RF-02 independent preparation review

- Workstream: refactor-inner-loop
- Task: RF-02
- Candidate: b8a603f5c3b5d3a141bc089d1873a1d6ab47f4de
- Task base: 2f911b7768e27bb4c7af480dcf0b58bef5840755
- Reviewer: independent RF-02 review subagent
- Runtime: codex
- Model: gpt-6-luna
- Parent model: not exposed
- Verdict: REJECTED
- Boundary: ok

## Scope

Reviewed the full RF-02 candidate diff from its task base, accepted RF-006
requirements and PREP-01..06 mappings, implementation and override, candidate
test assertions, and traceability history. The changed paths are
`_ask/skills/prepare-skills.sh`, `_ask/skills/tdd-override.md`, and
`_ask/tests/test_tdd_preparation_overlay.py`; each matches RF-02's owned paths.

## Findings

### RF02-B8A-01: PREP-02 still lacks its required behavior Red evidence

Classification: local structural suggestion.

Location: RF-02 task TDD history and traceability records.

The strengthened PREP-02 test now stales the managed text in both `.agents` and
`.cursor`, uses an installer stub that writes views only on the first invocation,
checks the upstream canary and one current marker pair in both views, rejects
stale text, then verifies byte stability on a third prepare. These assertions
address the previous review's test-quality finding.

However, the accepted plan requires behavior Red/Green for PREP-02. The only
candidate-bound run for this test source is final-green
`c2d03b03784d41ab9e4e5e45a6ce47f3`, where PREP-02 passes. The prior red-phase
run `6877d909b752480bbd757ec3d676c169` has PREP-02 passing, and its recorded
source digest predates the strengthened two-view/third-run assertions. Earlier
red runs also fail on PREP-01 or PREP-04, not PREP-02. Thus the current PREP-02
behavior assertions have no recorded behavior-assertion Red, despite the prior
review explicitly requiring one after the test was strengthened.

Suggested fix: execute the strengthened PREP-02 case against a candidate where
managed-block replacement is absent, record the PREP-02 behavior assertion
failure, then record final-green against the corrected candidate. Ensure the
Red source digest corresponds to the current PREP-02 assertions; a run labeled
`red` where PREP-02 passes does not satisfy the requirement.

## Assertion and evidence assessment

- PREP-01: Candidate final-green passes both prepared-view checks; the repository
  override explicitly establishes precedence and points to the canonical task
  loop. Candidate test also rejects an absent Cursor view after installer
  success.
- PREP-02: Strengthened assertions now cover both views, non-overwriting second
  installer call, preserved canaries, one current block, stale text removal,
  and byte-stable third run. Candidate final-green passes. Required Red remains
  absent as described above.
- PREP-03: Candidate final-green passes snapshot checks that SKIP_INSTALL does
  not mutate views or manifest.
- PREP-04: Behavior Red at `78fe4007a21b4ff0b537f5d63ea5c290` captures the
  required installer returning nonzero while stale outputs exist; candidate
  final-green passes.
- PREP-05: Candidate final-green verifies failed optional installation does not
  fabricate skill views.
- PREP-06: Candidate final-green verifies zero installer exit without the
  required `.agents` output fails even with an old Cursor view.
- Traceability candidate and final-green source SHA are bound to
  `b8a603f5c3b5d3a141bc089d1873a1d6ab47f4de`; the run reports all six cases
  passed and its recorded output digest is present. Passing PREP-02 does not
  replace the missing required Red.

## Suggested fixes

Complete the PREP-02 Red/Green evidence cycle and request a fresh independent
review on the resulting candidate. No source behavior changes are suggested.

## Parked refactor handoffs

None.

## Residual risks

No out-of-scope paths were found. PREP-02's assertions now cover the previously
identified multi-view replacement and idempotence cases, but the task's required
TDD continuity remains incomplete.

## Review verdict

REJECTED. Boundary is valid; all changed paths are RF-02-owned. Do not integrate
this candidate until the PREP-02 Red/Green evidence gap is resolved and fresh
review approves the updated candidate.
