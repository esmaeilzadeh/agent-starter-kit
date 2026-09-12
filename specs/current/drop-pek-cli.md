# Specification: drop obsolete pek-cli workstream

## Status

CURRENT

## Goal

`work/pek-cli/` is gone. Status does not list `pek-cli`.

## Non-goals

Renaming `ask`. Touching `work/rename-pek-to-ask`.

## Behavior

- Delete `work/pek-cli/` (intent-only archive of the pre-rename CLI name).
- Live leftover `agent/pek-cli` already deleted (it was an ancestor of `main`).

## Acceptance criteria

- `work/pek-cli/` does not exist.
- `./ask status --work-id pek-cli` reports no workstream.
- `./ask` still works. `./ask verify` passes.

## Source intent

`work/drop-pek-cli/intent.md`
