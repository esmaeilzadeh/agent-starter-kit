#!/usr/bin/env bash
# Overlay the kit into the current git repo. askit calls this only after confirm.
# Env: ASKIT_KIT_ROOT  ASKIT_INSTALL_FLAGS (default --skip-prepare)
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "askit: ask is not applicable in a non-git folder" >&2
  exit 1
fi

TARGET="$(git rev-parse --show-toplevel)"
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

if [[ ! -x "$TARGET/ask" || ! -d "$TARGET/_ask" ]]; then
  echo "askit: overlay did not produce ./ask and _ask/" >&2
  exit 1
fi
