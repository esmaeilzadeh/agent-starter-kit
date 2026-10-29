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

"$ROOT/_ask/scripts/check-clean-worktree.sh"
"$ROOT/_ask/scripts/access-check.sh"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "start-work: not a git repository" >&2
  exit 2
fi

TPL="$ROOT/_ask/templates"
for required in intent.md plan.md review.md verification.json acceptance.md; do
  if [[ ! -f "$TPL/$required" ]]; then
    echo "start-work: required template is missing: $TPL/$required" >&2
    exit 1
  fi
done

# Base new workstreams on develop. Fail closed if that branch is missing.
if git show-ref --verify --quiet refs/heads/develop; then
  BASE=develop
elif git show-ref --verify --quiet refs/remotes/origin/develop; then
  BASE=origin/develop
else
  echo "start-work: create a local 'develop' branch first (Git-flow integration branch)." >&2
  echo "start-work: refusing to branch from main/master." >&2
  exit 1
fi

# Owner refs are part of the project inventory. Serialize their publication
# with capture_project through the persistent Git-common-dir lock.
COMMON_DIR="$(git rev-parse --git-common-dir)"
if [[ "$COMMON_DIR" != /* ]]; then COMMON_DIR="$ROOT/$COMMON_DIR"; fi
mkdir -p "$COMMON_DIR/ask-locks"
exec {REF_LOCK_FD}>>"$COMMON_DIR/ask-locks/references.lock"
flock -x "$REF_LOCK_FD"
if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
  git checkout -q "$BRANCH"
else
  git checkout -q -b "$BRANCH" "$BASE"
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
# explore-map.md is created only when 00 Explore runs (real skip leaves no map)
copy_tpl "$TPL/intent.md" "$WS/intent.md"
copy_tpl "$TPL/plan.md" "$WS/plan.md"
copy_tpl "$TPL/review.md" "$WS/review.md"
copy_tpl "$TPL/verification.json" "$WS/verification.json"
copy_tpl "$TPL/acceptance.md" "$WS/acceptance.md"

flock -u "$REF_LOCK_FD"
exec {REF_LOCK_FD}>&-

echo "start-work: work-id=${WORK_ID}"
echo "start-work: branch=$(git rev-parse --abbrev-ref HEAD)"
echo "start-work: HEAD=$(git rev-parse HEAD)"
echo "start-work: workstream=${WS}"
