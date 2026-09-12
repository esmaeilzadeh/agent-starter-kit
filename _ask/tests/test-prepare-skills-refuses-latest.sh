#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/_ask/skills" "$TMP/scripts"
cp "$ROOT/_ask/skills/prepare-skills.sh" "$TMP/_ask/skills/"
cat > "$TMP/_ask/skills/manifest.yaml" <<'YAML'
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
SKIP_INSTALL=1 ./_ask/skills/prepare-skills.sh >/tmp/prep-out.txt 2>/tmp/prep-err.txt
code=$?
set -e
if [[ "$code" -eq 0 ]]; then
  echo "FAIL: expected latest to be refused" >&2
  cat /tmp/prep-err.txt >&2
  exit 1
fi
grep -qi 'latest' /tmp/prep-err.txt
echo "PASS: prepare-skills refuses revision=latest"
