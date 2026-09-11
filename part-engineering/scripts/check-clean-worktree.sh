#!/usr/bin/env bash
# Refuse delegated work when the Git working tree is dirty.
# Does not stash, reset, or modify user changes — check only.
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "check-clean-worktree: not a git repository" >&2
  exit 2
fi

# porcelain covers staged, unstaged, and untracked
if [[ -n "$(git status --porcelain)" ]]; then
  echo "check-clean-worktree: working tree is dirty; commit, stash, or discard changes before starting delegated work." >&2
  git status --short >&2
  exit 1
fi

echo "check-clean-worktree: clean"
exit 0
