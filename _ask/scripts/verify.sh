#!/usr/bin/env bash
# Discover and run configured checks; print commit SHA; emit JSON summary.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
OUT_DIR="${VERIFY_OUT_DIR:-.}"
OUT_JSON="${VERIFY_JSON:-${OUT_DIR}/verification-result.json}"

CHECKS=()
# Project-local config
if [[ -f .starter-kit/verify.conf ]]; then
  # shellcheck disable=SC1091
  source .starter-kit/verify.conf
fi
# Default discovery: kit tests + common project entrypoints if present
if [[ ${#CHECKS[@]} -eq 0 ]]; then
  for t in _ask/tests/test-*.sh tests/test-*.sh; do
    [[ -e "$t" && -x "$t" ]] && CHECKS+=("$t")
  done
  if [[ -f package.json ]] && command -v npm >/dev/null 2>&1; then
    if grep -q '"test"' package.json; then CHECKS+=("npm test"); fi
  fi
  if [[ -f pyproject.toml || -f pytest.ini ]] && command -v pytest >/dev/null 2>&1; then
    CHECKS+=("pytest")
  fi
  if [[ -f Cargo.toml ]] && command -v cargo >/dev/null 2>&1; then
    CHECKS+=("cargo test")
  fi
fi

results=()
overall=0
for c in "${CHECKS[@]+"${CHECKS[@]}"}"; do
  echo "verify: running: $c"
  set +e
  bash -lc "$c"
  code=$?
  set -e
  if [[ $code -eq 0 ]]; then
    results+=("{\"check\":$(printf '%s' "$c" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),\"result\":\"pass\"}")
  else
    results+=("{\"check\":$(printf '%s' "$c" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'),\"result\":\"fail\",\"code\":$code}")
    overall=1
  fi
done

joined=$(IFS=,; echo "${results[*]-}")
python3 - <<PY
import json
doc={
  "commit_sha": "$SHA",
  "result": "pass" if $overall == 0 else "fail",
  "checks": [$joined]
}
print(json.dumps(doc, indent=2))
open("$OUT_JSON","w").write(json.dumps(doc, indent=2)+"\n")
PY

echo "verify: commit_sha=$SHA"
exit $overall
