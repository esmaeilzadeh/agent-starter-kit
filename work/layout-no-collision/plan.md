# Plan

## Specification

`specs/current/layout-no-collision.md`

## Approach

The layout already landed on `main` (moves + ADR-0011 + install-kit tests). Close artifacts. No second move.

## Work breakdown

1. ~~ADR + `git mv` scripts/tests/docs under `_ask/`; install-kit never overlays consumer trees~~ — done on `main`.
2. Verify + Accept.

## Risks

Old docs may still say `docs/demo/` or `scripts/` for kit paths. The demo vehicle `scripts/kit-status.sh` is product-owned and correct.

## Verification approach

- `_ask/scripts`, `_ask/tests`, `_ask/docs` exist
- install-kit tests pass via `./ask verify`

## Out of scope for this plan

Renaming `specs/` or `work/`. Factory layouts.
