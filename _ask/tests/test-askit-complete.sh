#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ASKIT="$ROOT/askit"
chmod +x "$ASKIT"

# From the kit repo, askit finds ./ask and wraps it.
out="$("$ASKIT" --help)"
printf '%s\n' "$out" | grep -q 'Agent Starter Kit'
out="$("$ASKIT" --complete 1 askit sta)"
printf '%s\n' "$out" | grep -q start-work
out="$("$ASKIT" completion bash)"
printf '%s\n' "$out" | grep -q askit

# No ./ask: still complete from the bundled lib (run from a temp dir, PATH to askit).
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo x > README.md
git add README.md && git commit -q -m init
out="$("$ASKIT" --help)"
printf '%s\n' "$out" | grep -q 'no ./ask yet'
out="$("$ASKIT" --complete 1 askit)"
printf '%s\n' "$out" | grep -q setup

echo "PASS: askit wraps ./ask and completes without a local kit"
