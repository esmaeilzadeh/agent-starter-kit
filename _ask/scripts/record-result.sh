#!/usr/bin/env bash
# Argument translation only; Python owns provenance and completion policy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORK_ID="" SHA="" RESULT="" NOTES=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --work-id) WORK_ID="$2"; shift 2 ;;
    --commit-sha) SHA="$2"; shift 2 ;;
    --result) RESULT="$2"; shift 2 ;;
    --notes) NOTES="$2"; shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$WORK_ID" && -n "$RESULT" ]] || { echo 'record-result: work-id and result required' >&2; exit 2; }
[[ -n "$SHA" ]] || { echo 'record-result: refusing — missing commit SHA' >&2; exit 1; }
exec "$ROOT/_ask/scripts/traceability.sh" --root "$ROOT" record-result "$WORK_ID" --candidate-sha "$SHA" --result "$RESULT" --notes "$NOTES"
