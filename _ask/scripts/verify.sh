#!/usr/bin/env bash
# Discover and run configured checks; print commit SHA; emit JSON summary.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

WORK_ID=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --work-id)
      if [[ $# -lt 2 || "$2" == -* ]]; then
        echo "verify: --work-id requires an id" >&2
        exit 2
      fi
      WORK_ID="$2"
      shift 2
      ;;
    -h|--help)
      cat <<'EOF'
Usage: ./ask verify [--work-id <id>]

Run repo checks; print commit SHA. Refuses a dirty tree.
--work-id <id>   write work/<id>/verification.json; marked pilots also run
                 targeted OpenSpec validation
Env: VERIFY_OUT_DIR, VERIFY_JSON  (used when --work-id is omitted)
EOF
      exit 0
      ;;
    *)
      echo "verify: unknown arg $1" >&2
      exit 2
      ;;
  esac
done

"$ROOT/_ask/scripts/check-clean-worktree.sh"

SHA="$(git rev-parse HEAD 2>/dev/null || echo unknown)"
OUT_DIR="${VERIFY_OUT_DIR:-.}"
if [[ -n "$WORK_ID" ]]; then
  OUT_JSON="work/${WORK_ID}/verification.json"
  mkdir -p "work/${WORK_ID}"
else
  OUT_JSON="${VERIFY_JSON:-${OUT_DIR}/verification-result.json}"
fi

CHECKS=()
if [[ -f .starter-kit/verify.conf ]]; then
  # shellcheck disable=SC1091
  source .starter-kit/verify.conf
fi
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

if [[ -n "$WORK_ID" && -f "work/${WORK_ID}/intent.md" ]] \
  && grep -qE '^Engine:[[:space:]]*openspec[[:space:]]*$' "work/${WORK_ID}/intent.md"; then
  CLI="$ROOT/_ask/scripts/openspec_cli.py"
  echo "verify: running: openspec validate ${WORK_ID} --strict"
  set +e
  python3 "$CLI" --root "$ROOT" validate "$WORK_ID" >/tmp/ask-verify-os.json 2>/tmp/ask-verify-os.err
  os_code=$?
  set -e
  if [[ "$os_code" -eq 0 ]]; then
    results+=("{\"check\":\"openspec validate --strict\",\"result\":\"pass\"}")
  else
    cat /tmp/ask-verify-os.err >&2 || true
    results+=("{\"check\":\"openspec validate --strict\",\"result\":\"fail\",\"code\":${os_code}}")
    overall=1
  fi
fi

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
export ASK_VERIFY_SHA="$SHA" ASK_VERIFY_OVERALL="$overall" ASK_VERIFY_OUT="$OUT_JSON" ASK_VERIFY_WID="$WORK_ID"
python3 - <<PY
import json, os
joined = """$joined"""
checks = json.loads("[" + joined + "]") if joined.strip() else []
wid = os.environ.get("ASK_VERIFY_WID") or ""
doc = {
    "commit_sha": os.environ["ASK_VERIFY_SHA"],
    "result": "pass" if os.environ["ASK_VERIFY_OVERALL"] == "0" else "fail",
    "checks": checks,
}
if wid:
    doc = {
        "work_id": wid,
        "commit_sha": doc["commit_sha"],
        "checks": checks,
        "result": doc["result"],
        "notes": "",
    }
print(json.dumps(doc, indent=2))
open(os.environ["ASK_VERIFY_OUT"], "w").write(json.dumps(doc, indent=2) + "\n")
PY

echo "verify: commit_sha=$SHA"
exit $overall
