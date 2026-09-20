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
grep -q 'workspaces:' "$TMP/.agents/verification.yaml" || fail "named workspace sections"

# wizard preview (no write)
prev="$("${PY[@]}" --root "$TMP" --wizard-preview --preset ask-kit)"
printf '%s\n' "$prev" | grep -q 'workspaces:' || fail "preview names workspaces"
[[ -f "$TMP/.agents/verification.yaml" ]] || fail "preview must not delete yaml"

# rollback restores previous yaml
python3 - <<PY
from pathlib import Path
import sys
sys.path.insert(0, "$ROOT/_ask/scripts")
import verify_scaffold as vs
dest = Path("$TMP/.agents/verification.yaml")
old = dest.read_text()
try:
    vs.apply_with_rollback(dest, "schema: mutated\n", after_write=lambda: (_ for _ in ()).throw(RuntimeError("boom")))
except RuntimeError:
    pass
else:
    raise SystemExit("expected boom")
if dest.read_text() != old:
    raise SystemExit("rollback did not restore yaml")
print("rollback ok")
PY

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

# workspace-local biome vs root eslint stops
WS="$TMP/ws"
mkdir -p "$WS/packages/app"
printf '%s\n' '{"workspaces":["packages/*"]}' > "$WS/package.json"
printf '%s\n' '{"name":"app"}' > "$WS/packages/app/package.json"
echo '{}' > "$WS/eslint.config.js"
echo '{}' > "$WS/packages/app/biome.json"
set +e
out="$("${PY[@]}" --root "$WS" --preset ask-kit 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "workspace lint disagreement should stop: $out"

echo "PASS: scaffold yaml only if absent; re-scaffold candidate; mixed-stack stops"
