#!/usr/bin/env bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
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
cp -r "$ROOT/_ask/scripts/engineering_model" _ask/scripts/
cp -r "$ROOT/_ask/scripts/inner_loop" _ask/scripts/
mkdir -p .agents
cp -r "$ROOT/.agents/ask" .agents/
python3 "$ROOT/_ask/tests/traceability_support.py" seed-model "$TMP" demo
chmod +x _ask/scripts/*.sh
printf 'work/demo/traceability/\n__pycache__/\n' > .gitignore
git add . && git commit -q -m kit
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
