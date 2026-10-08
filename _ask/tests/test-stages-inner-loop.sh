#!/usr/bin/env bash
# 06/07/08 call the inner-loop module; owned_paths are steering globs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

for f in .agents/ask/stages/06-implement.md .agents/ask/stages/07-review.md .agents/ask/stages/08-refactor.md; do
  grep -q './ask inner-loop' "$f"
  grep -q 'owned_paths' "$f"
  grep -qiE 'steering|seam/module' "$f"
done

grep -q 'git diff --name-only' .agents/ask/stages/07-review.md

# Contracts point at the runner; they do not copy TaskGraph YAML.
if grep -qE '^id: t[0-9]' .agents/ask/stages/06-implement.md; then
  echo "FAIL: 06 inlines a TaskGraph node" >&2
  exit 1
fi

echo "PASS: 06/07/08 call inner-loop with steering owned_paths"
