#!/usr/bin/env bash
# Current-checkout status uses targeted OpenSpec CLI and strips nextSteps.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
STATUS="$ROOT/_ask/scripts/status.sh"
TMP="$(mktemp -d)"
PAYLOADS="$(mktemp -d)"
trap 'rm -rf "$TMP" "$PAYLOADS"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo x > README.md
git add README.md && git commit -q -m init
git branch -M main
git checkout -q -b agent/demo

mkdir -p _ask/scripts work/demo openspec/changes/demo
cp "$ROOT/_ask/scripts/openspec_cli.py" _ask/scripts/
cp "$ROOT/_ask/openspec-pin.yaml" _ask/
cat > _ask/scripts/openspec-stub.sh <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
echo "$@" >> "${STUB_LOG}"
case "${1:-}" in
  --version) echo 1.13.0; exit 0 ;;
  status) cat "${STUB_STATUS_JSON}"; exit 0 ;;
  *) echo "stub $*" >&2; exit 2 ;;
esac
STUB
chmod +x _ask/scripts/openspec-stub.sh _ask/scripts/openspec_cli.py
export OPENSPEC_BIN="$TMP/_ask/scripts/openspec-stub.sh"
export STUB_LOG="$PAYLOADS/stub.log"
cat > "$PAYLOADS/status.json" <<'JSON'
{
  "changeName": "demo",
  "isPlanningComplete": true,
  "isComplete": true,
  "nextSteps": ["Run openspec instructions apply --change \"demo\" --json"],
  "root": {"path": "/tmp", "source": "nearest"}
}
JSON
export STUB_STATUS_JSON="$PAYLOADS/status.json"

cat > work/demo/intent.md <<'EOF'
# Intent

Engine: openspec

## What

demo
EOF
printf '# Plan\n' > work/demo/plan.md
printf 'schema: spec-driven\n' > openspec/changes/demo/.openspec.yaml
git add . && git commit -q -m demo

: > "$STUB_LOG"
out="$("$STATUS" --json --work-id demo)"
echo "$out" | python3 -c '
import json,sys
doc=json.load(sys.stdin)
row=doc["workstreams"][0]
assert row["stage"]=="planned"
assert row["artifacts"].get("openspec_plan") is True
ost=row["artifacts"].get("openspec_status") or {}
assert ost.get("isPlanningComplete") is True
'
grep -q -- '--change demo --json' "$STUB_LOG"
if grep -q 'openspec instructions' <<<"$out"; then
  echo "FAIL: status JSON leaked OpenSpec nextSteps" >&2
  exit 1
fi

echo "PASS: status current-checkout OpenSpec CLI, planned, nextSteps stripped"
