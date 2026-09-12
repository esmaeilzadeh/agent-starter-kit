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
echo dirty > dirty.txt
sha="$(git rev-parse HEAD)"
set +e
./_ask/scripts/record-run.sh --run-id demo --commit-sha "$sha" --metric 0.9 >/tmp/rr-out.txt 2>/tmp/rr-err.txt
code=$?
set -e
if [[ "$code" -eq 0 ]]; then
  echo "FAIL: record-run must refuse dirty tree" >&2
  cat /tmp/rr-err.txt >&2
  exit 1
fi
echo "PASS: record-run refuses dirty tree"
