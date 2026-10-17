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
