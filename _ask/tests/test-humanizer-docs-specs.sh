#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

grep -q 'source: blader/humanizer' _ask/skills/manifest.yaml
grep -q 'revision: "v3.0.0"' _ask/skills/manifest.yaml
grep -q 'role: docs-voice' _ask/skills/manifest.yaml
grep -q 'skill: humanizer' _ask/skills/manifest.yaml

[[ -f .cursor/rules/humanizer-docs-specs.mdc ]]
grep -q 'embedded mode' .cursor/rules/humanizer-docs-specs.mdc
grep -q 'humanizer' .cursor/rules/humanizer-docs-specs.mdc

for f in _ask/agents/02-spec.md _ask/agents/03-spec-challenge.md _ask/agents/04-spec-change.md; do
  grep -q 'humanizer' "$f"
done

[[ -f _ask/docs/adr/0017-humanizer-docs-specs.md ]]
grep -q '0017' _ask/spec/06-phases-and-acceptance.md

echo "PASS: humanizer pin, rule, Spec-stage contracts, and ADR 0017"
