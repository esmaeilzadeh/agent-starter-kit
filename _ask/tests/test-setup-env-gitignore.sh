#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

[[ -f .ask.env.example ]]
if grep -Eiq 'token=.+[A-Za-z0-9]{12,}' .ask.env.example; then
  echo "FAIL: .ask.env.example looks like it contains a live token" >&2
  exit 1
fi
git check-ignore -q .ask.env
git check-ignore -q .ask/tracker-context.md
if git check-ignore -q .ask.env.example; then
  echo "FAIL: .ask.env.example must not be ignored" >&2
  exit 1
fi
if git check-ignore -q .ask/README.md; then
  echo "FAIL: .ask/README.md must not be ignored" >&2
  exit 1
fi
echo "PASS: setup env example is placeholders; secrets paths are ignored"
