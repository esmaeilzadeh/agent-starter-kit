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
SKIP_INSTALL=1 "$ROOT/part-engineering/scripts/install-kit.sh" --skip-prepare "$TMP"
test -d "$TMP/part-engineering"
test -f "$TMP/part-engineering/scripts/check-clean-worktree.sh"
test -d "$TMP/.cursor"
grep -q consumer "$TMP/docs/README.md"
test ! -e "$TMP/scripts/check-clean-worktree.sh"
echo "PASS: install-kit apply leaves docs/ intact and does not create root scripts/"
