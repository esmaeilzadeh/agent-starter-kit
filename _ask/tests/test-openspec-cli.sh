#!/usr/bin/env bash
# Pin + invoke helper: refuse latest, fail-closed shape, no --all, strip nextSteps.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CLI="$ROOT/_ask/scripts/openspec_cli.py"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$TMP/_ask" "$TMP/bin" "$TMP/work/demo" "$TMP/payloads"
cat > "$TMP/_ask/openspec-pin.yaml" <<'YAML'
package: "@fission-ai/openspec"
revision: "1.13.0"
schema: spec-driven
profile: core
YAML

# --- pin refuses latest ---
cat > "$TMP/_ask/bad-pin.yaml" <<'YAML'
package: "@fission-ai/openspec"
revision: latest
schema: spec-driven
profile: core
YAML
set +e
python3 "$CLI" --root "$TMP" --pin "$TMP/_ask/bad-pin.yaml" load-pin >/tmp/os-out.txt 2>/tmp/os-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -qi 'latest' /tmp/os-err.txt

# --- stub CLI ---
cat > "$TMP/bin/openspec" <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
echo "$@" >> "${STUB_LOG}"
case "${1:-}" in
  --version)
    printf '%s\n' "${STUB_VERSION:-1.13.0}"
    exit 0
    ;;
  validate)
    if [[ -n "${STUB_VALIDATE_JSON:-}" ]]; then
      cat "${STUB_VALIDATE_JSON}"
    fi
    exit "${STUB_VALIDATE_EXIT:-0}"
    ;;
  status)
    if [[ -n "${STUB_STATUS_JSON:-}" ]]; then
      cat "${STUB_STATUS_JSON}"
    fi
    exit "${STUB_STATUS_EXIT:-0}"
    ;;
  *)
    echo "stub: unexpected $*" >&2
    exit 2
    ;;
esac
STUB
chmod +x "$TMP/bin/openspec"
export OPENSPEC_BIN="$TMP/bin/openspec"
export STUB_LOG="$TMP/stub.log"
: > "$STUB_LOG"

run_cli() {
  python3 "$CLI" --root "$TMP" --pin "$TMP/_ask/openspec-pin.yaml" "$@"
}

# missing binary
mkdir -p "$TMP/empty-path"
export OPENSPEC_BIN="$TMP/empty-path/openspec"
set +e
python3 "$CLI" --root "$TMP" --pin "$TMP/_ask/openspec-pin.yaml" version-assert >/tmp/os-out.txt 2>/tmp/os-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -qi 'missing' /tmp/os-err.txt
export OPENSPEC_BIN="$TMP/bin/openspec"

# version mismatch
export STUB_VERSION=9.9.9
set +e
run_cli version-assert >/tmp/os-out.txt 2>/tmp/os-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -qi 'mismatch' /tmp/os-err.txt
unset STUB_VERSION

run_cli version-assert >/tmp/os-out.txt
grep -qx '1.13.0' /tmp/os-out.txt

# root: null is failure even with exit 0
cat > "$TMP/payloads/null-root.json" <<'JSON'
{"root": null, "items": []}
JSON
export STUB_VALIDATE_JSON="$TMP/payloads/null-root.json"
export STUB_VALIDATE_EXIT=0
set +e
run_cli validate demo >/tmp/os-out.txt 2>/tmp/os-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'root: null' /tmp/os-err.txt

# exit-0 with status[].severity=error
cat > "$TMP/payloads/sev-error.json" <<'JSON'
{"status": [{"severity": "error", "code": "no_openspec_root"}]}
JSON
export STUB_VALIDATE_JSON="$TMP/payloads/sev-error.json"
set +e
run_cli validate demo >/tmp/os-out.txt 2>/tmp/os-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'severity=error' /tmp/os-err.txt

# empty-set success (items: 0, valid-looking) is a failure: no matching item
cat > "$TMP/payloads/empty.json" <<'JSON'
{"items": [], "root": {"path": "/tmp", "source": "nearest"}}
JSON
export STUB_VALIDATE_JSON="$TMP/payloads/empty.json"
set +e
run_cli validate demo >/tmp/os-out.txt 2>/tmp/os-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'no item' /tmp/os-err.txt

# valid: false
cat > "$TMP/payloads/invalid.json" <<'JSON'
{"items": [{"id": "demo", "valid": false}], "root": {"path": "/tmp", "source": "nearest"}}
JSON
export STUB_VALIDATE_JSON="$TMP/payloads/invalid.json"
set +e
run_cli validate demo >/tmp/os-out.txt 2>/tmp/os-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'invalid change' /tmp/os-err.txt

# valid true
cat > "$TMP/payloads/valid.json" <<'JSON'
{"items": [{"id": "demo", "valid": true}], "root": {"path": "/tmp", "source": "nearest"}}
JSON
export STUB_VALIDATE_JSON="$TMP/payloads/valid.json"
export STUB_VALIDATE_EXIT=0
run_cli validate demo >/tmp/os-out.txt

# helper never passes --all
if grep -q -- '--all' "$STUB_LOG"; then
  echo "FAIL: helper passed --all" >&2
  cat "$STUB_LOG" >&2
  exit 1
fi
grep -q 'validate demo --strict --json' "$STUB_LOG"

# incomplete status → gate fails; status (report) still prints
cat > "$TMP/payloads/status-incomplete.json" <<'JSON'
{
  "changeName": "demo",
  "isPlanningComplete": false,
  "isComplete": false,
  "artifacts": [{"id": "proposal", "status": "ready"}],
  "nextSteps": ["Run openspec instructions proposal --change \"demo\" --json"],
  "root": {"path": "/tmp", "source": "nearest"}
}
JSON
export STUB_STATUS_JSON="$TMP/payloads/status-incomplete.json"
export STUB_STATUS_EXIT=0
run_cli status demo >/tmp/os-out.txt
python3 - <<'PY'
import json
doc=json.load(open("/tmp/os-out.txt"))
steps=doc.get("nextSteps") or []
assert steps, "missing nextSteps"
assert all("openspec " not in s.lower() or "internal" in s.lower() for s in steps), steps
assert "Use kit stage commands" in steps[0]
PY

set +e
run_cli gate demo >/tmp/os-out.txt 2>/tmp/os-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'incomplete' /tmp/os-err.txt

# complete gate
cat > "$TMP/payloads/status-complete.json" <<'JSON'
{
  "changeName": "demo",
  "isPlanningComplete": true,
  "isComplete": true,
  "artifacts": [{"id": "proposal", "status": "done"}, {"id": "tasks", "status": "done"}],
  "nextSteps": ["Run openspec instructions apply --change \"demo\" --json"],
  "root": {"path": "/tmp", "source": "nearest"}
}
JSON
export STUB_STATUS_JSON="$TMP/payloads/status-complete.json"
run_cli gate demo >/tmp/os-out.txt

# is-pilot marker
printf 'Engine: openspec\n' > "$TMP/work/demo/intent.md"
run_cli is-pilot demo
printf '# Intent\n\n## What\n\nx\n' > "$TMP/work/demo/intent.md"
set +e
run_cli is-pilot demo
code=$?
set -e
[[ "$code" -ne 0 ]]

echo "PASS: openspec_cli pin, shape, no --all, nextSteps strip, gate incomplete"
