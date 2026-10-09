#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git init -q "$TMP"
cd "$TMP"
git config user.email test@example.invalid
git config user.name test
printf 'seed\n' > README.md
mkdir -p _ask/scripts specs/current work/demo
cp "$ROOT/_ask/scripts/check-clean-worktree.sh" _ask/scripts/
cp "$ROOT/_ask/scripts/check-workstream.sh" _ask/scripts/
cp "$ROOT/_ask/scripts/intent-confirmation.py" _ask/scripts/
cp "$ROOT/ask" ./ask
chmod +x ask _ask/scripts/*.sh
printf '# Spec\n' > specs/current/demo.md
printf '# Intent\n\n## What\nA demo.\n\n## Known assumptions\n- Local use.\n' > work/demo/intent.md
printf '# Plan\n' > work/demo/plan.md
git add . && git commit -qm seed
git checkout -qb agent/demo

if ./_ask/scripts/check-workstream.sh demo >/dev/null 2>&1; then
  echo 'FAIL: implementation gate accepted an intent with no human confirmation' >&2
  exit 1
fi
if python3 _ask/scripts/intent-confirmation.py confirm --root "$TMP" --work-id demo \
  --response 'No, do not proceed'; then
  echo 'FAIL: confirmation command accepted a negative response' >&2
  exit 1
fi

python3 _ask/scripts/intent-confirmation.py confirm --root "$TMP" --work-id demo \
  --response 'I approve these defaults are OK'
git add . && git commit -qm 'record explicit intent confirmation'
./_ask/scripts/check-workstream.sh demo >/dev/null

printf '\nA new unconfirmed assumption.\n' >> work/demo/intent.md
git add . && git commit -qm 'change intent after confirmation'
if ./_ask/scripts/check-workstream.sh demo >/dev/null 2>&1; then
  echo 'FAIL: implementation gate accepted a stale confirmation' >&2
  exit 1
fi
echo 'PASS: workstream gate requires an explicit, current intent confirmation'
