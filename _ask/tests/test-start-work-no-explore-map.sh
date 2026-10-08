#!/usr/bin/env bash
# start-work must not seed explore-map.md (00 creates it; real skip leaves none)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo x > README.md
git add README.md && git commit -q -m init
mkdir -p _ask/scripts _ask/templates
cp "$ROOT/_ask/scripts/check-clean-worktree.sh" "$ROOT/_ask/scripts/start-work.sh" _ask/scripts/
chmod +x _ask/scripts/*.sh
cp "$ROOT/_ask/templates/"*.md "$ROOT/_ask/templates/"*.json _ask/templates/ 2>/dev/null || \
  cp "$ROOT/_ask/templates/"* _ask/templates/
git add _ask && git commit -q -m kit
git branch develop
./_ask/scripts/start-work.sh demo
if [[ -e work/demo/explore-map.md ]]; then
  echo "FAIL: start-work must not seed explore-map.md" >&2
  exit 1
fi
test -f work/demo/intent.md
echo "PASS: start-work does not seed explore-map.md"
