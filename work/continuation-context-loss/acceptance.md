# Acceptance

## Workstream

`continuation-context-loss`

## Specification

Continuation requests recover the uniquely active authorized workstream from repository evidence before new-task intake. Existing approvals remain in force; only ambiguous workstream identity triggers a narrow question.

## Evidence

Canonical and generated Explore instructions contain the recovery rule. `./ask sync` succeeds on two consecutive runs, `git diff --check` passes, and manual projection inspection passes. Full `./ask verify` stops before checks due to the pre-existing `migration_required: missing coordinator accepted-tests ref` condition.

## Residual risks

The repository verifier cannot provide full suite evidence until that accepted-tests migration is completed.

## Context-engineering audit

Only the canonical Explore contract and its generated projections changed; the rule appears once in each.

## Acceptance decision

Accepted for the bounded instruction fix with the verification limitation recorded.

## Accepted commit SHA

Pending workstream commit.
