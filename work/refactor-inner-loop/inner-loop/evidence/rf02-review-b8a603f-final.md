# RF-02 independent preparation review

- Workstream: refactor-inner-loop
- Task: RF-02
- Candidate: b8a603f5c3b5d3a141bc089d1873a1d6ab47f4de
- Task base: 2f911b7768e27bb4c7af480dcf0b58bef5840755
- Reviewer: independent RF-02 review subagent
- Runtime: codex
- Model: gpt-6-luna
- Parent model: not exposed
- Verdict: APPROVED
- Boundary: ok

## Scope

Reviewed the complete RF-02 candidate diff from the task base, accepted RF-006
requirements, PREP-01..06 mappings and assertions, preparation implementation,
managed override, task TDD result, and candidate-bound test artifacts. Changed
paths are `_ask/skills/prepare-skills.sh`, `_ask/skills/tdd-override.md`, and
`_ask/tests/test_tdd_preparation_overlay.py`. All are inside RF-02 owned paths.

## Findings

No valid task-local findings, existing-spec behavior defects, required redesign,
or broader-refactor proposals remain.

## Assertion and evidence assessment

- **PREP-01:** Candidate `b8a603f` final-green run
  `c2d03b03784d41ab9e4e5e45a6ce47f3` passes. The test verifies both installed
  views preserve upstream canaries, receive the canonical task-loop pointer and
  Red -> Green -> Refactor guidance, contain exactly one managed block, and
  leave the manifest unchanged. It also checks that successful installation
  without the required Cursor view is rejected. The override explicitly gives
  repository task-loop rules precedence over conflicting upstream instructions.
- **PREP-02:** The controlled installer writes both views on its first call and
  leaves them untouched thereafter. The test replaces managed content in both
  views with stale text; after the second prepare it checks both canaries, one
  current marker pair, current override text, and absence of stale text. The
  third prepare must leave both files byte-identical. All assertions pass in
  candidate final-green run `c2d03b03784d41ab9e4e5e45a6ce47f3`.
- **PREP-02 Red/Green continuity:** Immutable test-only candidate
  `b5c069742531a3576e52eb213ddbc61530597e4b` is based directly on RF-02 task
  base `2f911b7768e27bb4c7af480dcf0b58bef5840755`. Its PREP-02 test source is
  byte-identical to candidate `b8a603f` (digest
  `0c31ee5f5cbfc2a13cfacbfae39fdac5de61571703cf9766eb9aed3634aad156`). The
  traceability result `3745b4b1f9184eff8abe8c4cfcdb4e5e` binds that source and
  candidate SHA; PREP-02 is a `behavior_assertion` failure because the baseline
  leaves stale managed override content. The candidate-bound final-green run
  above passes PREP-02. This satisfies the accepted PREP-02 Red/Green obligation.
- **PREP-03:** Candidate final-green passes validation-only `SKIP_INSTALL=1`
  snapshot assertions for installed files and manifest.
- **PREP-04:** Required-install failure with stale output has behavior Red at
  `78fe4007a21b4ff0b537f5d63ea5c290`; candidate final-green passes. The
  implementation immediately treats a nonzero installer exit as failure.
- **PREP-05:** Candidate final-green verifies a missing optional skill remains
  unfabricated on installer failure.
- **PREP-06:** Candidate final-green rejects a zero-exit install without the
  required primary `.agents` output, even when an old Cursor view exists.
- Candidate final-green run `c2d03b03784d41ab9e4e5e45a6ce47f3` is bound to
  `b8a603f5c3b5d3a141bc089d1873a1d6ab47f4de`, uses the accepted spec and plan
  digests, and records all six PREP cases passing with output digest
  `024594ee5c7f2f9c2380f1adacc8c621767872dd61709d5b8980fdd194a97907`.

## Suggested fixes

None.

## Parked refactor handoffs

None.

## Residual risks

No RF-02-specific residual risk blocks task integration. Review is limited to the
accepted RF-02 task scope; it does not authorize the outer workstream's final
verification or acceptance.

## Review verdict

APPROVED. Boundary is valid; all changed paths match RF-02 ownership. The
candidate has passing final-green evidence for all planned PREP cases and
candidate-appropriate Red/Green evidence for PREP-01, PREP-02, and PREP-04.
