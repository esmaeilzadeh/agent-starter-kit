#!/usr/bin/env bash
# Prefer .agents/ask/stages over _ask/agents when both exist.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/_ask/scripts" "$TMP/_ask/agents" "$TMP/_ask/cursor-commands"
mkdir -p "$TMP/.agents/ask/stages"
cp "$ROOT/_ask/scripts/sync-cursor-binding.sh" "$TMP/_ask/scripts/"
cp "$ROOT/_ask/scripts/sync-runtime-agents.py" "$TMP/_ask/scripts/"
cp -a "$ROOT/_ask/bindings" "$TMP/_ask/bindings"
if [[ -d "$ROOT/.agents/ask/bindings" ]]; then
  mkdir -p "$TMP/.agents/ask/bindings"
  cp -a "$ROOT/.agents/ask/bindings/." "$TMP/.agents/ask/bindings/"
fi

printf '%s\n' 'old-canary-do-not-emit' > "$TMP/_ask/agents/06-implement.md"
printf '%s\n' 'new-canary-from-agents-ask' > "$TMP/.agents/ask/stages/06-implement.md"

(cd "$TMP" && bash _ask/scripts/sync-cursor-binding.sh >/dev/null)

skill="$TMP/.cursor/skills/kit-06-implement/SKILL.md"
grep -q 'new-canary-from-agents-ask' "$skill"
if grep -q 'old-canary-do-not-emit' "$skill"; then
  echo "FAIL: sync used _ask/agents while .agents/ask/stages existed" >&2
  exit 1
fi
grep -q '.agents/ask/stages/06-implement.md' "$skill"

echo "PASS: sync prefers .agents/ask/stages over _ask/agents"
