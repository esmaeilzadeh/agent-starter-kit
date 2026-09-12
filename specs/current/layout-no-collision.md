# Specification: namespace kit off generic product folders

## Status

CURRENT

## Goal

Kit scripts, kit tests, and kit-author docs live under `_ask/` so a product can keep its own `docs/`, `scripts/`, and `tests/`.

## Non-goals

Factory/wrap layouts. Renaming `specs/` or `work/`.

## Behavior

- Kit package is `_ask/` only (ADR-0011).
- `install-kit` / `upgrade-kit` never overlay consumer `docs/`, `scripts/`, or `tests/`.
- Root adapter stays `ask`, `AGENTS.md`, `.cursor/`.

## Acceptance criteria

- `_ask/scripts/`, `_ask/tests/`, `_ask/docs/` exist.
- Root `scripts/` is not the kit script tree.
- `test-install-kit-apply.sh` and `test-install-kit-dry-run.sh` pass.
- `./ask verify` passes.

## Source intent

`work/layout-no-collision/intent.md`
