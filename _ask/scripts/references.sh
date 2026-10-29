#!/usr/bin/env bash
# Public workflow-reference command surface.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="$ROOT/.agents/ask${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m workflow_refs "$@"
