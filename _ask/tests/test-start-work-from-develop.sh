#!/usr/bin/env bash
# start-work branches from develop or fails closed.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

setup_kit() {
  mkdir -p _ask/scripts _ask/templates
  cp "$ROOT/_ask/scripts/check-clean-worktree.sh" "$ROOT/_ask/scripts/access-check.sh" "$ROOT/_ask/scripts/start-work.sh" _ask/scripts/
  chmod +x _ask/scripts/*.sh
  cp "$ROOT/_ask/templates/"*.md "$ROOT/_ask/templates/"*.json _ask/templates/ 2>/dev/null || \
    cp "$ROOT/_ask/templates/"* _ask/templates/
}

# --- no develop ---
git init -q "$TMP/none"
cd "$TMP/none"
git config user.email t@e.com
git config user.name t
echo x > README.md
git add README.md && git commit -q -m init
setup_kit
git add _ask && git commit -q -m kit
set +e
out="$(./_ask/scripts/start-work.sh demo 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "missing develop should fail: $out"
printf '%s\n' "$out" | grep -qi develop || fail "message names develop: $out"
git rev-parse --abbrev-ref HEAD | grep -qv '^agent/demo$' || fail "must not create agent branch"

# --- develop present (created after kit so templates are on develop) ---
git init -q "$TMP/yes"
cd "$TMP/yes"
git config user.email t@e.com
git config user.name t
echo x > README.md
git add README.md && git commit -q -m init
setup_kit
git add _ask && git commit -q -m kit
git branch develop
git checkout -q develop
echo d > on-develop
git add on-develop && git commit -q -m develop-tip
git checkout -q master 2>/dev/null || git checkout -q main
./_ask/scripts/start-work.sh demo
[[ "$(git rev-parse --abbrev-ref HEAD)" == agent/demo ]] || fail "checked out agent/demo"
git merge-base --is-ancestor develop HEAD || fail "agent/demo not based on develop"
test -f on-develop || fail "missing develop tip file"
python3 - <<'PY'
import json
from pathlib import Path
path = Path('work/demo/engineering-model.json')
model = json.loads(path.read_text())
assert model['schema'] == 'ask-engineering-model/v2'
assert model['work_id'] == 'demo'
assert model['revision'] == 1
assert model['nodes'][0]['type'] == 'intent'
model['revision'] = 7
path.write_text(json.dumps(model))
PY
git add work && git commit -qm 'existing model must survive start-work retry'
./_ask/scripts/start-work.sh demo
python3 -c 'import json; assert json.load(open("work/demo/engineering-model.json"))["revision"] == 7'

echo "PASS: start-work from develop or fail closed"
