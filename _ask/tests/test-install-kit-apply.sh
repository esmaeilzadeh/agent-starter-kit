#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
mkdir -p docs
echo consumer > docs/README.md
echo init > README.md
git add . && git commit -q -m init
SKIP_INSTALL=1 "$ROOT/_ask/scripts/install-kit.sh" --skip-prepare "$TMP"
test -d "$TMP/_ask"
test -f "$TMP/_ask/scripts/check-clean-worktree.sh"
test -d "$TMP/.cursor"
test -x "$TMP/ask"
grep -q consumer "$TMP/docs/README.md"
test ! -e "$TMP/scripts/check-clean-worktree.sh"
test ! -d "$TMP/_ask/tests"
test ! -e "$TMP/askit"
test ! -e "$TMP/install-askit.sh"
echo "PASS: install-kit apply leaves docs/ intact and does not overlay root scripts/ or kit tests/"
