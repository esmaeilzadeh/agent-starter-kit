#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
git check-ignore -q .later/some-card.md
if git check-ignore -q .later/README.md; then
  echo "FAIL: .later/README.md must not be ignored" >&2
  exit 1
fi
echo "PASS: later-inbox gitignore keeps README, ignores cards"
