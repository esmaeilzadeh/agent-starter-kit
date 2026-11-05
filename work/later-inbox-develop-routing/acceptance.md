# Acceptance

## Workstream

`later-inbox-develop-routing`

## Specification

A card committed on develop is visible from any work branch through `./ask status`, including when the local develop branch is absent but `origin/develop` exists.

## Evidence

`bash _ask/tests/test-status.sh` passes its feature-branch regression for local and remote develop. `git diff --check` passes. Full `./ask verify` stops before checks because the existing coordinator lacks an accepted-tests reference; this is recorded in `verification.json`.

## Residual risks

Card creation, tracker publication, and unpublished local cards remain separate proposals in `.later/later-inbox-develop-routing.md` and related cards.

## Context-engineering audit

Status help, ADR, workflow policy, root guidance, and `.later/README.md` consistently describe integration-ref listing.

## Acceptance decision

Accepted for the confirmed visibility defect only.

## Accepted commit SHA

Pending.
