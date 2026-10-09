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

python3 _ask/scripts/intent-confirmation.py confirm --root "$TMP" --work-id demo \
  --response 'approve'
python3 -c 'import json; assert json.load(open("work/demo/intent-confirmation.json"))["human_response"] == "approve"'
git add . && git commit -qm 'record exact terse approval'
./_ask/scripts/check-workstream.sh demo >/dev/null

cp work/demo/intent-confirmation.json prior-confirmation.json
if python3 _ask/scripts/intent-confirmation.py confirm --root "$TMP" --work-id demo \
  --choice revise; then
  echo 'FAIL: revision choice granted approval' >&2
  exit 1
fi
cmp prior-confirmation.json work/demo/intent-confirmation.json
if python3 _ask/scripts/intent-confirmation.py confirm --root "$TMP" --work-id demo \
  --choice approve --response 'No'; then
  echo 'FAIL: conflicting choice and text answers were accepted' >&2
  exit 1
fi

python3 _ask/scripts/intent-confirmation.py confirm --root "$TMP" --work-id demo \
  --choice approve
python3 -c 'import json; c=json.load(open("work/demo/intent-confirmation.json")); assert c["schema"] == "ask-intent-confirmation/v2" and c["human_choice"] == "approve"'
git add . && git commit -qm 'record submitted approval choice'
./_ask/scripts/check-workstream.sh demo >/dev/null

python3 - <<'PY'
import json
from pathlib import Path
path = Path('work/demo/intent-confirmation.json')
record = json.loads(path.read_text())
record['human_choice'] = 'revise'
path.write_text(json.dumps(record))
PY
git add . && git commit -qm 'test a non-affirmative recorded choice'
if ./_ask/scripts/check-workstream.sh demo >/dev/null 2>&1; then
  echo 'FAIL: gate accepted a non-affirmative recorded choice' >&2
  exit 1
fi
python3 _ask/scripts/intent-confirmation.py confirm --root "$TMP" --work-id demo \
  --choice approve
git add . && git commit -qm 'restore submitted approval choice'

printf '\nA new unconfirmed assumption.\n' >> work/demo/intent.md
git add . && git commit -qm 'change intent after confirmation'
if ./_ask/scripts/check-workstream.sh demo >/dev/null 2>&1; then
  echo 'FAIL: implementation gate accepted a stale confirmation' >&2
  exit 1
fi
echo 'PASS: workstream gate requires an explicit, current intent confirmation'
