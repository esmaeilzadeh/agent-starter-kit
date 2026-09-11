#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PEK="$ROOT/pek"

"$PEK" --help | grep -q 'Part Engineering Kit'
set +e
"$PEK" nosuchcmd >/dev/null 2>&1
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
# invoke pek by absolute path; check-clean uses cwd git
"$PEK" check-clean

echo "PASS: pek help, unknown-command, check-clean on clean temp repo"
