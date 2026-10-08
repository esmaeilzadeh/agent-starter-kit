#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="$ROOT/.agents/ask${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m verification.traceability.cli "$@"
