# Spec Change record: client-security-hardening

## Current status

Planning paused after the human requested an additional feature. The new
proposal is `spec-change-model-flow.md`; its complete revised intent is
`intent-model-flow.proposed.md`. They require one combined scope/intent decision
before amending the accepted security contract. The prior no-change disposition
below applies only to revision 1 and is retained as history.

## Prior disposition: security specification revision 1

## Current specification

`specs/current/client-security-hardening.md` and its canonical criterion registry,
`specs/current/client-security-hardening.json`, revision 1. Independent Astra
challenge: `spec-challenge.md`, PASS.

## Proposed change

None. Keep the accepted specification and approved intent byte-identical.

## Why this disposition applies

The challenge found implementation details that the specification explicitly
leaves to Plan: executable identity, write ownership, durable recovery, private
credential location and migration, dependency pins, verification environment,
runtime serialization and listener precedence. Plan must specify these and
carry the challenge's counterexamples into its test contract. No criterion is
removed, weakened or converted to review-only verification.

## Impacted artifacts and workstreams

Prepare `plan.md`, `inner-loop/tasks.yaml`, `test-plan.json` and guarded Engineering
Model additions, then obtain an independent review of the exact contracts.
Serialize shared installer work on this branch. Preserve the existing client
file obligation; any demonstrated violation needs a separate focused repair
before overlapping implementation proceeds.

## Migration / transition notes

Include existing client trust enrollment, credential migration and rotation,
project overlay preservation, dependency source approval and retained-log
handling in the implementation plan. Preserve the Git index and history.

## Decision

No specification change is proposed, so no new human scope choice is required.
Proceed to Stage 05 under the existing approval. Human endpoint: "stop when
implementation plan is ready". This record authorizes no implementation.
