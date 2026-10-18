# Specification Challenge: refactor-inner-loop

## Model

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


## Second review of ade4444fd00fa13aef10d795a6c01de11ec9bec3

C-01 resolved: tagged drafts stay in persisted runtime review evidence throughout
active, blocked, escalated, and interrupted task work. Coordinator source commits
are deferred until all candidates integrate and no writer/resumable candidate
remains. C-02 resolved by LOOP-05. C-03 resolved by PREP-04 and PREP-06, including
nonzero installation with stale output in PREP-04. Their task assignments agree
with RF-02 and RF-03 ownership. Independently recomputed spec, plan, and graph
digests match the coordinator's supplied values.

### C-04 — Classify unchanged preparation behavior as regression

PREP-03 validation-only nonmutation, PREP-05 missing optional output, and PREP-06
zero-exit installation missing primary output already satisfy their described
outcomes in the current preparation script. They are marked new and the RF-02
plan requires behavior Red for each. Requiring an artificial failure would confuse
new test source with changed product behavior. Classify these unchanged scenarios
as regression coverage, consistent with LOOP cases, and retain executed current
candidate evidence plus independent assertion review. Keep new override behavior
and the stale-output installer-failure fix under actual behavior Red/Green.

Second verdict: REJECTED solely pending C-04 metadata/evidence wording correction.
The RF-001..004 classification authorization remains valid. No implementation or
behavior-case execution has been performed.


## Final exact-contract decision

APPROVED for planning at commit d754f11c4a2b4568ae37f5753f41389edf14ae04.

C-04 resolved: PREP-03/05/06 now correctly classify unchanged behavior as
regression coverage. PREP-01/02/04 retain actual behavior Red/Green obligations;
the Plan explains the distinction. C-01, C-02, and C-03 remain resolved.
RF-001..004 review-only classification is independently APPROVED under
_ask/policies/delegation.md. There are no unresolved challenge findings.

Independently recomputed canonical digests:

- spec_digest: 6909c47a0698ce79b99c87f7ac6997e7d0136c3d3a03b12baa6780e5d760cc37
- plan_digest: b5cf5ecd89eab56758e9fd29475347064500b3bced8dad3c0b3cc4ac8ab69e49
- graph_digest: 574d65df8f5811094c250a24038ce16edcacfb7b6aa1b4020cdc12ad791d78f4

Graph and spec/test mapping validation passed. This is metadata validation and
independent Plan approval, not implementation verification or execution evidence.
The decision and assessments are recorded in plan-review.json. Stop at Plan as
requested; normal implementation authority and candidate evidence remain future
gates. No production code, behavior tests, task runtime state, or delivery refs
were changed by this review.

## Spec-change amendment review

The amendment at `2b2f3a46040216da6b44333df3cf4a779786b2b5` was independently
reviewed by `amended-plan-review` (gpt-6-astra, codex, high). The first review
identified a stale test-plan digest; the coordinator corrected it and committed
the exact reviewed contract at `88b314597f9b39cba1da895c7e86bb6da8cb6faf`.
The reviewer confirmed the final spec/test-plan binding and approved the amended
intent, task ownership, test mappings, continuation boundaries, and authorized
implementation/merge/push scope.

Review-only criteria RF-001..004 and RF-008..009 are APPROVED for independent
semantic review under `_ask/policies/delegation.md`. The added criteria require
walkthroughs of combined option-and-comment responses, runtime capability for
the current question, fallback behavior, and explicit plan stops. Final digests:

```text
spec_digest: dd5dc51976d5796b86605b93e33b44a562a7b575e4d57a684fc0a91473c4ad3d
plan_digest: aa1e74ae33c96e95d1b7c7fc529d603f185fe90a243597f81048963304f4089b
```
