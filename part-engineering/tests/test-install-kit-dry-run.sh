#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
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
out="$("$ROOT/part-engineering/scripts/install-kit.sh" --dry-run "$TMP")"
echo "$out" | grep -q 'docs/ excluded\|will not modify target docs'
# ensure dry-run did not copy part-engineering yet
if [[ -d "$TMP/part-engineering" ]]; then
  echo "FAIL: dry-run should not copy" >&2
  exit 1
fi
# docs untouched
grep -q consumer docs/README.md
echo "PASS: install-kit dry-run excludes consumer docs"
