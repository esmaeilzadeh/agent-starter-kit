#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/_ask/skills" "$TMP/_ask/scripts" "$TMP/.agents/ask.local/skills"
cp "$ROOT/_ask/skills/prepare-skills.sh" "$TMP/_ask/skills/"
cp "$ROOT/_ask/skills/manifest.yaml" "$TMP/_ask/skills/manifest.yaml"
cp "$ROOT/_ask/skills/dependency-pins.json" "$TMP/_ask/skills/dependency-pins.json"
cp "$ROOT/_ask/scripts/distribution.py" "$TMP/_ask/scripts/distribution.py"
cat > "$TMP/.agents/ask.local/skills/manifest.yaml" <<'YAML'
skills:
  bad:
    source: example/skills
    revision: latest
    skill: bad
    role: test
    required: true
YAML
cd "$TMP"
set +e
SKIP_INSTALL=1 ./_ask/skills/prepare-skills.sh >"$TMP/prep-out.txt" 2>"$TMP/prep-err.txt"
code=$?
set -e
if [[ "$code" -eq 0 ]]; then
  echo "FAIL: expected latest to be refused" >&2
  cat "$TMP/prep-err.txt" >&2
  exit 1
fi
grep -qi 'latest' "$TMP/prep-err.txt"
echo "PASS: prepare-skills refuses revision=latest"
