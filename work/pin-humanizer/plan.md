# Plan

## Specification

`specs/current/pin-humanizer.md`

## Approach

Pin the skill, add a thin stock rule and Spec-stage pointers, lock the install, add a contract test and ADR. Do not rewrite existing kit prose.

## Work breakdown

1. Manifest pin + `./ask prepare` + commit `skills-lock.json`.
2. Stock Cursor rule, `02`/`03`/`04` contracts, ADR 0017, spec/MAPPING row, contract test.
3. Park `.later/humanize-ask-docs-and-specs.md`.
4. Review, verify, accept.

## Risks

Tag `v3.0.0` could be retagged. Mitigation: lock hash.

Consumer upgrade gets the rule without the pin. Residual, documented.

## Verification approach

`./ask prepare` ok for humanizer. Grep pin/rule/contracts. `./ask verify`.

## Out of scope for this plan

Rewriting kit Guide/Build Spec prose (later inbox).
