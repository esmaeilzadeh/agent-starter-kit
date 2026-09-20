#!/usr/bin/env bash
# Scaffold writes yaml only when absent; mixed-stack stops; --preset for tests.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PY=(python3 "$ROOT/_ask/scripts/verify_scaffold.py")
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $*" >&2; exit 1; }

"${PY[@]}" --help | grep -qi 'human-only'

# non-TTY without --preset refuses
set +e
"${PY[@]}" --root "$TMP" </dev/null >/tmp/ask-scaffold-notty.out 2>/tmp/ask-scaffold-notty.err
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "non-TTY scaffold should fail"
grep -q 'human-only' /tmp/ask-scaffold-notty.err || fail "human-only on stderr"
[[ ! -f "$TMP/.agents/verification.yaml" ]] || fail "non-TTY wrote yaml"

# --preset ask-kit writes yaml when absent
mkdir -p "$TMP"
"${PY[@]}" --root "$TMP" --preset ask-kit
[[ -f "$TMP/.agents/verification.yaml" ]] || fail "preset should write yaml"
grep -q 'ask-kit' "$TMP/.agents/verification.yaml" || fail "preset contents"

# second run does not overwrite
echo 'schema: keep-me' > "$TMP/.agents/verification.yaml"
"${PY[@]}" --root "$TMP" --preset ask-kit
grep -q 'keep-me' "$TMP/.agents/verification.yaml" || fail "should not overwrite existing yaml"
[[ ! -f "$TMP/.agents/verification.yaml.candidate" ]] || fail "no candidate without --re-scaffold"

# re-scaffold writes candidate only
"${PY[@]}" --root "$TMP" --preset ask-kit --re-scaffold
[[ -f "$TMP/.agents/verification.yaml.candidate" ]] || fail "missing candidate"
grep -q 'keep-me' "$TMP/.agents/verification.yaml" || fail "re-scaffold mutated yaml"
grep -q 'ask-kit' "$TMP/.agents/verification.yaml.candidate" || fail "candidate should be ask-kit"

# mixed eslint+biome stops, writes nothing
FIX="$ROOT/_ask/tests/fixtures/brownfield-mixed"
OUT="$TMP/mixed"
mkdir -p "$OUT"
cp -a "$FIX/." "$OUT/"
set +e
out="$("${PY[@]}" --root "$OUT" --preset ask-kit 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "mixed stack should stop: $out"
printf '%s\n' "$out" | grep -qiE 'choice|eslint|biome' || fail "mixed message: $out"
[[ ! -f "$OUT/.agents/verification.yaml" ]] || fail "mixed wrote yaml"

echo "PASS: scaffold yaml only if absent; re-scaffold candidate; mixed-stack stops"
