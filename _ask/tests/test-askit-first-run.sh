#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ASKIT="$ROOT/askit"
# Verification sets ASK_ROOT to the candidate checkout. This test deliberately
# exercises separate consumer directories, so let each command resolve from
# its working directory instead of writing generated projections into the kit.
unset ASK_ROOT
export ASKIT_KIT_ROOT="$ROOT"
export ASKIT_SKIP_SETUP=1
export ASKIT_SKIP_COMPLETION_INSTALL=1
export ASKIT_INSTALL_FLAGS=--skip-prepare

# Non-git folder: refuse. Do not overlay. Do not dump kit commands.
NONE="$(mktemp -d)"
trap 'rm -rf "$NONE"' EXIT
cd "$NONE"
set +e
out="$("$ASKIT" status 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]]
printf '%s\n' "$out" | grep -qi 'non-git'
! printf '%s\n' "$out" | grep -q start-work
[[ ! -e "$NONE/ask" ]]
[[ ! -d "$NONE/_ask" ]]

# Git repo without the kit: no silent overlay, no command catalog.
TMP="$(mktemp -d)"
trap 'rm -rf "$NONE" "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo app > README.md
git add README.md && git commit -q -m init

set +e
out="$("$ASKIT" status 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]]
printf '%s\n' "$out" | grep -q 'not ask-based'
! printf '%s\n' "$out" | grep -q start-work
[[ ! -e "$TMP/ask" ]]
[[ ! -d "$TMP/_ask" ]]

help="$("$ASKIT" --help 2>&1 || true)"
printf '%s\n' "$help" | grep -q 'installed launcher'
! printf '%s\n' "$help" | grep -q start-work
! printf '%s\n' "$help" | grep -q 'no ./ask'

# Explicit overlay does not imply trust; commands stay gated until that choice.
set +e
out="$(ASKIT_ADD_ASK=1 "$ASKIT" status 2>&1)"
code=$?
set -e
[[ "$code" -ne 0 ]]
printf '%s\n' "$out" | grep -q 'run askit trust'
[[ -x "$TMP/ask" ]]
[[ -d "$TMP/_ask" ]]
git check-ignore -q ask
git check-ignore -q AGENTS.md
git add . && git commit -qm 'Keep project configuration only'
git clone -q . "$NONE/fresh"
cd "$NONE/fresh"
[[ ! -e ask && ! -d _ask && ! -e AGENTS.md ]]
[[ -z "$(git ls-files -- .cursor .codex .claude .opencode .agents/ask .agents/skills)" ]]
out="$(ASKIT_ADD_ASK=1 "$ASKIT" 2>&1 || true)"
printf '%s\n' "$out" | grep -q 'run askit trust'
./ask access-check
[[ -z "$(git status --porcelain)" ]]

echo "PASS: first-run askit gates on Git and confirmation, then installs the ignored runtime per checkout"
