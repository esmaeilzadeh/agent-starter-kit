#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HOME="$(mktemp -d)"
export HOME
trap 'rm -rf "$HOME"' EXIT
unset XDG_CACHE_HOME
export ASKIT_SKIP_COMPLETION_INSTALL=1

REF="$(git -C "$ROOT" rev-parse HEAD)"

# The legacy no-argument invocation directs users to the pinned install.
code=0
out="$(env -u KIT_REF -u KIT_COMMIT bash -s <"$ROOT/askit" 2>&1)" || code=$?
[[ "$code" -eq 2 ]]
[[ "$out" == *"full expected commit is required"* ]]
[[ "$out" == *"#install-askit"* ]]
[[ ! -e "$HOME/.local/bin/askit" ]]

# Exercise the installer entry point with a pinned source revision.
bash -s -- --source "$ROOT" --ref "$REF" --expected-commit "$REF" \
  --prefix "$HOME/.local" <"$ROOT/askit"

[[ -L "$HOME/.local/bin/askit" ]]
[[ -x "$HOME/.local/bin/askit" ]]
[[ "$(git -C "$HOME/.cache/askit/kit" rev-parse --is-shallow-repository)" == true ]]

TMP="$(mktemp -d)"
trap 'rm -rf "$HOME" "$TMP"' EXIT
cd "$TMP"
set +e
out="$("$ROOT/askit" status 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]]
printf '%s\n' "$out" | grep -qi 'non-git'
! printf '%s\n' "$out" | grep -q start-work

out="$("$ROOT/askit" self-install --help)"
printf '%s\n' "$out" | grep -q self-install

echo "PASS: askit self-install verifies and installs a pinned source revision"
