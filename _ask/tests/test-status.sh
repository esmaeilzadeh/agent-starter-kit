#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STATUS="$ROOT/_ask/scripts/status.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo base > README.md
mkdir -p work/done-one
cat > work/done-one/acceptance.md <<'EOF'
# Acceptance

## Accepted commit SHA

abcdef1234567
EOF
git add . && git commit -q -m init
git branch -M main

# live: seeded only (stock explore-map handoff must not count as explored)
git checkout -q -b agent/seeded
mkdir -p work/seeded
printf '# Plan\n\n## Approach\n\n' > work/seeded/plan.md
cat > work/seeded/explore-map.md <<'EOF'
# Explore Map: x

## Handoff to Intent

**Contract:** This section must be non-empty before `01 Grill`. Empty handoff → not eligible for the Engineering Pipeline.

<!-- Required non-empty before entering 01 Grill. Summarize the destination. -->
EOF
git add work/seeded && git commit -q -m seeded
git checkout -q main

# live: intent filled
git checkout -q -b agent/has-intent
mkdir -p work/has-intent
cat > work/has-intent/intent.md <<'EOF'
# Intent: demo

## What

Ship a status command.

## Why
EOF
git add work/has-intent && git commit -q -m intent
git checkout -q main

out="$("$STATUS")"
echo "$out" | grep -q 'default=main'
echo "$out" | grep -qE 'live +seeded +seeded'
echo "$out" | grep -qE 'live +has-intent +intent'
echo "$out" | grep -qE 'archived +done-one +accepted'

filt="$("$STATUS" --work-id has-intent)"
echo "$filt" | grep -q has-intent
echo "$filt" | grep -qv seeded || { echo "FAIL: filter leaked seeded" >&2; exit 1; }

"$STATUS" --json --work-id done-one | python3 -c '
import json,sys
doc=json.load(sys.stdin)
assert doc["workstreams"][0]["life"]=="archived"
assert doc["workstreams"][0]["stage"]=="accepted"
'
echo "PASS: status lists live agent/* and archived work/* without checkout"
