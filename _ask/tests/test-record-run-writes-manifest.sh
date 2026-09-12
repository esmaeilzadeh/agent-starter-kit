#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo x > README.md
git add README.md && git commit -q -m init
mkdir -p _ask/scripts results/demo
cp "$ROOT/_ask/scripts/check-clean-worktree.sh" "$ROOT/_ask/scripts/record-run.sh" _ask/scripts/
chmod +x _ask/scripts/*.sh
echo "lr: 0.1" > results/demo/config.yaml
git add _ask results && git commit -q -m cfg
sha="$(git rev-parse HEAD)"
./_ask/scripts/record-run.sh --run-id demo --commit-sha "$sha" --metric 0.91
test -f results/demo/run_manifest.json
grep -q "$sha" results/demo/run_manifest.json
grep -q '0.91' results/demo/summary.json
grep -q demo results/RUN_REGISTRY.md
# SHA ≠ HEAD must refuse
set +e
./_ask/scripts/record-run.sh --run-id demo --commit-sha deadbeef --metric 0.1 >/dev/null 2>&1
code=$?
set -e
[[ "$code" -ne 0 ]]
echo "PASS: record-run writes manifest and refuses SHA ≠ HEAD"
