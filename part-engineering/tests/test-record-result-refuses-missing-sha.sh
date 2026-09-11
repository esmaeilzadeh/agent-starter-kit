#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
set +e
"$ROOT/part-engineering/scripts/record-result.sh" --work-id demo --result pass >/dev/null 2>&1
code=$?
set -e
if [[ "$code" -eq 0 ]]; then
  echo "FAIL: expected missing SHA to refuse" >&2
  exit 1
fi
echo "PASS: record-result refuses missing commit SHA"
