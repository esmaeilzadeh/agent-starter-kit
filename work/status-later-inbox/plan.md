# Plan

## Specification

`specs/current/status-later-inbox.md`

## Approach

Extend `status.sh` with a working-tree later scan and two inventory flags. Keep workstream inference on git refs. Completion and kit docs follow the same contract.

## Work breakdown

1. Parse `--later-only` / `--work-only`; exclusive-flag errors; later scan + human/JSON output in `_ask/scripts/status.sh`.
2. Help in `ask` and `status.sh`; flags in `_ask/scripts/ask-complete.sh`.
3. Extend `_ask/tests/test-status.sh` (and completion assertion).
4. Update Build Spec §23.4 / §30.1, ADR 0015, `.later/README.md`, `workflow.md`, root `README.md` status line.

## Risks

Existing tests grep the workstream table; empty later must not change that output. `--work-id` must not leak later rows.

## Verification approach

`_ask/tests/test-status.sh`; `./ask --complete` for `status`; `./ask verify`.

## Out of scope for this plan

`cursor-spawn-slugs` (parked). `./ask later`. Tracker sync. Recursing `.later/` subdirs.
