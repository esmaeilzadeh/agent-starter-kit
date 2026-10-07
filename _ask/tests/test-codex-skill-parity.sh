#!/usr/bin/env bash
# Public CLI contract: Codex and Cursor stages share sources and overlays.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp -a "$ROOT/_ask" "$TMP/_ask"
mkdir -p "$TMP/.agents/ask" "$TMP/.agents/ask.local/stages"
cp -a "$ROOT/.agents/ask/." "$TMP/.agents/ask/"
printf '%s\n' 'local-parity-canary' > "$TMP/.agents/ask.local/stages/06-implement.md"
bash "$TMP/_ask/scripts/sync-cursor-binding.sh" >/dev/null
python3 - "$TMP" <<'PY'
import sys, re
from pathlib import Path
root=Path(sys.argv[1])
stages=sorted((root/'.agents/ask/stages').glob('[0-9][0-9]-*.md'))
assert len(stages)==11
for stage in stages:
    name='kit-'+stage.stem
    codex=root/'.agents/skills'/name/'SKILL.md'
    assert codex.is_file(), f'Missing Codex skill: {name}'
    text=codex.read_text()
    assert text.startswith(f'---\nname: {name}\ndescription: ')
    body=text.split('---\n',2)[2]
    cursor=(root/'.cursor/skills'/name/'SKILL.md').read_text().split('---\n',2)[2]
    assert body==cursor, name
    assert stage.read_text().strip() in body
    if stage.stem=='06-implement': assert 'local-parity-canary' in body
    agent=(root/'.codex/agents'/f'{name}.toml').read_text()
    assert all(re.search(r'^'+k+r' = .+',agent,re.M) for k in ('name','description','developer_instructions'))
first={p.relative_to(root):p.read_bytes() for p in (root/'.agents/skills').rglob('*') if p.is_file()}
import subprocess
subprocess.run(['bash',str(root/'_ask/scripts/sync-cursor-binding.sh')],check=True,stdout=subprocess.DEVNULL)
assert first=={p.relative_to(root):p.read_bytes() for p in (root/'.agents/skills').rglob('*') if p.is_file()}
PY
echo 'PASS: eleven Codex skills match Cursor stage bodies and overlays; sync is idempotent'

# Stale generated directories are cleaned; unrelated skills survive.
mkdir -p "$TMP/.agents/skills/community"
printf '%s\n' 'consumer-skill-canary' > "$TMP/.agents/skills/community/SKILL.md"
cp -a "$TMP/.agents/skills/kit-06-implement" "$TMP/.agents/skills/kit-99-retired"
bash "$TMP/_ask/scripts/sync-cursor-binding.sh" >/dev/null
test ! -e "$TMP/.agents/skills/kit-99-retired"
grep -q consumer-skill-canary "$TMP/.agents/skills/community/SKILL.md"

# Refuse unmarked and symlink collisions before changing outputs.
mkdir -p "$TMP/.agents/skills/kit-consumer"
printf '%s\n' 'consumer-reserved-canary' > "$TMP/.agents/skills/kit-consumer/SKILL.md"
if bash "$TMP/_ask/scripts/sync-cursor-binding.sh" > "$TMP/collision.log" 2>&1; then
  echo 'FAIL: unmarked reserved collision accepted' >&2; exit 1
fi
grep -q 'unmarked reserved skill collision' "$TMP/collision.log"
grep -q consumer-reserved-canary "$TMP/.agents/skills/kit-consumer/SKILL.md"
rm -rf "$TMP/.agents/skills/kit-consumer"
mkdir -p "$TMP/outside"
printf '%s\n' 'outside-canary' > "$TMP/outside/SKILL.md"
ln -s "$TMP/outside" "$TMP/.agents/skills/kit-consumer"
if bash "$TMP/_ask/scripts/sync-cursor-binding.sh" > "$TMP/collision.log" 2>&1; then
  echo 'FAIL: symlink reserved collision accepted' >&2; exit 1
fi
grep -q outside-canary "$TMP/outside/SKILL.md"
rm "$TMP/.agents/skills/kit-consumer"
echo 'PASS: stale ASK skills cleaned; unrelated, unmarked and symlink skills protected'

# Preparation validates the entire manifest before invoking the installer.
cp "$TMP/_ask/skills/manifest.yaml" "$TMP/manifest.saved"
cat >> "$TMP/_ask/skills/manifest.yaml" <<'YAML'
  reserved-fixture:
    source: example/skills
    revision: v1.0.0
    skill: kit-06-implement
    required: true
YAML
mkdir -p "$TMP/bin"
cat > "$TMP/bin/npx" <<'SH'
#!/usr/bin/env bash
: > "$INSTALL_CALLED"
exit 1
SH
chmod +x "$TMP/bin/npx"
if INSTALL_CALLED="$TMP/install-called" PATH="$TMP/bin:$PATH" bash "$TMP/_ask/skills/prepare-skills.sh" > "$TMP/prepare.log" 2>&1; then
  echo 'FAIL: preparation accepted reserved skill name' >&2; exit 1
fi
test ! -e "$TMP/install-called"
grep -q 'reserved' "$TMP/prepare.log"
mv "$TMP/manifest.saved" "$TMP/_ask/skills/manifest.yaml"
echo 'PASS: reserved preparation names rejected before any installer runs'
