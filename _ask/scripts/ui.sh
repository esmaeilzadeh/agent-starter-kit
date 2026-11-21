#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON_BIN="${ASK_PYTHON:-python3}"

if ! "$PYTHON_BIN" -m streamlit --version >/dev/null 2>&1; then
  echo "ask ui: Streamlit is unavailable; install _ask/ui/requirements.txt first." >&2
  exit 127
fi

declare -a streamlit_args=()
address_set=false
while (($#)); do
  case "$1" in
    --)
      streamlit_args+=("$@")
      break
      ;;
    --server.address=*)
      address="${1#*=}"
      shift
      ;;
    --server.address)
      shift
      if (($# == 0)) || [[ "$1" == --* ]]; then
        echo "ask ui: --server.address requires a value." >&2
        exit 2
      fi
      address="$1"
      shift
      ;;
    *)
      streamlit_args+=("$1")
      shift
      continue
      ;;
  esac

  if [[ "$address_set" == true ]]; then
    echo "ask ui: --server.address may be specified only once." >&2
    exit 2
  fi
  if [[ -z "$address" || "$address" == -* || "$address" == *[[:space:][:cntrl:]]* || "$address" == *"="* ]]; then
    echo "ask ui: invalid --server.address value." >&2
    exit 2
  fi
  streamlit_args+=("--server.address=$address")
  address_set=true
done

if [[ "$address_set" == false ]]; then
  streamlit_args=("--server.address=127.0.0.1" "${streamlit_args[@]}")
fi

exec "$PYTHON_BIN" -m streamlit run "$ROOT/_ask/ui/streamlit_app.py" "${streamlit_args[@]}"
