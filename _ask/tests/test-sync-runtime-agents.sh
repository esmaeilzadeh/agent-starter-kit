#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# Portable defaults and protocol must not name vendor slugs.
if grep -qiE 'grok|composer-|claude-|gpt-|sonnet|opus|haiku|fable|muse-' \
  .agents/ask/bindings/models.defaults.yaml; then
  echo "FAIL: models.defaults.yaml contains a vendor slug" >&2
  exit 1
fi
if grep -qiE 'grok-|composer-|claude-sonnet|gpt-5|haiku|opus|fable' \
  .agents/ask/stages/07-review.md; then
  echo "FAIL: 07-review.md contains a vendor slug" >&2
  exit 1
fi

./_ask/scripts/sync-cursor-binding.sh >/dev/null

grep -q 'model: grok-4.6' .cursor/agents/kit-07-review.md
grep -q 'readonly: true' .cursor/agents/kit-07-review.md
grep -q 'model: composer-2.5' .cursor/agents/kit-06-implement.md
grep -q 'model: sonnet' .claude/agents/kit-07-review.md
grep -q 'model = "gpt-5.4-mini"' .codex/agents/kit-06-implement.toml

ASK_RISK=HIGH python3 _ask/scripts/sync-runtime-agents.py >/dev/null
grep -q 'model: kimi-k3' .cursor/agents/kit-07-review.md
ASK_MODEL_07_REVIEW=thinking python3 _ask/scripts/sync-runtime-agents.py >/dev/null
grep -q 'model: grok-4.6' .cursor/agents/kit-07-review.md
./_ask/scripts/sync-cursor-binding.sh >/dev/null

echo "PASS: sync writes per-runtime Review/Implement models; defaults and 07-review have no slugs"
