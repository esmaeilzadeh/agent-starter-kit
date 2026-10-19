# RF-02 independent preparation review

- Workstream: refactor-inner-loop
- Task: RF-02
- Candidate: 27920306a9619c2f180417732b13ff803410cc74
- Task base: 2f911b7768e27bb4c7af480dcf0b58bef5840755
- Reviewer: amended-plan-review
- Runtime: codex
- Model: gpt-6-astra
- Parent model: not exposed
- Verdict: REJECTED
- Boundary: ok

## Scope

Reviewed the complete task diff, accepted RF-006 requirements and PREP-01..06
obligations, preparation script, managed override, all six test methods and
their fixture, and recorded RF-02 red/final-green evidence. All three changed
paths belong to RF-02: _ask/skills/prepare-skills.sh,
_ask/skills/tdd-override.md, and _ask/tests/test_tdd_preparation_overlay.py.

## Findings

### RF02-01: Missing Cursor output can be reported as successful preparation

Severity: high. Location: _ask/skills/prepare-skills.sh, apply_tdd_override's
missing-file continue (lines 66-68).

An installer can exit zero and create only the primary .agents TDD file. The
script verifies that file, patches it, silently skips the absent Cursor file,
then prints ok and exits zero. RF-006 requires both installed views to carry
the override; the spec also rejects success when a required TDD output is
missing. PREP-01 always creates both views, so it cannot catch this outcome.

Resolution: validate the required installed-view outputs before reporting
successful TDD preparation. Preserve optional missing-skill semantics, but do
not claim a successful patched preparation with a missing required view. Cover
the partial-output scenario through the public prepare seam.

### RF02-02: PREP-02 does not exercise replacement or preservation on rerun

Severity: high. Location: _ask/tests/test_tdd_preparation_overlay.py:92-106
and the installer stub in setUp.

The test mutates the installed block, then invokes the same installer stub,
which overwrites both SKILL.md files with fresh upstream text. The production
replacement branch never sees the stale managed block. An implementation that
only appends a block, without removing the old one, would pass this test.

Resolution: make the second successful installer invocation preserve existing
installed files, seed stale managed content in both views, and assert exactly
one current block plus preserved surrounding upstream content. Verify a further
unchanged rerun remains byte-stable. The test must fail if replacement is
removed, without fixture/import/setup failures.

### RF02-03: The prepared guidance retains semantic conflicts

Severity: medium. Location: _ask/skills/tdd-override.md:1-3.

The managed body tells the agent to follow the task loop but does not explicitly
state that it supersedes upstream text excluding Refactor. The installed
document therefore retains conflicting directions despite the spec's explicit
precedence requirement. It also says to escalate every finding outside the
task boundary; the accepted contract parks broader behavior-preserving
refactors without blocking on their implementation.

Resolution: state the managed repository rules take precedence over upstream
conflicting loop/refactoring guidance. Distinguish broad behavior-preserving
proposals, which receive candidate-bound parked-card handoffs, from required
contract changes or ambiguous/unsafe corrections, which escalate. Retain the
canonical contract pointer and unrelated upstream text.

### RF02-04: Required PREP-02 Red evidence is absent

Severity: medium. Location: RF-02 traceability execution history.

The accepted plan requires behavior Red/Green for PREP-02. The case first appears
at 62a387efd49e37d5d38def1514fa830a89d8558c and passes in that phase-red run;
it passes again at the candidate. No recorded PREP-02 behavior-assertion failure
exists. A run named red does not supply Red for every collected case.

Resolution: establish genuine executed failing coverage for the accepted
replacement/idempotence behavior, then record green at the corrected final
candidate. Do not relabel the new obligation as regression or fabricate failure.

## Assertion and evidence assessment

- PREP-01: Actual final-green evidence exists; checks both fresh views, one
  managed block, canary content, canonical pointer, and unchanged manifest.
  Coverage remains insufficient for explicit precedence and partial installer
  output as described above.
- PREP-02: Actual final-green exists, but the fixture removes the condition it
  claims to exercise. Replacement assertion adequacy and TDD continuity rejected.
- PREP-03: Snapshot equality supports validation-only nonmutation for the
  represented prepared fixture. Production code bypasses installation and
  overlay application when SKIP_INSTALL=1.
- PREP-04: Nonzero installer handling now precedes stale-file checks, preserving
  the required failure. The stale-file regression has behavior-assertion Red at
  62a387e and final-green at this candidate with identical test source bytes.
- PREP-05: Missing optional skill plus installer failure exits successfully
  without fabricating either output, as the accepted optional policy requires.
- PREP-06: Zero installer exit without primary .agents output is refused even
  when stale Cursor output exists; the test also checks Cursor preservation.

Final-green run 5b6004bef86c4142b472c86470b02641 records all six cases passing
at this candidate. Inspected recorded runner logs and verified their output
digests; no mismatches were found. PREP-01 has a meaningful behavior-assertion
Red at e07c7a5 after fixture repair. Earlier broken-fixture attempts cannot
substitute for the relevant behavior evidence. Passing cases do not resolve
the counterexamples and evidence gap above.

## Review limit

No source edits or new test execution by this reviewer. This artifact records
independent rejection; it does not authorize task integration or RF-006 coverage.
