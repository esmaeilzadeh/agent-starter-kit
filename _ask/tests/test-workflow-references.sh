#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
PYTHONPATH="$ROOT/.agents/ask${PYTHONPATH:+:$PYTHONPATH}" \
  python3 -m unittest _ask.tests.test_workflow_refs_e2e
