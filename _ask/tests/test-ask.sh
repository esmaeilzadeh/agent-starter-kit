#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ASK="$ROOT/ask"

"$ASK" --help | grep -q 'Agent Starter Kit'
"$ASK" --help | grep -q 'status'
"$ASK" --help | grep -q '.agents/ask/'
grep -q 'context-audit.md' "$ROOT/.agents/ask/stages/10-accept.md"
grep -q 'open' "$ROOT/.agents/ask/stages/10-accept.md"
"$ASK" --help | grep -q 'setup'
"$ASK" --help | grep -q -- '--dry-run'
"$ASK" --help | grep -q -- '--commit-sha'
"$ASK" --help | grep -q -- '--work-id'
"$ASK" --help | grep -q 'completion'
"$ASK" -h | grep -q 'install'
"$ASK" | grep -q 'Usage:'
out="$("$ASK" --complete 1 ./ask st)"
printf '%s\n' "$out" | grep -q start-work
out="$("$ASK" --complete 2 ./ask install)"
printf '%s\n' "$out" | grep -q -- '--dry-run'
printf '%s\n' "$out" | grep -q -- '--force'
printf '%s\n' "$out" | grep -q -- '--skip-prepare'
out="$("$ASK" --complete 2 ./ask record-result)"
printf '%s\n' "$out" | grep -q -- '--work-id'
printf '%s\n' "$out" | grep -q -- '--commit-sha'
out="$("$ASK" --complete 2 ./ask start-work)"
printf '%s\n' "$out" | grep -q -- '--help'
out="$("$ASK" --complete 2 ./ask upgrade)"
printf '%s\n' "$out" | grep -q -- '--version'
out="$("$ASK" completion bash)"
printf '%s\n' "$out" | grep -q '_ask_kit_complete'
out="$("$ASK" completion zsh)"
printf '%s\n' "$out" | grep -q 'compdef'
for sub in check-clean start-work check-workstream status verify record-result record-run sync install upgrade prepare setup completion; do
  out="$("$ASK" --complete 2 ./ask "$sub")"
  printf '%s\n' "$out" | grep -q . 
done

# Simulate Tab after "./ask start" (unique) and "./ask sta" (start-work + status).
# Must run in the kit repo so ./ask completion is not replaced by askit self-install.
# shellcheck disable=SC2034
eval "$("$ASK" completion bash)"
COMP_WORDS=(./ask start)
COMP_CWORD=1
_ask_kit_complete
printf '%s\n' "${COMPREPLY[@]}" | grep -q start-work
COMP_WORDS=(./ask sta)
COMP_CWORD=1
_ask_kit_complete
printf '%s\n' "${COMPREPLY[@]}" | grep -q start-work
printf '%s\n' "${COMPREPLY[@]}" | grep -q status

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
