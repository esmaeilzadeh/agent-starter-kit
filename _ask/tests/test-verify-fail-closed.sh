#!/usr/bin/env bash
# Fail-closed verify: empty/missing plan fails; core has no language CLIs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if grep -qE 'npm test|pytest|cargo test' _ask/scripts/verify.sh .agents/ask/verification/*.py 2>/dev/null; then
  echo "FAIL: language CLIs still in verify core" >&2
  exit 1
fi

[[ -f .agents/verification.yaml ]]
grep -q 'ask-kit' .agents/verification.yaml
grep -q 'no_production_datastore' .agents/verification.yaml

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
git -C "$TMP" config user.email t@e.com
git -C "$TMP" config user.name t
echo x > "$TMP/README"
git -C "$TMP" add README
git -C "$TMP" commit -q -m init

# missing yaml → fail
set +e
out="$(ASK_ROOT="$TMP" VERIFY_OUT_DIR="$TMP" "$ROOT/_ask/scripts/verify.sh" 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || { echo "FAIL: missing yaml passed: $out" >&2; exit 1; }
printf '%s\n' "$out" | grep -qiE 'wizard|verification.yaml' || {
  echo "FAIL: missing yaml should name wizard/yaml: $out" >&2
  exit 1
}

# empty checks → fail
mkdir -p "$TMP/.agents"
printf '%s\n' 'schema: ask-checkplan/v1' 'checks: []' > "$TMP/.agents/verification.yaml"
set +e
out="$(ASK_ROOT="$TMP" VERIFY_OUT_DIR="$TMP" "$ROOT/_ask/scripts/verify.sh" 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || { echo "FAIL: empty checks passed: $out" >&2; exit 1; }

echo "PASS: verify fail-closed; ask-kit named; no language CLIs in core"
