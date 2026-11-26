# Acceptance

## Workstream

Focused bug fix: the dogfood worktree no longer depends on `/tmp` and its exact pin and recreation command are tracked.

## Specification

`work/dogfood-directory-persistence/intent.md` and `bugfix.md`.

## Evidence

`work/dogfood-directory-persistence/frozen-copy.md` and `verification.json`.

## Residual risks

The worktree itself is local Git-managed state and is not committed as repository content.

## Context-engineering audit

Not applicable to this focused operational bug fix.

## Acceptance decision

The focused bug fix is implemented and its pin/path/recreation checks pass. Repository-level completion remains blocked because the frozen verifier requires an accepted-tests authority ref that this bugfix workstream does not have.

## Accepted commit SHA

`9725d67e0cf515cecbc884ec8991fed7c0e4b30e`
