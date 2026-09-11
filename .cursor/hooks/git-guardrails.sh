#!/usr/bin/env bash
# Thin Cursor hook wrapper → kit Git guardrail scripts.
# Reads Cursor hook stdin JSON; only enforces on risky git mutations when configured.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
# Always allow; enforce via explicit script calls in agent checklist.
# When CURSOR_ENFORCE_CLEAN=1, refuse shell if tree dirty (optional hard mode).
if [[ "${CURSOR_ENFORCE_CLEAN:-0}" == "1" ]]; then
  if ! "$ROOT/scripts/check-clean-worktree.sh" >/dev/null 2>&1; then
    echo '{"permission":"deny","userMessage":"Working tree dirty; run scripts/check-clean-worktree.sh"}'
    exit 0
  fi
fi
echo '{"permission":"allow"}'
