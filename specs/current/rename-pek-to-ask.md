# Specification: rename pek → ask and part-engineering → _ask

## Status

CURRENT

## Goal

The public kit CLI is `./ask`. The kit package directory is `_ask/`. No live `pek` dispatcher or `part-engineering/` tree remains.

## Non-goals

Changing script behavior under `_ask/scripts/` beyond path renames. Rewriting historical `work/pek-cli` / `work/rename-pek-to-ask` intent text.

## Behavior

- Root dispatcher file is `ask` (Agent Starter Kit).
- Protocol, scripts, tests, and kit-author docs live under `_ask/`.
- `install-kit` / `upgrade-kit` copy and refresh `ask` and `_ask/`.
- ADRs and living docs say `ask` / `_ask/`, not `pek` / `part-engineering/`.

## Acceptance criteria

- Root `ask` exists and help text names Agent Starter Kit.
- Directory `_ask/` exists; `part-engineering/` does not.
- Kit tests and docs do not invoke `./pek` or `part-engineering/` as current paths.
- `./ask verify` passes.

## Source intent

`work/rename-pek-to-ask/intent.md`
