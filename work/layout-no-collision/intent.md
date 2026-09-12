# Intent: Namespace kit off generic product folders

## What

Move kit scripts, kit tests, and kit-author docs under `_ask/` so a Nest (or any) product can keep its own `docs/`, `scripts/`, and `tests/` without overlay collisions.

## Why

Root `scripts/` and this repo’s `docs/` contradicted the story “everything outside _ask is the running project.”

## Non-goals

Factory/wrap layouts. Renaming `specs/` or `work/`.

## Known assumptions

Cursor still requires root `AGENTS.md` and `.cursor/`.

## Open questions

None — Q1=A, Q2=A locked.

## Human decisions

Three layers: kit package / thin adapter / product state.

Explore skipped: destination already clear.
