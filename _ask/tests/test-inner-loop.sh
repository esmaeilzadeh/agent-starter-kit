#!/usr/bin/env bash
# Inner-loop graph validate, CAS, single-writer.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ASK="$ROOT/ask"
PY=(python3 "$ROOT/_ask/scripts/inner_loop/__main__.py")
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fail() { echo "FAIL: $*" >&2; exit 1; }

# --- cycle ---
mkdir -p "$TMP/work/cycle/inner-loop"
cat > "$TMP/work/cycle/inner-loop/tasks.yaml" <<'YAML'
schema: ask-inner-loop-tasks/v1
work_id: cycle
tasks:
  - id: a
    depends_on: [b]
    owned_paths: [one/**]
  - id: b
    depends_on: [a]
    owned_paths: [two/**]
YAML
set +e
out="$("${PY[@]}" --root "$TMP" validate cycle 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "cycle should be nonzero"
printf '%s\n' "$out" | grep -q cycle || fail "cycle status in output: $out"

# --- path_conflict: overlap, no depends_on ---
mkdir -p "$TMP/work/conflict/inner-loop"
cat > "$TMP/work/conflict/inner-loop/tasks.yaml" <<'YAML'
schema: ask-inner-loop-tasks/v1
work_id: conflict
tasks:
  - id: a
    depends_on: []
    owned_paths: [pkg/**]
  - id: b
    depends_on: []
    owned_paths: [pkg/mod.py]
YAML
set +e
out="$("${PY[@]}" --root "$TMP" validate conflict 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "path_conflict should be nonzero"
printf '%s\n' "$out" | grep -q path_conflict || fail "path_conflict status: $out"

# --- overlap with depends_on is ok ---
mkdir -p "$TMP/work/ordered/inner-loop"
cat > "$TMP/work/ordered/inner-loop/tasks.yaml" <<'YAML'
schema: ask-inner-loop-tasks/v1
work_id: ordered
tasks:
  - id: a
    depends_on: []
    owned_paths: [pkg/**]
  - id: b
    depends_on: [a]
    owned_paths: [pkg/mod.py]
YAML
out="$("${PY[@]}" --root "$TMP" validate ordered 2>&1)"
printf '%s\n' "$out" | grep -q '^ok$' || fail "ordered overlap should be ok: $out"

# --- CAS ---
mkdir -p "$TMP/work/cas/inner-loop"
cat > "$TMP/work/cas/inner-loop/tasks.yaml" <<'YAML'
schema: ask-inner-loop-tasks/v1
work_id: cas
tasks:
  - id: t
    depends_on: []
    owned_paths: [x/**]
YAML
"${PY[@]}" --root "$TMP" cas-init cas
out="$("${PY[@]}" --root "$TMP" cas-apply cas --observed 0)"
printf '%s\n' "$out" | grep -q 'revision=1' || fail "cas apply: $out"
set +e
out="$("${PY[@]}" --root "$TMP" cas-apply cas --observed 0 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "stale CAS should fail"
printf '%s\n' "$out" | grep -qi 'revision' || fail "stale CAS message: $out"

# --- worker cannot write state ---
set +e
out="$(ASK_INNER_LOOP_ROLE=worker "${PY[@]}" --root "$TMP" cas-apply cas --observed 1 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "worker CAS should fail"
printf '%s\n' "$out" | grep -qi 'protocol' || fail "worker protocol message: $out"

# --- second writer refused ---
"${PY[@]}" --root "$TMP" spawn-writer cas t
set +e
out="$("${PY[@]}" --root "$TMP" spawn-writer cas t 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "second writer should fail"
printf '%s\n' "$out" | grep -qi 'second writer' || fail "second writer message: $out"

# dispatcher
"$ASK" inner-loop --help 2>&1 | grep -q validate

# --- commit allowlist ---
set +e
out="$("${PY[@]}" check-paths --glob 'pkg/**' -- pkg/a.py 2>&1)"
code=$?
set -e
[[ "$code" -eq 0 ]] || fail "in-glob path should pass: $out"

set +e
out="$("${PY[@]}" check-paths --glob 'pkg/**' -- README.md 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "out-of-glob path should fail"
printf '%s\n' "$out" | grep -q README.md || fail "rejected path named: $out"

out="$("${PY[@]}" classify-paths --glob 'pkg/**' --required '' -- tmp/cache 2>&1)"
printf '%s\n' "$out" | grep -q '^extras$' || fail "unrequired outside glob is extras: $out"

out="$("${PY[@]}" classify-paths --glob 'pkg/**' --required 'lib/core.py' -- lib/core.py 2>&1)"
printf '%s\n' "$out" | grep -q '^glob_too_narrow$' || fail "required outside glob: $out"

REPO="$TMP/gitrepo"
mkdir -p "$REPO/pkg"
git init -q "$REPO"
git -C "$REPO" config user.email t@e.com
git -C "$REPO" config user.name t
echo in > "$REPO/pkg/a.py"
echo out > "$REPO/OUT.txt"
git -C "$REPO" add pkg/a.py OUT.txt
set +e
out="$("${PY[@]}" --root "$REPO" check-index --glob 'pkg/**' 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "staged OUT.txt should fail check-index"
printf '%s\n' "$out" | grep -q OUT.txt || fail "check-index names OUT.txt: $out"

echo "PASS: inner-loop graph validate, CAS, single-writer, commit-allowlist"
