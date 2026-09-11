#!/usr/bin/env bash
# Automated negative/positive paths for check-clean-worktree.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/scripts/check-clean-worktree.sh"
TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

git init -q "$TMP"
cd "$TMP"
git config user.email "test@example.com"
git config user.name "Test"
echo base > README.md
git add README.md
git commit -q -m "init"

# positive: clean
if ! "$SCRIPT" >/dev/null; then
  echo "FAIL: expected clean tree to exit 0" >&2
  exit 1
fi

# negative: dirty (untracked) — must exit non-zero and not alter files
echo dirty > dirty.txt
set +e
"$SCRIPT" >/dev/null 2>&1
code=$?
set -e
if [[ "$code" -eq 0 ]]; then
  echo "FAIL: expected dirty tree to exit non-zero" >&2
  exit 1
fi
if [[ ! -f dirty.txt ]]; then
  echo "FAIL: script must not delete user files" >&2
  exit 1
fi
# ensure no stash was created
if [[ -n "$(git stash list)" ]]; then
  echo "FAIL: script must not stash user changes" >&2
  exit 1
fi

echo "PASS: check-clean-worktree dirty-tree negative + clean positive"
