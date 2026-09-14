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

# live: intent + code outside work/ → warning, not a lock
git checkout -q -b agent/jumped
mkdir -p work/jumped
cat > work/jumped/intent.md <<'EOF'
# Intent: jump

## What

Skip the plan.

## Why
EOF
echo impl > app.c
git add work/jumped app.c && git commit -q -m jump
git checkout -q main
# leftover agent/* after merge must not stay “live”
git checkout -q -b agent/merged-leftover
mkdir -p work/merged-leftover
cat > work/merged-leftover/intent.md <<'EOF'
# Intent: leftover

## What

Already merged.

## Why
EOF
git add work/merged-leftover && git commit -q -m leftover
git checkout -q main
git merge -q --ff-only agent/merged-leftover

out="$("$STATUS")"
echo "$out" | grep -q 'default=main'
echo "$out" | grep -qE 'live +seeded +seeded'
echo "$out" | grep -qE 'live +has-intent +intent'
echo "$out" | grep -qE 'archived +done-one +accepted'
echo "$out" | grep -qE 'archived +merged-leftover'
echo "$out" | grep -qvE 'live +merged-leftover' || { echo "FAIL: merged leftover still live" >&2; exit 1; }
echo "$out" | grep -qE 'live +jumped +intent'
echo "$out" | grep jumped | grep -q 'code-without-plan'

filt="$("$STATUS" --work-id has-intent)"
echo "$filt" | grep -q has-intent
echo "$filt" | grep -qv seeded || { echo "FAIL: filter leaked seeded" >&2; exit 1; }

"$STATUS" --json --work-id done-one | python3 -c '
import json,sys
doc=json.load(sys.stdin)
assert doc["workstreams"][0]["life"]=="archived"
assert doc["workstreams"][0]["stage"]=="accepted"
assert doc["later"]==[]
'

mkdir -p .later
printf '# Kit README\n' > .later/README.md
printf '# Title here\n\nbody\n' > .later/foo.md
printf '## Why\n\n# Real\n' > .later/bar.md
printf '#NoSpace\n' > .later/nospace.md
printf 'intro\n\n# Late h1\n' > .later/late.md

out="$("$STATUS")"
echo "$out" | grep -qE 'live +has-intent'
echo "$out" | grep -q '^later:'
echo "$out" | grep -qE '^foo +Title here'
echo "$out" | grep -qE '^bar +Real'
echo "$out" | grep -qE '^nospace '
echo "$out" | grep -qE '^late +Late h1'
echo "$out" | grep -qv 'Kit README' || { echo "FAIL: README.md listed as later card" >&2; exit 1; }

wo="$("$STATUS" --work-only)"
echo "$wo" | grep -qv '^later:' || { echo "FAIL: --work-only leaked later" >&2; exit 1; }

lo="$("$STATUS" --later-only)"
echo "$lo" | grep -q '^later:'
echo "$lo" | grep -qv 'LIFE' || { echo "FAIL: --later-only printed LIFE" >&2; exit 1; }
echo "$lo" | grep -qv 'default=' || { echo "FAIL: --later-only printed default=" >&2; exit 1; }

filt="$("$STATUS" --work-id has-intent)"
echo "$filt" | grep -q has-intent
echo "$filt" | grep -qv '^later:' || { echo "FAIL: --work-id leaked later" >&2; exit 1; }

"$STATUS" --json --work-id has-intent | python3 -c '
import json,sys
doc=json.load(sys.stdin)
assert doc["later"]==[]
assert any(r["work_id"]=="has-intent" for r in doc["workstreams"])
'
"$STATUS" --json --later-only | python3 -c '
import json,sys
doc=json.load(sys.stdin)
assert doc["workstreams"]==[]
slugs={c["slug"] for c in doc["later"]}
assert slugs=={"foo","bar","nospace","late"}
foo=next(c for c in doc["later"] if c["slug"]=="foo")
assert foo["title"]=="Title here"
assert foo["path"]==".later/foo.md"
bar=next(c for c in doc["later"] if c["slug"]=="bar")
assert bar["title"]=="Real"
ns=next(c for c in doc["later"] if c["slug"]=="nospace")
assert ns["title"]==""
late=next(c for c in doc["later"] if c["slug"]=="late")
assert late["title"]=="Late h1"
'
"$STATUS" --json --work-only | python3 -c '
import json,sys
doc=json.load(sys.stdin)
assert doc["later"]==[]
assert doc["workstreams"]
'

set +e
"$STATUS" --later-only --work-only >/tmp/status-ex-out 2>/tmp/status-ex-err
ex=$?
set -e
[[ "$ex" -eq 2 ]]
grep -q -- '--later-only' /tmp/status-ex-err
grep -q -- '--work-only' /tmp/status-ex-err

set +e
"$STATUS" --later-only --work-id anything >/tmp/status-id-out 2>/tmp/status-id-err
ex=$?
set -e
[[ "$ex" -eq 2 ]]
grep -q -- '--work-id' /tmp/status-id-err

# overlapping slug still listed
printf '# Seeded park\n' > .later/seeded.md
overlap="$("$STATUS" --later-only)"
echo "$overlap" | grep -qE '^seeded +Seeded park'

# README-only → no later block
rm -f .later/foo.md .later/bar.md .later/nospace.md .later/late.md .later/seeded.md
empty_later="$("$STATUS")"
echo "$empty_later" | grep -qv '^later:' || { echo "FAIL: README-only printed later" >&2; exit 1; }
lo_empty="$("$STATUS" --later-only)"
echo "$lo_empty" | grep -qx 'status: no later cards in .later/'

# zero workstreams + later card
EMPTY="$(mktemp -d)"
git init -q "$EMPTY"
(
  cd "$EMPTY"
  git config user.email t@e.com
  git config user.name t
  echo x > README.md
  git add README.md && git commit -q -m init
  git branch -M main
  mkdir -p .later
  printf '# Park this\n' > .later/park.md
  none="$("$STATUS")"
  echo "$none" | grep -q 'no live agent/\*'
  echo "$none" | grep -q '^later:'
  echo "$none" | grep -qE '^park +Park this'
)
rm -rf "$EMPTY"

comp="$("$ROOT/ask" --complete 2 ./ask status)"
echo "$comp" | grep -q -- '--later-only'
echo "$comp" | grep -q -- '--work-only'

echo "PASS: status lists live agent/* and archived work/* without checkout; later inbox on checkout"
