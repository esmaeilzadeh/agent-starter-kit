#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
PAYLOADS="$(mktemp -d)"
trap 'rm -rf "$TMP" "$PAYLOADS"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo x > README.md
mkdir -p _ask/scripts work/demo
cp "$ROOT/_ask/scripts/check-clean-worktree.sh" \
   "$ROOT/_ask/scripts/verify.sh" \
   "$ROOT/_ask/scripts/openspec_cli.py" \
   _ask/scripts/
cp "$ROOT/_ask/openspec-pin.yaml" _ask/openspec-pin.yaml
chmod +x _ask/scripts/*.sh _ask/scripts/*.py
git add README.md _ask work && git commit -q -m init

echo dirty > dirty.txt
sha="$(git rev-parse HEAD)"
set +e
./_ask/scripts/verify.sh --work-id demo >/tmp/vf-out.txt 2>/tmp/vf-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -qi dirty /tmp/vf-err.txt
rm -f dirty.txt

# no checks in this repo → pass, write work/demo/verification.json
./_ask/scripts/verify.sh --work-id demo >/tmp/vf-out.txt
python3 - <<PY
import json
doc=json.load(open("work/demo/verification.json"))
assert doc["work_id"]=="demo"
assert doc["result"]=="pass"
assert doc["commit_sha"]
assert doc["notes"]==""
assert isinstance(doc["checks"], list)
PY
test -f work/demo/verification.json

# pilot: stub validate
cat > _ask/scripts/openspec-stub.sh <<'STUB'
#!/usr/bin/env bash
echo "$@" >> "${STUB_LOG}"
case "${1:-}" in
  --version) echo 1.13.0; exit 0 ;;
  validate) cat "${STUB_VALIDATE_JSON}"; exit "${STUB_VALIDATE_EXIT:-0}" ;;
  *) exit 2 ;;
esac
STUB
chmod +x _ask/scripts/openspec-stub.sh
export OPENSPEC_BIN="$TMP/_ask/scripts/openspec-stub.sh"
export STUB_LOG="$PAYLOADS/stub.log"
cat > "$PAYLOADS/valid.json" <<'JSON'
{"items": [{"id": "demo", "valid": true}], "root": {"path": "/tmp", "source": "nearest"}}
JSON
export STUB_VALIDATE_JSON="$PAYLOADS/valid.json"
export STUB_VALIDATE_EXIT=0
printf 'Engine: openspec\n' > work/demo/intent.md
mkdir -p openspec/changes/demo
printf 'schema: spec-driven\n' > openspec/changes/demo/.openspec.yaml
git add work _ask openspec && git commit -q -m pilot
: > "$STUB_LOG"
./_ask/scripts/verify.sh --work-id demo >/tmp/vf-out.txt
grep -q 'validate demo --strict --json' "$STUB_LOG"
python3 - <<'PY'
import json
doc=json.load(open("work/demo/verification.json"))
assert any(c.get("check")=="openspec validate --strict" and c.get("result")=="pass" for c in doc["checks"])
PY
git add work/demo/verification.json && git commit -q -m evidence

export STUB_VALIDATE_EXIT=1
cat > "$PAYLOADS/invalid.json" <<'JSON'
{"items": [{"id": "demo", "valid": false}], "root": {"path": "/tmp", "source": "nearest"}}
JSON
export STUB_VALIDATE_JSON="$PAYLOADS/invalid.json"
set +e
./_ask/scripts/verify.sh --work-id demo >/tmp/vf-out.txt 2>/tmp/vf-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]

# archive without Accept SHA — preflight fails
git add -A && git commit -q -m 'after invalid' || true
mkdir -p openspec/changes/archive/2026-09-14-demo
mv openspec/changes/demo/.openspec.yaml openspec/changes/archive/2026-09-14-demo/
rm -rf openspec/changes/demo
git add -A && git commit -q -m 'direct archive'
set +e
./_ask/scripts/verify.sh --work-id demo >/tmp/vf-out.txt 2>/tmp/vf-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'no Accept SHA' /tmp/vf-err.txt

echo "PASS: verify refuses dirty, writes work/<id>/verification.json, pilots run targeted validate"
