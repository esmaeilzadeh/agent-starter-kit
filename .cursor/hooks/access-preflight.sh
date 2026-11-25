#!/usr/bin/env bash
# Cursor session-start adapter for the shared AskIt workflow.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
exec python3 "$ROOT/_ask/scripts/session-start.py" cursor
