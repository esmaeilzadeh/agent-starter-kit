#!/usr/bin/env bash
# Verify workstream preconditions before delegated implement/review/refactor.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ $# -lt 1 || -z "${1:-}" ]]; then
  echo "usage: check-workstream.sh <work-id> [--allow-dirty]" >&2
  exit 2
fi
WORK_ID="$1"
ALLOW_DIRTY=0
shift || true
for arg in "$@"; do
  case "$arg" in
    --allow-dirty) ALLOW_DIRTY=1 ;;
    *) echo "unknown arg: $arg" >&2; exit 2 ;;
  esac
done

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
EXPECTED="agent/${WORK_ID}"
if [[ "$BRANCH" != "$EXPECTED" ]]; then
  echo "check-workstream: branch '${BRANCH}' is not dedicated to work-id '${WORK_ID}' (expected '${EXPECTED}')" >&2
  exit 1
fi

if [[ "$ALLOW_DIRTY" -eq 0 ]]; then
  "$ROOT/part-engineering/scripts/check-clean-worktree.sh"
fi

WS="work/${WORK_ID}"
if [[ ! -d "$WS" ]]; then
  echo "check-workstream: missing workstream dir ${WS}" >&2
  exit 1
fi

# Accepted spec: prefer specs/current/* or STATUS CURRENT in specs
SPEC_OK=0
if compgen -G "specs/current/*" > /dev/null; then
  SPEC_OK=1
fi
if [[ "$SPEC_OK" -eq 0 ]]; then
  while IFS= read -r -d '' f; do
    if grep -qiE '^## Status[[:space:]]*$' "$f" 2>/dev/null; then
      # next non-empty line
      st=$(awk 'BEGIN{s=0} /^## Status/{s=1;next} s && NF{print; exit}' "$f")
      if echo "$st" | grep -qiE 'CURRENT|ACCEPTED'; then
        SPEC_OK=1
        break
      fi
    fi
  done < <(find specs -type f -name '*.md' -print0 2>/dev/null || true)
fi
if [[ "$SPEC_OK" -eq 0 ]]; then
  echo "check-workstream: no accepted specification found under specs/current/ (or Status CURRENT)" >&2
  exit 1
fi

if [[ ! -f "${WS}/plan.md" ]]; then
  echo "check-workstream: missing plan ${WS}/plan.md" >&2
  exit 1
fi

echo "check-workstream: ok work-id=${WORK_ID} branch=${BRANCH}"
exit 0
