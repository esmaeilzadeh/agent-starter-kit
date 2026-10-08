#!/usr/bin/env bash
# Run the language-neutral CheckPlan. Logic lives in .agents/ask/verification/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export ASK_ROOT="${ASK_ROOT:-$ROOT}"
exec python3 "$ROOT/.agents/ask/verification/run.py"
