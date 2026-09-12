# Cursor hooks

Thin wrappers only. Guardrail logic lives in `_ask/scripts/` so it remains enforceable without Cursor.

- `git-guardrails.sh` — optional clean-tree gate (`CURSOR_ENFORCE_CLEAN=1`); agents should still call `./ask check-clean` / `./ask check-workstream` explicitly.
