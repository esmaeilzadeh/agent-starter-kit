#!/usr/bin/env bash
# Run the language-neutral CheckPlan. Logic lives in .agents/ask/verification/.
set -euo pipefail

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: ./ask verify

Checks run as trusted account-local code with filesystem and network access.
Run untrusted changes in isolated CI.
EOF
  exit 0
fi
if (($#)); then echo 'verify: unsupported argument' >&2; exit 2; fi

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export ASK_ROOT="${ASK_ROOT:-$ROOT}"
exec python3 "$ROOT/.agents/ask/verification/run.py"
