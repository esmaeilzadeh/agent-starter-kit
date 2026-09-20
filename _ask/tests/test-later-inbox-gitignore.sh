#!/usr/bin/env bash
# Later cards are committable (Git-flow: commit on develop + tracker issue).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
if git check-ignore -q .later/some-card.md; then
  echo "FAIL: .later/*.md cards must be committable on develop" >&2
  exit 1
fi
if git check-ignore -q .later/README.md; then
  echo "FAIL: .later/README.md must not be ignored" >&2
  exit 1
fi
echo "PASS: later-inbox cards are committable; README stays tracked"
