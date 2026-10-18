# Acceptance

## Workstream

git-integration-disconnected-red-evidence

## Specification

A disconnected recognized red source continues to fail completion, with a useful error naming the source and final candidate commits.

## Evidence

The new orphan-commit regression was observed failing with an empty error before the fix and passes afterward. The full traceability evidence module passes all 13 tests. ./ask verify stops before checks because the existing coordinator is missing an accepted-tests ref; this is recorded in verification.json.

## Residual risks

The broader evidence ancestry and retained-attempt policy remains unresolved in the parked later card.

## Context-engineering audit

The original later card now distinguishes the fixed diagnostic from its remaining policy investigation.

## Acceptance decision

Accepted for the non-ancestor diagnostic only.

## Accepted commit SHA

Pending.
