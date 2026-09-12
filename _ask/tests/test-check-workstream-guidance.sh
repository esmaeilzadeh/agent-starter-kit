#!/usr/bin/env bash
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
mkdir -p _ask/scripts work/demo
cp "$ROOT/_ask/scripts/check-clean-worktree.sh" "$ROOT/_ask/scripts/check-workstream.sh" _ask/scripts/
chmod +x _ask/scripts/*.sh
git checkout -q -b agent/demo
# no spec
set +e
./_ask/scripts/check-workstream.sh demo >/tmp/cw-out.txt 2>/tmp/cw-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'guidance, not a lock' /tmp/cw-err.txt
grep -q 'default path incomplete' /tmp/cw-err.txt
echo "PASS: check-workstream missing spec is guidance wording, not a padlock"
