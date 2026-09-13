#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOME="$(mktemp -d)"
export HOME
trap 'rm -rf "$HOME"' EXIT
unset XDG_CACHE_HOME
export ASKIT_SKIP_COMPLETION_INSTALL=1

REF="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD)"

# Same path as curl | bash: the file *is* the installer.
bash -s -- --source "$ROOT" --ref "$REF" --prefix "$HOME/.local" <"$ROOT/askit"

[[ -L "$HOME/.local/bin/askit" ]]
[[ -x "$HOME/.local/bin/askit" ]]

TMP="$(mktemp -d)"
trap 'rm -rf "$HOME" "$TMP"' EXIT
cd "$TMP"
out="$("$ROOT/askit" --help)"
printf '%s\n' "$out" | grep -q '/askit | bash'
printf '%s\n' "$out" | grep -q self-install
! printf '%s\n' "$out" | grep -q install-askit

out="$("$ROOT/askit" self-install --help)"
printf '%s\n' "$out" | grep -q self-install

echo "PASS: askit installs itself (curl | bash and self-install)"
