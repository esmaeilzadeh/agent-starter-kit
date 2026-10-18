# Specification Challenge: refactor-inner-loop

## Review identity and scope

Reviewer: refactor-spec-challenge (/root/refactor_spec_challenge).
Model: gpt-6-astra. Runtime: codex. Reasoning effort: high.
Identity supplied by the coordinator from the fixed kit-03-spec-challenge
agent-type launch configuration. Parent model: not exposed. The configured Spec
default is gpt-6.1-sol; that configuration is not evidence of actual parent identity.

This is an independent planning review under 03 Spec Challenge, using
writing-for-agents in embedded mode. Inspected the proposed intent, specification,
criterion metadata, Plan, test plan and TaskGraph; checked the current preparation,
retry, task integration/resume, installer, and traceability contracts.
Implementation, executable tests, task state, integration, and delivery remain
outside this review. The user authorized finishing Plan and stopping.

## Initial verdict

REJECTED pending the bounded corrections below. None changes the user's What/Why
or requires a new product decision. No final exact-digest approval is issued yet.
The proposed review-only metadata remains PENDING until the coordinator records
the independent classification authorization below and recomputes the contracts.

## Findings

### C-01 — Park cards without invalidating resumable task candidates

The specification allows the coordinator to commit cards after a writer
"integrates or stops". A stopped writer may still have a resumable candidate
based on the earlier coordinator HEAD. An independent card commit can make that
candidate ineligible for FF integration: read_candidate requires current HEAD to
be an ancestor of the candidate. Source repair also uses recorded coordinator_sha,
so a later dirty-source resume can rewind unregistered coordinator commits.

Keep drafts and publication status in durable review/runtime evidence while a
resumable task exists. Define a safe terminal publication boundary, preferably
when all task integrations finish, with no active writer or pending candidate.
Specify that interruption before publication retains a handoff, and normal
workstream integration publishes the attributed tagged cards. Do not invent a
new state mutation mechanism or perform out-of-band commits during the task loop.

### C-02 — Explicitly test approved candidates whose checks fail

RF-005 includes failed-check refusal, but LOOP-01 tests rejected review, LOOP-02
stale review, LOOP-03 successful checks, and LOOP-04 retry dispatch. Those cases
can all pass while a validly reviewed candidate incorrectly integrates despite a
failed check. Add a separately named public-CLI scenario with current APPROVED
review and a failing required check; assert refusal, unchanged coordinator source,
and no integrated task state. Assign it to RF-03 and RF-005 in the exact test map.

### C-03 — Separate installer failure from missing required output

PREP-04 says the installer "fails or produces no required skill view", which
leaves one distinct failure path untested. Use separately named cases for
nonzero installation and zero-exit installation missing one required skill view;
avoid unsupported dynamic subtests. For the nonzero case, preexisting stale
prepared output is a useful counterexample: current prepare can report success
when matching old files survive an installer failure. Both required paths must
fail explicitly. Keep optional-skill handling separate and preserve upstream pins.

## Review-only classification authorization

Under _ask/policies/delegation.md, I independently APPROVE review-only
classification for each of the following criteria. This authorization is about
evidence type, not a claim that future implementation already satisfies it:

| Criterion | Classification decision | Required independent evidence |
| --- | --- | --- |
| RF-001 | APPROVED | Walk a behavior slice through Red, Green, Refactor, independent task review, correction, Verify, and integration; inspect outer flow for duplicated unconditional Refactor. |
| RF-002 | APPROVED | Walk valid local findings, broad horizontal proposals, and evidence-backed withdrawal of mistaken findings; verify local cleanup cannot be waived by advisory labeling. |
| RF-003 | APPROVED | Inspect coordinator-owned draft/publication instructions and interruption handoff against task ownership and FF boundaries; publication timing must address C-01. |
| RF-004 | APPROVED | Walk existing-spec behavior corrections, structural refactors, and necessary contract redesign; only the latter changes the accepted contract through Spec Change. |

These are semantic agent instructions implemented through protocol text and
existing evidence/handoff mechanisms. Literal text assertions cannot establish
agent judgment. If implementation adds executable publication, classification,
or state-transition behavior, its behavior needs explicit test obligations and a
reviewed amendment; this classification does not exempt that new behavior.

## Accepted design choices

- Preserve implement/debug/integrate/blocked and existing bounded retry counts;
  document their correction/TDD semantics instead of adding persistent sub-states.
- Keep all valid local refactors required, permit an empty Refactor pass when no
  cleanup applies, and allow evidence-backed withdrawal of mistaken findings.
- Park broad behavior-preserving proposals tagged refactoring; necessary redesign
  uses Spec Change and existing-spec defects use TDD correction.
- Test preparation and install/upgrade through public commands and disposable
  consumers. The TDD override preserves pinned upstream input and unrelated text.
- Integration checks for unchanged runtime behavior are regression obligations;
  they cannot be used as proof of newly introduced semantic runtime behavior.
- RF-01 has no executable cases; RF-02 owns preparation behavior; RF-03 owns
  generated delivery and integration regression scenarios. Dependencies serialize
  shared workflow effects and every planned executable case has one task owner.
- Every supported runtime must resolve the canonical task-loop contract; generated
  stage parity and consumer-overlay preservation are appropriate delivery checks.

## Final contract review

Pending coordinator corrections, replacement of PENDING classification decisions,
and final canonical spec/test-plan/TaskGraph digests. No plan-review.json approval
has been written. No behavior tests or implementation verification were run.
