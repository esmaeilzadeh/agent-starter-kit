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
mkdir -p _ask/scripts results/demo .agents/ask
cp "$ROOT/_ask/scripts/check-clean-worktree.sh" "$ROOT/_ask/scripts/record-run.sh" _ask/scripts/
mkdir -p .agents/ask/workflow_refs
cp "$ROOT"/.agents/ask/workflow_refs/*.py .agents/ask/workflow_refs/
chmod +x _ask/scripts/*.sh
echo "lr: 0.1" > results/demo/config.yaml
git add _ask results .agents && git commit -q -m cfg
sha="$(git rev-parse HEAD)"
./_ask/scripts/record-run.sh --run-id demo --commit-sha "$sha" --metric 0.91
test -f results/demo/run_manifest.json
grep -q 'repository-runs/run/1@1' results/demo/run_manifest.json
! grep -q "$sha" results/demo/run_manifest.json
grep -q '0.91' results/demo/summary.json
grep -q demo results/RUN_REGISTRY.md
grep -q "$sha" results/references/integrity.json
grep -q 'source_bindings' results/references/integrity.json
# Dirty worktree and missing SHA still refuse.
set +e
./_ask/scripts/record-run.sh --run-id dirty --commit-sha "$sha" --metric 0.1 >/dev/null 2>&1
code=$?
./_ask/scripts/record-run.sh --run-id missing-sha --metric 0.1 >/dev/null 2>&1
missing_code=$?
set -e
[[ "$code" -ne 0 && "$missing_code" -ne 0 ]]
git add results && git commit -q -m "record run fixture"
clean_sha="$(git rev-parse HEAD)"
# SHA != HEAD and missing config still refuse after a clean checkpoint.
set +e
./_ask/scripts/record-run.sh --run-id wrong-sha --commit-sha deadbeef --metric 0.1 >/dev/null 2>&1
wrong_code=$?
./_ask/scripts/record-run.sh --run-id missing-config --commit-sha "$clean_sha" --metric 0.1 >/dev/null 2>&1
config_code=$?
set -e
[[ "$wrong_code" -ne 0 && "$config_code" -ne 0 ]]
echo "PASS: record-run writes manifest and refuses SHA ≠ HEAD"
