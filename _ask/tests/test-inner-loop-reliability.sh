#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHONPATH="$ROOT/_ask/scripts${PYTHONPATH:+:$PYTHONPATH}" python3 "$ROOT/_ask/tests/inner_loop_reliability.py"
