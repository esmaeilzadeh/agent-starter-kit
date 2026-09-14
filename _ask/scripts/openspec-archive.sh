#!/usr/bin/env bash
# Kit-mediated openspec-archive. Refuses without an Accept SHA.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

if [[ $# -lt 1 || -z "${1:-}" || "${1:-}" == -* ]]; then
  echo "usage: ./ask openspec-archive <work-id>" >&2
  exit 2
fi
WORK_ID="$1"
CLI="$ROOT/_ask/scripts/openspec_cli.py"

sha="$(python3 - <<PY
from pathlib import Path
import sys
sys.path.insert(0, "$ROOT/_ask/scripts")
from openspec_cli import accept_sha, repo_root
print(accept_sha(repo_root("$ROOT"), "$WORK_ID"))
PY
)"
if [[ -z "$sha" ]]; then
  echo "openspec-archive: refuse — work/${WORK_ID}/acceptance.md has no accepted commit SHA" >&2
  exit 1
fi

python3 "$CLI" --root "$ROOT" archive "$WORK_ID"
echo "openspec-archive: archived ${WORK_ID} after Accept ${sha}"
