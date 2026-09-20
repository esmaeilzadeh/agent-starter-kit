#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$ROOT/_ask" "$TMP/_ask"
mkdir -p "$TMP/.agents"
cp -a "$ROOT/.agents/ask" "$TMP/.agents/ask"
mkdir -p "$TMP/.cursor/commands"
(cd "$TMP" && ./_ask/scripts/sync-cursor-binding.sh >/dev/null)
test -f "$TMP/.cursor/commands/off-path.md"
grep -q 'this session only' "$TMP/.cursor/commands/off-path.md"
grep -qE '^description:' "$TMP/.cursor/commands/off-path.md"
echo "PASS: sync copies /off-path as a session-only command"
