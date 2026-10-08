#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  export PYTHONPATH="$ROOT/_ask/scripts${PYTHONPATH:+:$PYTHONPATH}"
  exec python3 -m engineering_model --help
fi
if [[ "${1:-}" != "validate" && "${1:-}" != "admit" && "${1:-}" != "show" ]]; then
  echo "usage: ./ask model {validate|admit|show} --work-id <work-id>" >&2
  exit 2
fi
export PYTHONPATH="$ROOT/_ask/scripts${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m engineering_model "$@"
