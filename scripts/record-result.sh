#!/usr/bin/env bash
# Record a workstream result; refuse when commit SHA is missing.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

WORK_ID=""
SHA=""
RESULT=""
NOTES=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --work-id) WORK_ID="$2"; shift 2 ;;
    --commit-sha) SHA="$2"; shift 2 ;;
    --result) RESULT="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$WORK_ID" ]]; then
  echo "record-result: --work-id required" >&2
  exit 2
fi
if [[ -z "$SHA" ]]; then
  echo "record-result: refusing — --commit-sha is required (missing commit SHA)" >&2
  exit 1
fi
if [[ -z "$RESULT" ]]; then
  echo "record-result: --result required" >&2
  exit 2
fi

WS="work/${WORK_ID}"
mkdir -p "$WS"
OUT="${WS}/result.json"
python3 - <<PY
import json
doc={
  "work_id": "$WORK_ID",
  "commit_sha": "$SHA",
  "result": "$RESULT",
  "notes": """$NOTES""",
}
open("$OUT","w").write(json.dumps(doc, indent=2)+"\n")
print(f"record-result: wrote {doc['work_id']} @ {doc['commit_sha']} -> $OUT")
PY
