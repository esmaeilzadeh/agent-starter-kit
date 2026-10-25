# Cursor hooks

Thin wrappers only. Guardrail logic lives in `_ask/scripts/` so it remains enforceable without Cursor.

- `git-guardrails.sh` — optional clean-tree gate (`CURSOR_ENFORCE_CLEAN=1`); agents should still call `./ask check-clean` / `./ask check-workstream` explicitly.
- `access-preflight.sh` — session-start write-access check; on failure it injects a stop instruction with the blocked path. Cloud sessions use the portable project instructions because Cursor does not run `sessionStart` there.
