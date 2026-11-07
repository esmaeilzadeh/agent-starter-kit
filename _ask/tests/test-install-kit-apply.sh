#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
mkdir -p docs
echo consumer > docs/README.md
echo init > README.md
echo 'consumer-cache/' > .gitignore
git add . && git commit -q -m init
SKIP_INSTALL=1 "$ROOT/_ask/scripts/install-kit.sh" --skip-prepare "$TMP"
test -d "$TMP/_ask"
test -f "$TMP/_ask/scripts/check-clean-worktree.sh"
test -d "$TMP/.cursor"
test -x "$TMP/ask"
grep -q consumer "$TMP/docs/README.md"
test ! -e "$TMP/scripts/check-clean-worktree.sh"
test ! -d "$TMP/_ask/tests"
for path in spec guide decisions .venv docs/research docs/demo README.md MAPPING.md OWNED-PATHS.md; do
  test ! -e "$TMP/_ask/$path"
done
test ! -e "$TMP/ai-agent-engineering-guide.md"
test ! -e "$TMP/ai-agent-starter-kit-spec.md"
test -z "$(find "$TMP/_ask" -name __pycache__ -o -name '*.pyc')"
for path in policies/workflow.md templates/plan.md scripts/inner_loop/__main__.py ui/streamlit_app.py docs/inner-loop-evidence.md docs/spec-test-traceability.md; do
  test -f "$TMP/_ask/$path"
done
test ! -e "$TMP/askit"
test ! -e "$TMP/install-askit.sh"
grep -qxF 'consumer-cache/' "$TMP/.gitignore"
git check-ignore -q _ask/scripts/check-clean-worktree.sh
SKIP_INSTALL=1 "$ROOT/_ask/scripts/install-kit.sh" --skip-prepare "$TMP" >/dev/null
test "$(grep -cxF '_ask/' "$TMP/.gitignore")" -eq 1
"$TMP/ask" --help >/dev/null
"$TMP/ask" sync >/dev/null
echo "PASS: install-kit apply leaves docs/ intact and does not overlay root scripts/ or kit tests/"
