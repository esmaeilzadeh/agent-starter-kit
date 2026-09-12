# Review

## Scope

Remaining `ask-status` work vs `specs/current/ask-status.md`: `/off-path` discoverability, kit-owned `cursor-commands/`, guide pointer. `./ask status` was already shipped.

## Findings

None blocking.

- Front matter `description` is on `_ask/cursor-commands/off-path.md` and the synced `.cursor/commands/off-path.md`.
- README, demo human/agent roles, spec §34a, guide §5, `OWNED-PATHS.md`, and `upgrade-kit.sh` mention session-only `/off-path` / kit-owned `cursor-commands/`.
- Sync test now requires `description:` in the copied command.
- Non-goals held: no durable flag, no `/on-path`, no autoplay.

## Suggested fixes

None.

## Residual risks

Humans may still expect `/off-path` to survive a new chat. Mitigation is already in the command, policy, and guide. Palette visibility is manual (Cursor UI).

## Review verdict

Pass. No refactor.
