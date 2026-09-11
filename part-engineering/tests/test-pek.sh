#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PEK="$ROOT/pek"

"$PEK" --help | grep -q 'Part Engineering Kit'
"$PEK" check-clean
set +e
"$PEK" nosuchcmd >/dev/null 2>&1
code=$?
set -e
[[ "$code" -ne 0 ]]
echo "PASS: pek help, check-clean, unknown-command"
