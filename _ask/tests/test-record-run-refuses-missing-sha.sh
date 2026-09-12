#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
chmod +x "$ROOT/_ask/scripts/record-run.sh"
set +e
"$ROOT/_ask/scripts/record-run.sh" --run-id demo --metric 0.9 >/dev/null 2>&1
code=$?
set -e
if [[ "$code" -eq 0 ]]; then
  echo "FAIL: expected missing SHA to refuse" >&2
  exit 1
fi
echo "PASS: record-run refuses missing commit SHA"
