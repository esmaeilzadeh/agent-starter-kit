# Plan

## Specification

Session-only `/off-path`. Contract:

- Every new Cursor session starts **on-path**.
- `/off-path` switches **this chat only**. No git flag, no `work/*/kit-path`, no intent flip.
- Source of truth: `_ask/cursor-commands/off-path.md`. `./ask sync` copies it to `.cursor/commands/off-path.md`.
- Policy: `_ask/policies/workflow.md`. Safety gates unchanged.

**Already on this branch (do not redo):** command file, sync copy + `test-sync-off-path-command.sh`, workflow/AGENTS/rule/CONTEXT/ADR-0013 wording.

## Approach

Treat the command as a **session mode**, not a workstream state. Finish discoverability and kit-owned-path docs so install/upgrade/sync keep the file. Then verify and merge when you accept.

## Work breakdown

1. ~~SoT + sync + session-only rules + test~~ — done (`82d1cbd`).

2. ~~**Discoverability**~~ — done (`e522d01`).

3. ~~**Owned paths**~~ — done (`d21cdc2`).

4. ~~**Guide pointer**~~ — done (`8b0993f`).

5. **Verify + merge** — `./ask verify`; merge `agent/ask-status` when you accept.

## Risks

- Humans expect `/off-path` to last across chats. Mitigation: command text + policy say new chat = on-path; do not add `/on-path` (new chat is enough).
- Name clash with Cursor `/fast`. Mitigation: keep the name `/off-path`.
- `./ask sync` on an old tree without `cursor-commands/` — loop already `[[ -f ]]` safe.

## Verification approach

- `_ask/tests/test-sync-off-path-command.sh` (already).
- After front matter: grep description in synced `.cursor/commands/off-path.md`.
- `./ask verify`.
- Manual: new Composer chat is on-path; `/off-path` warns once; another new chat is on-path again.

## Out of scope for this plan

- Durable off-path flag in git.
- `/on-path` command.
- Redefining Cursor `/fast`.
- Autoplays `/01`–`/10` as a batch job.
