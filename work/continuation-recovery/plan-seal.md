# Sealed continuation-recovery plan

Status: **SEALED — STOP BEFORE IMPLEMENTATION**. Date: 2026-10-22.

The user directed “apply all review changes and seal the plan and stop”, then
selected current branch (“rec”) as the base for a separate branch and fresh
context. `authorization.md` records that scope; `AGENTS.md` now requires this
base choice, separate branch and isolated context for urgent interrupts.

## Exact contract and independent decision

- Workstream: `continuation-recovery`; branch: `agent/continuation-recovery`.
- Selected source base: `d04b3a4e515105df8cdf703f2fa0a28895f1524d`.
- Reviewed contract source commit: `68ca29caf9cc06a5460157685bacba0bef7b3f97`.
- Acceptance-record commit: `da2e64eb705d70751c99a2497bff67ee6d51cf89`.
- Reviewer: `/root/isolated_continuation_recovery/exact_plan_review`.
- Decision: APPROVED, no blockers; record: `traceability/plan-review.json`.
- Review file SHA256: `3fb8ed81184fd46fc82641f81ac4fd262e398d89aa7600b352dac9d03db67020`.
- Canonical spec digest: `02dcf36a73bbaf4c100e413854e823518f14d3dcbed34fe47a333d8e65790cf1`.
- Canonical test-plan digest: `edbba36648e8853b6a985acbfbca51ee82fb695c79620533aafc8a988e5e07ed`.
- Canonical parsed graph digest: `3337fb9c2e04492044485638c79035d9bb540f2663e7ea3b0abd03c8a618c1f6`.
- Review digest: `80cc4640bfd28102f0b88743e7735a5f594b2a06773c9c909394822e14cbbe84`.
- Registered authority: `refs/ask/accepted-tests/continuation-recovery` → `1cdf5177784a030537c9b4f0dd14e12ae562ec1b`.

Existing `./ask traceability accept-plan` registered this exact contract. The
tracked acceptance pin and authority's `accepted.json` were read back equal.
The review record also pins exact authorization, plan, checkpoint design,
bootstrap design, baseline and R1–R4 review-input file SHA256 values. All were
rechecked unchanged after registration. This seal adds evidence only; it does
not amend the reviewed contract or its design.

## Corrections and static evidence

R1 retains the complete required Git object closure through real parent/tree
edges and requires GC plus self-contained transfer tests. R2 uses a normal
separate repair queue with scoped guards, preserving the blocked legacy queue;
CR-4 prepares a reviewed real adoption proposal for later explicit integration.
R3 assigns finalization to the coordinator after verifier exit, preserving lock
ownership and trusted snapshots, including old runner/interrupted ledger paths.
R4 binds 21 unique case selectors to exact production/assertion/fixture sources.

Completed planning checks: prepared pinned skills without installation; binding
sync; TaskGraph validation (`ok`); canonical contract validation at source SHA;
unique supported unittest selectors, exact source paths and task scopes; matching
canonical digests; independent source/design/mapping review. These are static
planning evidence. Production behavior suites and aggregate `./ask verify` were
not run under the explicit stop-before-behavior-execution direction. No runtime
pass, task completion, workstream acceptance or submitted intent confirmation
has been fabricated. The derived repair intent requires the normal submitted
complete-intent approval before later implementation.

## Interrupted product preserved

Original `agent/shorter-hashes` remains `d04b3a4e515105df8cdf703f2fa0a28895f1524d`.
Original authority remains `e1ca2a523c5417687479c09ffc1bf6c1cc337763`.
Product tracked work artifacts and canonical spec have zero diff from the
selected base. Product raw state SHA256 remains `b5fad609842013a1ca11017ec60e4ae45c042f92828cbf040c795129525b17e6`;
revision 11: Task1 integrated, Task2 blocked, Tasks3–10 pending.
Approved intent SHA256 remains
`8784f3748505fe0ac51ccb9a7dfe78de0c04f79cd26dac58689fdee10cb084e6`.
The old tracked pin and observed authority remain separately preserved; this
seal neither validates historical approval nor moves product authority.

## Binding endpoint

STOP. No implementation, runtime initialization/bootstrap, behavior execution,
checkpoint adoption, product integration or scheduling occurred. The only new
authority is the reviewed repair planning registration. A generic “continue”
must report this endpoint. Later explicit human direction is required to proceed;
normal intent/admission/TDD/review/verification gates still apply. Product
integration/adoption and product scheduling each retain their explicit handoff
and authorization conditions in `bootstrap.md`.

## Revision 10 continuation authority and acceptance

The user later explicitly directed continuation and authorized the scope-aware
CR-1 evidence carry-forward and interrupted-candidate attribution rule. The
original stop-after-seal endpoint is therefore superseded for implementation
inside this workstream; product adoption and scheduling remain outside scope.

Revision 10 was independently reviewed and accepted on 2026-10-22. Candidate:
`588c6cd9f3585eeb77d8a745abfc8d1a96b73cb6`. Reviewer: `/root/review_cr1`.
Review record: `traceability/plan-review-cr2-scope-carry-forward.json`.
The exact review confirms CR-T57 maps checkpoint retention to CR-02 and
interrupted-path attribution, quiescence, and recovery to CR-07; CR-T22 remains
CR-07 only. Accepted digests are spec
`02dcf36a73bbaf4c100e413854e823518f14d3dcbed34fe47a333d8e65790cf1`, test plan
`2ddca16503e68dc640b51b9a4d5ddb8dab79e75b16fd1eec04bc9de012958aa0`, and graph
`0bd73550d1ed2a30b80b554946e55ad8ea839b13fa0da1a84d294242738e42f6`.
Coordinator authority `refs/ask/accepted-tests/continuation-recovery` points to
`14d8bbe20c5f3d24082c13ef98a29e80ac019b92`; the generated tracked pin matches
that authority. Implementation continues at CR-2 under its task-loop gates.
