#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${ASK_PYTHON:-python3}"

if ! "$PYTHON_BIN" -m streamlit --version >/dev/null 2>&1; then
  echo "ask ui: Streamlit is unavailable; install _ask/ui/requirements.txt first." >&2
  exit 127
fi

exec "$PYTHON_BIN" -m streamlit run "$ROOT/_ask/ui/streamlit_app.py" "$@"
