#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ASK="$ROOT/ask"

"$ASK" --help | grep -q 'Agent Starter Kit'
"$ASK" --help | grep -q 'status'
"$ASK" --help | grep -q 'setup'
"$ASK" --help | grep -q -- '--dry-run'
"$ASK" --help | grep -q -- '--commit-sha'
"$ASK" --help | grep -q -- '--work-id'
"$ASK" --help | grep -q 'completion'
"$ASK" -h | grep -q 'install'
"$ASK" | grep -q 'Usage:'
"$ASK" --complete 1 ./ask st | grep -q start-work
"$ASK" --complete 2 ./ask install -- | grep -q -- '--dry-run'
"$ASK" completion bash | grep -q '_ask_kit_complete'
"$ASK" completion zsh | grep -q 'compdef'
set +e
"$ASK" nosuchcmd >/dev/null 2>&1
code=$?
set -e
[[ "$code" -ne 0 ]]

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo x > README.md
git add README.md && git commit -q -m init
# invoke ask by absolute path; check-clean uses cwd git
"$ASK" check-clean

echo "PASS: ask help, unknown-command, check-clean on clean temp repo"
