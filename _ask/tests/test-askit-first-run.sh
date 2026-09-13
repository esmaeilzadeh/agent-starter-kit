#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo app > README.md
git add README.md && git commit -q -m init

export ASKIT_KIT_ROOT="$ROOT"
export ASKIT_SKIP_SETUP=1
export ASKIT_SKIP_COMPLETION_INSTALL=1
export ASKIT_INSTALL_FLAGS=--skip-prepare

"$ROOT/askit" status
[[ -x "$TMP/ask" ]]
[[ -d "$TMP/_ask" ]]

echo "PASS: first-run askit overlays the kit and runs the command"
