#!/usr/bin/env bash
# Prepare the selected pinned skills after validating their identities and approvals.
set -euo pipefail

ROOT="${ASK_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
MANIFEST="$ROOT/.agents/ask.local/skills/manifest.yaml"
if [[ ! -f "$MANIFEST" ]]; then
  MANIFEST="$ROOT/_ask/skills/manifest.yaml"
fi
exec python3 "$ROOT/_ask/scripts/distribution.py" \
  --root "$ROOT" \
  --manifest "$MANIFEST" \
  --pins "$ROOT/_ask/skills/dependency-pins.json"
