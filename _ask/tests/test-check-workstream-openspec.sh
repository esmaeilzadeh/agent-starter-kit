#!/usr/bin/env bash
# Marked-pilot check-workstream: missing/incomplete/invalid fail; non-pilot unchanged.
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
git add README.md && git commit -q -m init

mkdir -p _ask/scripts work/demo specs/current
cp "$ROOT/_ask/scripts/check-clean-worktree.sh" \
   "$ROOT/_ask/scripts/check-workstream.sh" \
   "$ROOT/_ask/scripts/openspec_cli.py" \
   _ask/scripts/
cp "$ROOT/_ask/openspec-pin.yaml" _ask/openspec-pin.yaml
chmod +x _ask/scripts/*.sh _ask/scripts/*.py

cat > _ask/scripts/openspec-stub.sh <<'STUB'
#!/usr/bin/env bash
set -euo pipefail
echo "$@" >> "${STUB_LOG:-/tmp/stub.log}"
case "${1:-}" in
  --version) printf '%s\n' "${STUB_VERSION:-1.13.0}"; exit 0 ;;
  validate) cat "${STUB_VALIDATE_JSON}"; exit "${STUB_VALIDATE_EXIT:-0}" ;;
  status) cat "${STUB_STATUS_JSON}"; exit "${STUB_STATUS_EXIT:-0}" ;;
  *) echo "stub unexpected $*" >&2; exit 2 ;;
esac
STUB
chmod +x _ask/scripts/openspec-stub.sh
export OPENSPEC_BIN="$TMP/_ask/scripts/openspec-stub.sh"
export STUB_LOG="$PAYLOADS/stub.log"
: > "$STUB_LOG"

cat > "$PAYLOADS/valid.json" <<'JSON'
{"items": [{"id": "demo", "valid": true}], "root": {"path": "/tmp", "source": "nearest"}}
JSON
cat > "$PAYLOADS/invalid.json" <<'JSON'
{"items": [{"id": "demo", "valid": false}], "root": {"path": "/tmp", "source": "nearest"}}
JSON
cat > "$PAYLOADS/complete.json" <<'JSON'
{"changeName": "demo", "isPlanningComplete": true, "isComplete": true,
 "artifacts": [{"id": "tasks", "status": "done"}],
 "root": {"path": "/tmp", "source": "nearest"}}
JSON
cat > "$PAYLOADS/incomplete.json" <<'JSON'
{"changeName": "demo", "isPlanningComplete": false, "isComplete": false,
 "artifacts": [{"id": "proposal", "status": "blocked"}],
 "root": {"path": "/tmp", "source": "nearest"}}
JSON
export STUB_VALIDATE_JSON="$PAYLOADS/valid.json"
export STUB_VALIDATE_EXIT=0
export STUB_STATUS_JSON="$PAYLOADS/complete.json"
export STUB_STATUS_EXIT=0

# --- non-pilot: unrelated specs/current is enough (today's behavior) ---
git checkout -q -b agent/demo
mkdir -p work/demo specs/current
printf '# Intent\n\n## What\n\nnon-pilot\n' > work/demo/intent.md
printf '# Plan\n' > work/demo/plan.md
printf '# Specification: other\n\n## Status\n\nCURRENT\n' > specs/current/other.md
git add work specs _ask && git commit -q -m seed
./_ask/scripts/check-workstream.sh demo >/tmp/cw-out.txt
# non-pilot must not invoke stub
if grep -q validate "$STUB_LOG"; then
  echo "FAIL: non-pilot invoked OpenSpec" >&2
  exit 1
fi

# --- pilot, missing change, unrelated spec exists ---
cat > work/demo/intent.md <<'EOF'
# Intent

Engine: openspec

## What

pilot
EOF
printf '# Plan\n' > work/demo/plan.md
git add work && git commit -q -m 'mark pilot'
set +e
./_ask/scripts/check-workstream.sh demo >/tmp/cw-out.txt 2>/tmp/cw-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'missing OpenSpec change' /tmp/cw-err.txt

# --- pointer duplicate plan ---
mkdir -p openspec/changes/demo
printf 'schema: spec-driven\n' > openspec/changes/demo/.openspec.yaml
cat > work/demo/plan.md <<'EOF'
# Plan

## Approach

Do the thing in kit plan.md.

## Work breakdown

1. Duplicate.
EOF
git add work openspec && git commit -q -m 'dup plan'
set +e
./_ask/scripts/check-workstream.sh demo >/tmp/cw-out.txt 2>/tmp/cw-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'meaningful plan content' /tmp/cw-err.txt

# --- skip_specs without reason ---
printf '# Plan\n' > work/demo/plan.md
printf 'schema: spec-driven\nskip_specs: true\n' > openspec/changes/demo/.openspec.yaml
git add work openspec && git commit -q -m skip
set +e
./_ask/scripts/check-workstream.sh demo >/tmp/cw-out.txt 2>/tmp/cw-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'skip_specs' /tmp/cw-err.txt

# --- valid complete active change ---
printf 'schema: spec-driven\n' > openspec/changes/demo/.openspec.yaml
printf '# Plan\n\nCanonical: openspec/changes/demo/\n' > work/demo/plan.md
git add work openspec && git commit -q -m ok
: > "$STUB_LOG"
./_ask/scripts/check-workstream.sh demo >/tmp/cw-out.txt
grep -q 'validate demo --strict --json' "$STUB_LOG"
grep -q -- '--change demo --json' "$STUB_LOG"

# --- invalid ---
export STUB_VALIDATE_JSON="$PAYLOADS/invalid.json"
set +e
./_ask/scripts/check-workstream.sh demo >/tmp/cw-out.txt 2>/tmp/cw-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'invalid change' /tmp/cw-err.txt
export STUB_VALIDATE_JSON="$PAYLOADS/valid.json"

# --- incomplete ---
export STUB_STATUS_JSON="$PAYLOADS/incomplete.json"
set +e
./_ask/scripts/check-workstream.sh demo >/tmp/cw-out.txt 2>/tmp/cw-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'incomplete' /tmp/cw-err.txt
export STUB_STATUS_JSON="$PAYLOADS/complete.json"

echo "PASS: check-workstream OpenSpec pilot marker, missing, duplicate, skip_specs, invalid, incomplete, pass"
