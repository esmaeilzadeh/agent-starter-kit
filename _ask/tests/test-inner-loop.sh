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

# --- retry bounds ---
out="$("${PY[@]}" next-action --review-round 0 --debug-round 0 --verdict REJECTED --boundary ok)"
[[ "$out" == implement ]] || fail "reject 1 → implement: $out"
out="$("${PY[@]}" next-action --review-round 1 --debug-round 0 --verdict REJECTED --boundary ok)"
[[ "$out" == implement ]] || fail "reject 2 → implement: $out"
out="$("${PY[@]}" next-action --review-round 2 --debug-round 0 --verdict REJECTED --boundary ok)"
[[ "$out" == debug ]] || fail "reject 3 → debug: $out"
out="$("${PY[@]}" next-action --review-round 2 --debug-round 1 --verdict REJECTED --boundary ok)"
[[ "$out" == debug ]] || fail "debug 2 still debug: $out"
out="$("${PY[@]}" next-action --review-round 2 --debug-round 2 --verdict REJECTED --boundary ok)"
[[ "$out" == blocked ]] || fail "after 2 debug → blocked: $out"
out="$("${PY[@]}" next-action --review-round 0 --debug-round 0 --verdict REJECTED --boundary glob_too_narrow)"
[[ "$out" == blocked ]] || fail "glob_too_narrow → blocked no retry: $out"
out="$("${PY[@]}" next-action --review-round 0 --debug-round 0 --verdict APPROVED --boundary ok)"
[[ "$out" == integrate ]] || fail "approved → integrate: $out"

# --- FF integrate; cherry-pick forbidden ---
FF="$TMP/ff"
git init -q "$FF"
git -C "$FF" config user.email t@e.com
git -C "$FF" config user.name t
echo base > "$FF/f"
git -C "$FF" add f
git -C "$FF" commit -q -m base
base=$(git -C "$FF" rev-parse HEAD)
git -C "$FF" checkout -q -b task
echo task > "$FF/f"
git -C "$FF" add f
git -C "$FF" commit -q -m task
git -C "$FF" checkout -q master 2>/dev/null || git -C "$FF" checkout -q main
sha="$("${PY[@]}" --root "$FF" integrate --task-ref task --method ff-only)"
[[ "$sha" == "$(git -C "$FF" rev-parse HEAD)" ]] || fail "ff HEAD"
[[ "$sha" != "$base" ]] || fail "ff advanced"
set +e
out="$("${PY[@]}" --root "$FF" integrate --task-ref task --method cherry-pick 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "cherry-pick must be forbidden"
printf '%s\n' "$out" | grep -qi forbidden || fail "forbidden message: $out"

# --- resume abort to ancestor coordinator_sha ---
echo dirty > "$FF/f"
coord=$(git -C "$FF" rev-parse HEAD)
out="$("${PY[@]}" --root "$FF" resume-repair --coordinator-sha "$coord")"
[[ "$out" == aborted ]] || fail "dirty resume abort: $out"
[[ -z "$(git -C "$FF" status --porcelain)" ]] || fail "resume left dirty"

# --- driver: run / resume from state.json / cancel / integrate TDD gate ---
DRV="$TMP/drv"
git init -q "$DRV"
git -C "$DRV" config user.email t@e.com
git -C "$DRV" config user.name t
echo base > "$DRV/f"
git -C "$DRV" add f
git -C "$DRV" commit -q -m base
mkdir -p "$DRV/work/drv/inner-loop/results"
cat > "$DRV/work/drv/inner-loop/tasks.yaml" <<'YAML'
schema: ask-inner-loop-tasks/v1
work_id: drv
tasks:
  - id: t-a
    depends_on: []
    owned_paths: [a/**]
  - id: t-b
    depends_on: [t-a]
    owned_paths: [b/**]
YAML
out="$("${PY[@]}" --root "$DRV" run drv)"
printf '%s\n' "$out" | grep -q 'running=t-a' || fail "run starts first ready: $out"
out="$("${PY[@]}" --root "$DRV" run drv)"
printf '%s\n' "$out" | grep -q 'waiting=t-a' || fail "second run waits, no second writer: $out"

# missing TDD
cat > "$DRV/work/drv/inner-loop/results/t-a.json" <<'JSON'
{"schema":"ask-task-result/v1","task_id":"t-a","tdd":null,"exemption":null}
JSON
set +e
out="$("${PY[@]}" --root "$DRV" run drv 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "missing TDD should not integrate: $out"
printf '%s\n' "$out" | grep -qi 'tdd\|integrat' || fail "missing TDD message: $out"

# exemption without reviewer_ack
cat > "$DRV/work/drv/inner-loop/results/t-a.json" <<'JSON'
{"schema":"ask-task-result/v1","task_id":"t-a","tdd":null,"exemption":{"kind":"documentation-only","reason":"x"}}
JSON
set +e
out="$("${PY[@]}" --root "$DRV" run drv 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]] || fail "unchecked exemption should not integrate: $out"
printf '%s\n' "$out" | grep -qi 'reviewer_ack\|exemption' || fail "exemption message: $out"

# red then green
cat > "$DRV/work/drv/inner-loop/results/t-a.json" <<'JSON'
{"schema":"ask-task-result/v1","task_id":"t-a","tdd":{"seam":"a","red":{"command":"t","output":"FAIL","exit_code":1},"green":{"command":"t","output":"PASS","exit_code":0}},"exemption":null}
JSON
out="$("${PY[@]}" --root "$DRV" run drv)"
printf '%s\n' "$out" | grep -q 'running=t-b' || fail "after TDD integrate, next ready: $out"
st="$("${PY[@]}" --root "$DRV" status drv)"
printf '%s\n' "$st" | grep -q 't-a	integrated' || fail "t-a integrated: $st"

# exemption with reviewer_ack
cat > "$DRV/work/drv/inner-loop/results/t-b.json" <<'JSON'
{"schema":"ask-task-result/v1","task_id":"t-b","tdd":null,"exemption":{"kind":"documentation-only","reason":"x","reviewer_ack":true}}
JSON
out="$("${PY[@]}" --root "$DRV" run drv)"
printf '%s\n' "$out" | grep -q 'quiescent' || fail "all integrated → quiescent: $out"

# resume from state.json (dirty abort using coordinator_sha in state)
echo dirty > "$DRV/f"
out="$("${PY[@]}" --root "$DRV" resume drv)"
printf '%s\n' "$out" | grep -Eq 'aborted|quiescent' || fail "resume from state.json: $out"
[[ -z "$(git -C "$DRV" status --porcelain --untracked-files=no)" ]] || fail "resume left tracked dirty"
grep -q base "$DRV/f" || fail "resume did not restore coordinator file"

# cancel
mkdir -p "$DRV/work/cnl/inner-loop"
cat > "$DRV/work/cnl/inner-loop/tasks.yaml" <<'YAML'
schema: ask-inner-loop-tasks/v1
work_id: cnl
tasks:
  - id: x
    depends_on: []
    owned_paths: [x/**]
YAML
out="$("${PY[@]}" --root "$DRV" run cnl)"
printf '%s\n' "$out" | grep -q 'running=x' || fail "cancel fixture run: $out"
out="$("${PY[@]}" --root "$DRV" cancel cnl all)"
printf '%s\n' "$out" | grep -qi cancelled || fail "cancel all: $out"
st="$("${PY[@]}" --root "$DRV" status cnl)"
printf '%s\n' "$st" | grep -q 'x	cancelled' || fail "x cancelled: $st"

echo "PASS: inner-loop graph validate, CAS, single-writer, commit-allowlist, retry-resume, driver"
