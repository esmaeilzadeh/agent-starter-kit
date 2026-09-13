#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo init > README.md
git add README.md && git commit -q -m init
SKIP_INSTALL=1 "$ROOT/_ask/scripts/install-kit.sh" --skip-prepare "$TMP"
mkdir -p "$TMP/_ask/bindings"
echo 'canary: keep-me' > "$TMP/_ask/bindings/models.yaml"
SKIP_INSTALL=1 "$ROOT/_ask/scripts/install-kit.sh" --skip-prepare "$TMP"
grep -q 'canary: keep-me' "$TMP/_ask/bindings/models.yaml"
echo "PASS: install-kit does not clobber consumer bindings/models.yaml"
