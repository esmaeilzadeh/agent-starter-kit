#!/usr/bin/env bash
# Create a dedicated work branch and workstream skeleton for <work-id>.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ $# -lt 1 || -z "${1:-}" ]]; then
  echo "usage: start-work.sh <work-id>" >&2
  exit 2
fi
WORK_ID="$1"
BRANCH="agent/${WORK_ID}"

"$ROOT/part-engineering/scripts/check-clean-worktree.sh"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "start-work: not a git repository" >&2
  exit 2
fi

# Prefer main, then master, then current default
DEFAULT_BRANCH="$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || true)"
if [[ -z "$DEFAULT_BRANCH" ]]; then
  if git show-ref --verify --quiet refs/heads/main; then
    DEFAULT_BRANCH=main
  elif git show-ref --verify --quiet refs/heads/master; then
    DEFAULT_BRANCH=master
  else
    DEFAULT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  fi
fi

if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  git checkout -q "$BRANCH"
else
  git checkout -q -b "$BRANCH" "$DEFAULT_BRANCH"
fi

WS="work/${WORK_ID}"
mkdir -p "$WS"
# Seed from templates when missing
copy_tpl() {
  local src="$1" dest="$2"
  if [[ ! -e "$dest" ]]; then
    cp "$src" "$dest"
  fi
}
TPL="$ROOT/part-engineering/templates"
copy_tpl "$TPL/explore-map.md" "$WS/explore-map.md"
copy_tpl "$TPL/intent.md" "$WS/intent.md"
copy_tpl "$TPL/plan.md" "$WS/plan.md"
copy_tpl "$TPL/review.md" "$WS/review.md"
copy_tpl "$TPL/verification.json" "$WS/verification.json"
copy_tpl "$TPL/acceptance.md" "$WS/acceptance.md"

echo "start-work: work-id=${WORK_ID}"
echo "start-work: branch=$(git rev-parse --abbrev-ref HEAD)"
echo "start-work: HEAD=$(git rev-parse HEAD)"
echo "start-work: workstream=${WS}"
