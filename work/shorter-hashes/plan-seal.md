# Consolidated plan seal

## Task 9 impact correction amendment (2026-10-29)

**PROPOSED — independent review and human decision pending.** The proposal in
`task9-impact-scope-amendment.md` adds the existing, already-bound
`.agents/ask/workflow_refs/impact.py` source to serialized Task 9 ownership so
case 9/3 can enforce the accepted transition-wide revision assessment. It
preserves the sealed spec, intent, case definitions, authority rules, and
acceptance criteria. The Task 4/Task 9 shared path is explicitly sequential;
Task 9 runs after Task 8, which depends transitively on Task 4. Do not implement
the production correction or claim the amended plan accepted until the
independent exact-revision review and human decision are recorded and the plan
is registered again.

## Current Task 6 amendment (2026-10-29)

Task 6's source-binding amendment is authorized under the user's delegated
confidence threshold, recorded in `task6-binding-authorization.md`. Cases `6/1`
and `6/2` add checkpoint and recovery readers; `6/1` also adds the attempt
controller. This changes source coverage only. Independent review and renewed
registration of this exact test plan are pending; Task 6 implementation must
wait for them. Historical amendment statuses below describe earlier seals.

Status: **HISTORICAL SEAL; TASK 2 AMENDMENT PENDING REVIEW**. The original
sealed plan had 0 specification and planning blockers. Task 1's later
classification amendment is accepted and registered. Task execution is paused
while the Task 2 classification amendment receives exact-revision review and
registration.

- Workstream: `shorter-hashes`.
- Requirements baseline: sealed specification revision **7**, all **18** criteria;
  exact source/digests in `spec-seal.md`.
- Exact reviewed planning source: `02ad31b6e5ef5130986a920f943788cbbe970631`.
- Consolidated plan: `plan.md`; producer/consumer boundary: `surface-inventory.md`.
- Work breakdown: **10 ordered tasks**, `inner-loop/tasks.yaml`.
- Test contract: **39 planned cases**, **14 supported unittest runners**,
  all required criterion/type obligations and exact one-task case ownership.
- Measurement: **3 frozen journeys**, **14 real source files**, exact tokenizer
  version/encoding and accounting in `benchmark/baseline.json` and requirements.
- Independent review: `plan-review.md` and `traceability/plan-review.json`;
  reviewer `/root/shorter_hashes_challenge_r6`, Codex, `gpt-6.1-sol`, medium effort.
- Review decision: **APPROVED**, P1/P2 closed and no remaining blocker.
- Coordinator registration: `./ask traceability accept-plan`, recorded by `/root`.
- Coordinator authority ref: `refs/ask/accepted-tests/shorter-hashes`.
- Registered authority commit: `e1ca2a523c5417687479c09ffc1bf6c1cc337763`.
- Candidate-side exact accepted contract: `traceability-accepted.json`.
- Canonical spec digest: `9bd9107a4d9490528178e2ac204c44926aa9b0e8675fd58f042e2a6fa2a77a3e`.
- Original sealed test-plan digest: `40e2258c48f5e9dcfcaa55f0aa09808b8c2d3232b850db4752e852abaca3680b`.
- Canonical TaskGraph digest: `e40e35263b303fc5926fa4ac96a29480614febd5b0679f2f88a269088d7f9ccb`.

The original independent decision also bound exact plan/inventory/benchmark/requirements
and spec-seal file digests. All were checked against the reviewed commit and
checkout before registration. Any change to these bound inputs makes the plan
seal stale and requires renewed independent review/registration as applicable.
The earlier rejected plan/review is retained in Git at `8f40b6c` and
`8315ae4`/`850c168`; it was corrected rather than accepted conditionally.

## Amendments and current authority

The Task 5 classification amendment reclassifies `5/1` and `5/2` as
regressions; `5/3` remains new. It was independently reviewed and registered
before the continuation-process correction. The current accepted-tests contract
revision is `447bac6bb948fa53420df882883bc4962716e619`, with test-plan digest
`cc24b686bf3f0de55e6644ceb47ffe583511e0aefdb521448da5dd7828e62d5a` and
TaskGraph digest `e40e35263b303fc5926fa4ac96a29480614febd5b0679f2f88a269088d7f9ccb`.

The Task 1 amendment changed only case `1/2` from `new` to `regression`, based
on its pass at the recorded pre-implementation Red revision. Case `1/1` remains
new. The amendment was independently reviewed and registered; the current
accepted contract is pinned in `traceability-accepted.json`.

The Task 2 amendment proposes changing only cases `2/1` through `2/9` from
`new` to `regression`, based on all nine passing at the recorded pre-implementation
baseline. It preserves the spec, scenarios, assertions, source bindings, runners,
and TaskGraph. Independent review and renewed coordinator registration are pending.

Structural contract/graph checks, all criterion/type and case-owner mappings,
task-time declared input availability, all frozen source hashes, and independent
semantic review passed for the historical seal. At that time, the coordinator
authority pin matched the reviewed obligations. No future test's assertion result
was claimed by those checks.

## Current execution boundary

The user explicitly extended the endpoint through final acceptance. The
approved intent remains byte-identical and its existing confirmation remains
valid. Implementation and TaskGraph execution may proceed after the current
plan amendment is reviewed and registered. Completion requires per-task Red,
Green, Refactor, independent review, integration evidence, aggregate
verification, and final acceptance. No savings claim is made until Task 10
produces the required benchmark evidence.

Plan registration establishes planning authority, not passing implementation or
final-completion evidence. Implementation must produce current Red/Green,
independent candidate reviews, applicable regressions, integration receipts and
full final verification before workstream Accept.
