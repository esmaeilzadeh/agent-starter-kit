#!/usr/bin/env bash
# First-run: overlay this kit into cwd, then setup (TTY). Sourced or exec'd from askit.
# Env: ASKIT_KIT_ROOT  ASKIT_SKIP_SETUP=1  ASKIT_INSTALL_FLAGS (default --skip-prepare)
set -euo pipefail

if [[ ! -d .git ]]; then
  echo "askit: current directory is not a git repo" >&2
  exit 1
fi

TARGET="$(pwd)"
KIT="${ASKIT_KIT_ROOT:-}"
if [[ -z "$KIT" && -x "${ASKIT_DIR:-}/ask" && -x "${ASKIT_DIR:-}/_ask/scripts/install-kit.sh" ]]; then
  KIT="$ASKIT_DIR"
fi
if [[ -z "$KIT" && -x "${XDG_CACHE_HOME:-$HOME/.cache}/askit/kit/ask" ]]; then
  KIT="${XDG_CACHE_HOME:-$HOME/.cache}/askit/kit"
fi
if [[ -z "$KIT" ]]; then
  echo "askit: no kit cache. Install this command first:" >&2
  echo "  curl -fsSL https://raw.githubusercontent.com/esmaeilzadeh/agent-starter-kit/main/askit | bash" >&2
  exit 1
fi

# shellcheck disable=SC2086
"$KIT/ask" install ${ASKIT_INSTALL_FLAGS:---skip-prepare} "$TARGET"

if [[ -z "${ASKIT_SKIP_SETUP:-}" && -t 0 && -t 1 && -x "$TARGET/ask" ]]; then
  echo "askit: overlay done. Starting setup."
  exec "$TARGET/ask" setup
fi

if [[ ! -x "$TARGET/ask" ]]; then
  echo "askit: overlay did not produce ./ask" >&2
  exit 1
fi
