#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOME="$(mktemp -d)"
export HOME
trap 'rm -rf "$HOME"' EXIT
unset ASKIT_SKIP_COMPLETION_INSTALL
unset XDG_DATA_HOME
unset BASH_COMPLETION_USER_DIR

ASKIT_DIR="$ROOT" "$ROOT/_ask/scripts/install-user-completion.sh"

[[ -f "$HOME/.local/share/askit/complete.bash" ]]
[[ -f "$HOME/.local/share/bash-completion/completions/ask" ]]
[[ -f "$HOME/.local/share/bash-completion/completions/askit" ]]
grep -q askit-completion "$HOME/.bashrc"
grep -q askit-completion "$HOME/.zshrc"

# Second run does not duplicate the hook.
ASKIT_DIR="$ROOT" "$ROOT/_ask/scripts/install-user-completion.sh"
[[ "$(grep -c askit-completion "$HOME/.bashrc")" -eq 1 ]]

echo "PASS: askit installs user completion files and a one-time rc hook"
