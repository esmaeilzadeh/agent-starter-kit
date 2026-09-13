#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
for f in _ask/agents/01-grill.md _ask/agents/00-explore.md _ask/spec/03-policies-skills-context.md; do
  grep -q 'ask before' "$f"
  grep -q 'manifest' "$f"
done
grep -q "I'll assume" _ask/agents/01-grill.md || grep -q 'I’ll assume' _ask/agents/01-grill.md
grep -q '0016' _ask/docs/adr/0007-grilling-expanded-qa-before-resolution.md
[[ -f _ask/docs/adr/0016-grilling-load-bearing-and-skill-before.md ]]
echo "PASS: grilling-skip-trivia contracts mention ask-before-prepare, assume-list, ADR 0016"
