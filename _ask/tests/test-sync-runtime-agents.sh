#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
TMP="$(mktemp -d)"
PROJECTION_DIRS=(
  .cursor/agents
  .claude/agents
  .codex/agents
  .opencode/agents
)
for index in "${!PROJECTION_DIRS[@]}"; do
  projection_dir="${PROJECTION_DIRS[$index]}"
  if [[ -d "$projection_dir" ]]; then
    cp -a "$projection_dir" "$TMP/projection-$index"
    touch "$TMP/present-$index"
  fi
done

restore_projections() {
  for index in "${!PROJECTION_DIRS[@]}"; do
    projection_dir="${PROJECTION_DIRS[$index]}"
    rm -rf "$projection_dir"
    if [[ -e "$TMP/present-$index" ]]; then
      cp -a "$TMP/projection-$index" "$projection_dir"
    fi
  done
  rm -rf "$TMP"
}
trap restore_projections EXIT

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
grep -q 'model = "gpt-6-luna"' .codex/agents/kit-06-implement.toml

test -f .opencode/agents/kit-06-implement.md
grep -q '^description:' .opencode/agents/kit-06-implement.md
grep -q '^mode: subagent$' .opencode/agents/kit-06-implement.md
grep -q '^model:' .opencode/agents/kit-06-implement.md
if grep -qE '^(tools|maxSteps):' .opencode/agents/kit-06-implement.md; then
  echo "FAIL: OpenCode agent emits deprecated tools/maxSteps" >&2
  exit 1
fi
grep -q 'edit: deny' .opencode/agents/kit-07-review.md

env -u ASK_WORK_ID ASK_RISK=HIGH python3 _ask/scripts/sync-runtime-agents.py >/dev/null
grep -q 'model: kimi-k3' .cursor/agents/kit-07-review.md
grep -q 'model = "gpt-6-astra"' .codex/agents/kit-07-review.toml
env -u ASK_WORK_ID ASK_MODEL_07_REVIEW=thinking python3 _ask/scripts/sync-runtime-agents.py >/dev/null
grep -q 'model: grok-4.6' .cursor/agents/kit-07-review.md
grep -q 'model = "gpt-6.1-sol"' .codex/agents/kit-07-review.toml
./_ask/scripts/sync-cursor-binding.sh >/dev/null

if [[ "${ASK_SYNC_TEST_FORCE_FAILURE:-0}" == "1" ]]; then
  echo "FAIL: forced post-sync failure for cleanup verification" >&2
  exit 97
fi

python3 -m unittest discover -s _ask/tests -p test_codex_effort.py

echo "PASS: sync writes per-runtime Review/Implement models; defaults and 07-review have no slugs"
