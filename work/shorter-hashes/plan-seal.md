# Consolidated plan seal

Status: **SEALED**. Open specification blockers: **0**. Open planning blockers: **0**.

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
- Canonical test-plan digest: `cc24b686bf3f0de55e6644ceb47ffe583511e0aefdb521448da5dd7828e62d5a`.
- Canonical TaskGraph digest: `e40e35263b303fc5926fa4ac96a29480614febd5b0679f2f88a269088d7f9ccb`.

The independent decision also binds exact plan/inventory/benchmark/requirements
and spec-seal file digests. All were checked against the reviewed commit and
checkout before registration. Any change to these bound inputs makes the plan
seal stale and requires renewed independent review/registration as applicable.
The earlier rejected plan/review is retained in Git at `8f40b6c` and
`8315ae4`/`850c168`; it was corrected rather than accepted conditionally.

## Reviewed amendments

The Task 5 classification amendment reclassifies `5/1` and `5/2` as
regressions; `5/3` remains new. A Task 1 amendment reclassifies `1/2` as a
regression based on its pass at the recorded pre-implementation Red revision;
`1/1` remains new. Both amendments preserve the spec, scenarios, assertions,
source bindings, runners, and TaskGraph and require exact-revision review and a
renewed coordinator accepted-tests pin before execution.

Structural contract/graph checks, all criterion/type and case-owner mappings,
task-time declared input availability, all frozen source hashes, and independent
semantic review passed. The coordinator authority pin matches the independently
reviewed obligations. No future test's assertion result is claimed by these checks.

## Current execution boundary

The user explicitly extended the endpoint through final acceptance. The
approved intent remains byte-identical and its existing confirmation remains
valid. Implementation and TaskGraph execution may proceed after the current
reviewed plan amendment is registered. Completion still requires per-task Red,
Green, Refactor, independent review, integration evidence, aggregate
verification, and final acceptance. No savings claim is made until Task 10
produces the required benchmark evidence.

Plan registration establishes planning authority, not passing implementation or
final-completion evidence. Implementation must produce current Red/Green,
independent candidate reviews, applicable regressions, integration receipts and
full final verification before workstream Accept.
