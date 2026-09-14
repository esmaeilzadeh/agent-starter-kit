#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

grep -q 'source: blader/humanizer' _ask/skills/manifest.yaml
grep -q 'revision: "v3.0.0"' _ask/skills/manifest.yaml
grep -q 'role: docs-voice' _ask/skills/manifest.yaml
grep -q 'skill: humanizer' _ask/skills/manifest.yaml

grep -q 'skill: writing-for-agents' _ask/skills/manifest.yaml
grep -q 'source: mattpocock/skills' _ask/skills/manifest.yaml
grep -q 'role: agent-docs' _ask/skills/manifest.yaml

[[ -f .cursor/rules/humanizer-docs-specs.mdc ]]
grep -q 'embedded mode' .cursor/rules/humanizer-docs-specs.mdc
grep -q 'humanizer' .cursor/rules/humanizer-docs-specs.mdc
grep -q 'alwaysApply: false' .cursor/rules/humanizer-docs-specs.mdc
grep -q 'README.md' .cursor/rules/humanizer-docs-specs.mdc
if grep -q 'alwaysApply: true' .cursor/rules/humanizer-docs-specs.mdc; then
  echo "FAIL: humanizer rule must not be alwaysApply true" >&2
  exit 1
fi
# Humanizer rule may mention specifications only as a do-not-apply target.
if grep -E 'editing documentation or specifications' .cursor/rules/humanizer-docs-specs.mdc; then
  echo "FAIL: humanizer rule still targets specifications" >&2
  exit 1
fi

[[ -f .cursor/rules/writing-for-agents-machine-docs.mdc ]]
grep -q 'writing-for-agents' .cursor/rules/writing-for-agents-machine-docs.mdc
grep -q 'embedded mode' .cursor/rules/writing-for-agents-machine-docs.mdc

for f in _ask/agents/02-spec.md _ask/agents/03-spec-challenge.md _ask/agents/04-spec-change.md; do
  grep -q 'writing-for-agents' "$f"
  if grep -q 'follow it in embedded mode' "$f" && grep -q 'humanizer/SKILL.md' "$f"; then
    echo "FAIL: $f still applies humanizer" >&2
    exit 1
  fi
done

[[ -f _ask/docs/adr/0017-humanizer-docs-specs.md ]]
grep -q 'writing-for-agents' _ask/docs/adr/0017-humanizer-docs-specs.md
grep -q '0017' _ask/spec/06-phases-and-acceptance.md
grep -q 'SUPERSEDED' specs/current/pin-humanizer.md
grep -q 'humanizer-human-docs-only.md' specs/current/pin-humanizer.md

echo "PASS: humanizer human-facing scope, writing-for-agents on machine-first files, ADR 0017"
