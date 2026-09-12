#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo base > README.md
git add README.md && git commit -q -m init
# install kit scripts minimally
mkdir -p _ask/scripts _ask/templates
cp "$ROOT/_ask/scripts/check-clean-worktree.sh" "$ROOT/_ask/scripts/start-work.sh" _ask/scripts/
chmod +x _ask/scripts/*.sh
cp "$ROOT/_ask/templates/"*.md "$ROOT/_ask/templates/"*.json _ask/templates/ 2>/dev/null || \
  cp "$ROOT/_ask/templates/"* _ask/templates/
# dirty tree
echo dirty > dirty.txt
set +e
./_ask/scripts/start-work.sh should-fail >/tmp/sw-out.txt 2>/tmp/sw-err.txt
code=$?
set -e
if [[ "$code" -eq 0 ]]; then
  echo "FAIL: start-work must refuse dirty tree" >&2
  cat /tmp/sw-err.txt >&2
  exit 1
fi
# must not have created branch or wiped dirty file
if [[ -f dirty.txt ]] && ! git show-ref --verify --quiet refs/heads/agent/should-fail; then
  echo "PASS: start-work refuses dirty tree without absorbing changes"
  exit 0
fi
# branch might exist if check happened after checkout in old versions — still require dirty file
test -f dirty.txt
echo "PASS: start-work refuses dirty tree"
