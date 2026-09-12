# Specification: workstream status and kit-path guidance

## Status

CURRENT

## Goal

Agents can see live vs archived workstreams without checking out branches, and can leave the kit path for **this chat only** without persisting a flag.

## Non-goals

`work/INDEX.md`. External trackers. Checking out branches to build a board. Locking Implement. Autoplays `/01`–`/10`. Auto-deleting `agent/*`. Durable off-path flag. `/on-path` command.

## Behavior

### Status

`./ask status` reads local `agent/*` that are not fully merged into the default branch (live) and `work/*` on the default branch with no matching live `agent/*` (archive). No checkout, no `INDEX`.

### Session-only `/off-path`

- Every new Cursor session starts **on-path**.
- `/off-path` switches **this chat only**. Warn once, then follow.
- Do not write `work/*/kit-path`, flip intent, or add a repo flag.
- Source: `_ask/cursor-commands/off-path.md`. `./ask sync` copies it to `.cursor/commands/off-path.md`.
- Cursor’s command palette can find `/off-path` via command `description` front matter.
- Install/upgrade treat `_ask/cursor-commands/` as kit-owned.

### On-path skip meaning

Artifacts stay required on `01`–`10`. Skip means skip extra *approvals* (one defaults-OK, then Accept). Missing artifacts while still on-path: prepare from defaults, confirm once, continue.

## Interfaces

- `./ask status`
- `_ask/cursor-commands/off-path.md` → `.cursor/commands/off-path.md`
- `_ask/policies/workflow.md`
- `_ask/OWNED-PATHS.md` and `./ask upgrade` copy set

## Acceptance criteria

- `./ask status` lists live `agent/*` and archived `work/*` from refs.
- `/off-path` source has a `description` front matter; sync copies it.
- Root `README.md` mentions `/off-path`.
- Demo human/agent roles mention session-only `/off-path`.
- `_ask/spec/05-examples-and-binding.md` mentions `_ask/cursor-commands/` next to other `.cursor/commands`.
- `_ask/cursor-commands/` is kit-owned; upgrade copies it when present.
- `_ask/guide/02-workflow.md` says `/off-path` is this session only.
- `./ask verify` passes.

## Open questions

None.

## Source intent

`work/ask-status/intent.md`
