#!/usr/bin/env bash
# Write ask/askit tab-completion into the user's shell. Called from askit.
# Cannot inject into the parent shell; new Tab uses bash-completion drop-ins
# and a one-time rc hook for the next prompt.
set -euo pipefail

if [[ -n "${ASKIT_SKIP_COMPLETION_INSTALL:-}" ]]; then
  exit 0
fi
if [[ -z "${HOME:-}" || ! -w "$HOME" ]]; then
  exit 0
fi

ASKIT_DIR="${ASKIT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
ASK_BIN="${ASKIT_DIR}/ask"
if [[ ! -x "$ASK_BIN" ]]; then
  exit 0
fi

DATA="${XDG_DATA_HOME:-$HOME/.local/share}/askit"
BC_DIR="${BASH_COMPLETION_USER_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/bash-completion}/completions"
mkdir -p "$DATA" "$BC_DIR"

"$ASK_BIN" completion bash > "$DATA/complete.bash"
"$ASK_BIN" completion zsh > "$DATA/complete.zsh"
cp -f "$DATA/complete.bash" "$BC_DIR/ask"
cp -f "$DATA/complete.bash" "$BC_DIR/askit"

ensure_rc_hook() {
  local rc="$1"
  local snippet="$2"
  if [[ ! -e "$rc" ]]; then
    printf '%s\n' "$snippet" > "$rc"
    return 0
  fi
  if grep -q 'askit-completion' "$rc" 2>/dev/null; then
    return 0
  fi
  printf '\n%s\n' "$snippet" >> "$rc"
}

ensure_rc_hook "${HOME}/.bashrc" "$(cat <<EOF
# askit-completion
if [ -f \"\${XDG_DATA_HOME:-\$HOME/.local/share}/askit/complete.bash\" ]; then
  . \"\${XDG_DATA_HOME:-\$HOME/.local/share}/askit/complete.bash\"
fi
EOF
)"

ensure_rc_hook "${HOME}/.zshrc" "$(cat <<EOF
# askit-completion
if [ -f \"\${XDG_DATA_HOME:-\$HOME/.local/share}/askit/complete.zsh\" ]; then
  . \"\${XDG_DATA_HOME:-\$HOME/.local/share}/askit/complete.zsh\"
fi
EOF
)"
