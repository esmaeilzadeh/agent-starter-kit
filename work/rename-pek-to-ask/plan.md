# Plan

## Specification

`specs/current/rename-pek-to-ask.md`

## Approach

The rename already landed on `main` at `acec994`. This workstream records that fact and closes artifacts. No second rename.

## Work breakdown

1. ~~`git mv` `pek` → `ask`, `part-engineering/` → `_ask/`; update dispatcher, overlays, tests, docs, ADRs, Cursor projections~~ — done (`acec994`).
2. Confirm no live `pek` / `part-engineering/` paths remain (only historical work intents).
3. Verify + Accept.

## Risks

Historical `work/pek-cli` intent still says `pek`. That is archive text, not a current CLI.

## Verification approach

- `test -f ask` and `test -d _ask` and `! test -e pek` and `! test -d part-engineering`
- `rg` over kit (excluding `work/`) finds no current `pek` / `part-engineering` paths
- `./ask verify`

## Out of scope for this plan

Rewriting archived `work/pek-cli` intent. Merging other live branches.
