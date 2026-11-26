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
mkdir -p _ask/scripts work/demo/inner-loop
cp "$ROOT/_ask/scripts/check-clean-worktree.sh" "$ROOT/_ask/scripts/check-workstream.sh" _ask/scripts/
cp "$ROOT/_ask/scripts/client_ignores.py" _ask/scripts/
cp -r "$ROOT/_ask/scripts/engineering_model" _ask/scripts/
cp -r "$ROOT/_ask/scripts/inner_loop" _ask/scripts/
mkdir -p .agents
cp -r "$ROOT/.agents/ask" .agents/
printf 'schema: ask-inner-loop-tasks/v1\nwork_id: demo\ntasks:\n  - id: a\n    depends_on: []\n    owned_paths: [README.md]\n' > work/demo/inner-loop/tasks.yaml
python3 "$ROOT/_ask/tests/traceability_support.py" seed-model "$TMP" demo
chmod +x _ask/scripts/*.sh
printf 'work/demo/traceability/\nwork/demo/inner-loop/state.*\n__pycache__/\n' > .gitignore
git add . && git commit -q -m kit
git checkout -q -b agent/demo
# no spec
python3 _ask/scripts/inner_loop/__main__.py --root "$TMP" cas-init demo >/dev/null
set +e
output="$(./_ask/scripts/check-workstream.sh demo 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'guidance, not a lock' <<<"$output" || { printf '%s\n' "$output" >&2; exit 1; }
grep -q 'default path incomplete' <<<"$output"
echo "PASS: check-workstream missing spec is guidance wording, not a padlock"
