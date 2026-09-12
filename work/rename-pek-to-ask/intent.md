# Intent: rename pek → ask and part-engineering → _ask

## What

1. Rename the root kit dispatcher from `pek` to `ask` (Agent Starter Kit).
2. Rename the kit package directory from `part-engineering/` to `_ask/`.
Update dispatcher, install/upgrade overlays, tests, docs, ADRs, and Cursor projections.

## Why

Align CLI and package paths with the Agent Starter Kit product name.

## Non-goals

Changing script behavior under `_ask/scripts/` beyond path renames.

## Human decisions

- CLI: `ask` (Agent Starter Kit)
- Package root: `_ask/`
