#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo init > README.md
git add README.md && git commit -q -m init
mkdir -p _ask/{bindings,skills,agents}
echo 'canary: keep-me' > _ask/bindings/models.yaml
cp "$ROOT/_ask/skills/manifest.yaml" _ask/skills/manifest.yaml
echo '# project pins' >> _ask/skills/manifest.yaml
echo 'project stage override' > _ask/agents/01-grill.local.md
SKIP_INSTALL=1 "$ROOT/_ask/scripts/install-kit.sh" --skip-prepare "$TMP"
cmp _ask/bindings/models.yaml .agents/ask.local/bindings/models.yaml
cmp _ask/skills/manifest.yaml .agents/ask.local/skills/manifest.yaml
cmp _ask/agents/01-grill.local.md .agents/ask.local/stages/01-grill.md
grep -q 'project stage override' .cursor/commands/01-grill.md
git add .agents/ask.local
printf 'codex:\n  01-grill: gpt-6.1-sol\n' > .agents/ask.local/bindings/models.yaml
SKIP_INSTALL=1 "$ROOT/_ask/scripts/install-kit.sh" --skip-prepare "$TMP"
grep -qx '  01-grill: gpt-6.1-sol' .agents/ask.local/bindings/models.yaml
grep -qx 'model = "gpt-6.1-sol"' .codex/agents/kit-01-grill.toml
echo "PASS: install-kit migrates legacy project configuration and preserves tracked overrides"
