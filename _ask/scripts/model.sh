#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  export PYTHONPATH="$ROOT/_ask/scripts${PYTHONPATH:+:$PYTHONPATH}"
  exec python3 -m engineering_model --help
fi
if [[ "${1:-}" != "validate" ]]; then
  echo "usage: ./ask model validate --work-id <work-id>" >&2
  exit 2
fi
shift
export PYTHONPATH="$ROOT/_ask/scripts${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m engineering_model validate "$@"
