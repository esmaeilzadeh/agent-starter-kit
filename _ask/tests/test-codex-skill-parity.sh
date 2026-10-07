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
