# Spec Change record: client-security-hardening

## Current status

Human approved `spec-change-model-flow.md` and the complete revised intent
with the exact response "approved". The canonical criterion registry is now
revision 2; CSH-001 through CSH-008 are unchanged and CSH-009 through CSH-012
cover the extension. Intent confirmation binds the exact presented draft bytes;
its historical pending wording is superseded by this recorded approval.
Rechallenge the combined contract, then finish Plan and stop before implementation.
The prior no-change disposition below applies to revision 1 and remains history.

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
