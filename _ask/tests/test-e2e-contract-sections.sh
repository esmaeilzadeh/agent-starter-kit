#!/usr/bin/env bash
# Grill/Spec/Plan/06/09 require E2E applicability or not_applicable plus reason.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

for f in \
  _ask/templates/intent.md \
  _ask/templates/spec.md \
  _ask/templates/plan.md \
  .agents/ask/stages/01-grill.md \
  .agents/ask/stages/02-spec.md \
  .agents/ask/stages/05-plan.md \
  .agents/ask/stages/06-implement.md \
  .agents/ask/stages/09-verify.md
do
  grep -qiE 'e2e' "$f" || { echo "FAIL: $f missing E2E" >&2; exit 1; }
  grep -q 'not_applicable' "$f" || { echo "FAIL: $f missing not_applicable" >&2; exit 1; }
done

echo "PASS: E2E applicability or not_applicable+reason required in Grill/Spec/Plan/06/09"
