#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# Test the committed kit without copying ignored local environments or run logs.
git -C "$ROOT" archive HEAD _ask .agents/ask | tar -x -C "$TMP"
git -C "$TMP" init -q -b main
git -C "$TMP" config user.name fixture
git -C "$TMP" config user.email fixture@example.test
git -C "$TMP" add _ask .agents
git -C "$TMP" commit -qm fixture
mkdir -p "$TMP/.cursor/commands"
(cd "$TMP" && ASK_ROOT="$TMP" ./_ask/scripts/sync-cursor-binding.sh >/dev/null)
test -f "$TMP/.cursor/commands/off-path.md"
grep -q 'this session only' "$TMP/.cursor/commands/off-path.md"
grep -qE '^description:' "$TMP/.cursor/commands/off-path.md"
echo "PASS: sync copies /off-path as a session-only command"
