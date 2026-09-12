# Review

## Scope

`specs/current/layout-no-collision.md` vs the tree on `main`.

## Findings

None blocking. `_ask/scripts`, `_ask/tests`, and `_ask/docs` are the kit trees. ADR-0011 matches. install-kit apply/dry-run tests assert consumer `docs/` and root `scripts/` are not overlaid.

## Suggested fixes

None.

## Residual risks

A product that already put kit files in `scripts/` before this layout would still need a one-time move. This repo is already namespaced.

## Review verdict

Pass. No refactor.
