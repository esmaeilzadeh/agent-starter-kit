#!/usr/bin/env bash
# Prepare pinned Community Skills from manifest.yaml into .agents/skills/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
MANIFEST="$(cd "$(dirname "$0")" && pwd)/manifest.yaml"
cd "$ROOT"

if [[ ! -f "$MANIFEST" ]]; then
  echo "prepare-skills: missing $MANIFEST" >&2
  exit 2
fi

python3 - <<'PY' "$MANIFEST"
import sys, re, subprocess, os, json
from pathlib import Path

manifest_path = Path(sys.argv[1])
text = manifest_path.read_text()
# Minimal YAML subset parser for our schema (avoid PyYAML dependency)
# Expect skills: then indented keys
entries = []
current = None
for line in text.splitlines():
    if line.strip().startswith('#') or not line.strip():
        continue
    m = re.match(r'^  ([A-Za-z0-9_-]+):\s*$', line)
    if m:
        if current:
            entries.append(current)
        current = {"id": m.group(1)}
        continue
    m = re.match(r'^    (source|revision|skill|role|required):\s*(.+?)\s*$', line)
    if m and current is not None:
        key, val = m.group(1), m.group(2).strip().strip('"').strip("'")
        if key == 'required':
            current[key] = val.lower() in ('true', 'yes', '1')
        else:
            current[key] = val
if current:
    entries.append(current)

if not entries:
    print('prepare-skills: no skills entries found', file=sys.stderr)
    sys.exit(2)

# Validate every destination before invoking an installer for any entry.
for e in entries:
    skill = e.get('skill') or e.get('id')
    if skill.startswith('kit-'):
        print(f"prepare-skills: reserved ASK skill namespace: {skill}", file=sys.stderr)
        sys.exit(1)

failed = False

def apply_tdd_override(skill):
    if skill != 'tdd':
        return
    start = '<!-- ASK TDD OVERRIDE START -->'
    end = '<!-- ASK TDD OVERRIDE END -->'
    override_path = Path('_ask/skills/tdd-override.md')
    if not override_path.is_file():
        raise RuntimeError(f'missing repository TDD override: {override_path}')
    body = override_path.read_text(encoding='utf-8').strip()
    block = f'{start}\n{body}\n{end}'
    paths = (Path('.agents/skills/tdd/SKILL.md'), Path('.cursor/skills/tdd/SKILL.md'))
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise RuntimeError('missing prepared TDD skill view(s): ' + ', '.join(missing))
    for path in paths:
        content = path.read_text(encoding='utf-8')
        starts, ends = content.count(start), content.count(end)
        if starts != ends or starts > 1:
            raise RuntimeError(f'malformed or duplicate TDD override markers in {path}')
        if starts:
            content = re.sub(re.escape(start) + r'.*?' + re.escape(end), '', content, count=1, flags=re.S).rstrip()
        updated = content.rstrip() + '\n\n' + block + '\n'
        if updated != path.read_text(encoding='utf-8'):
            path.write_text(updated, encoding='utf-8')

for e in entries:
    rev = e.get('revision', '')
    if not rev or rev.lower() == 'latest':
        print(f"prepare-skills: REFUSE skill={e.get('id')} revision missing or 'latest'", file=sys.stderr)
        failed = True
        continue
    source = e.get('source')
    skill = e.get('skill') or e.get('id')
    if not source:
        print(f"prepare-skills: missing source for {e.get('id')}", file=sys.stderr)
        failed = True
        continue
    coord = f"{source}#{rev}"
    cmd = ['npx', 'skills', 'add', coord, '--skill', skill, '--agent', 'cursor', '--yes']
    print('prepare-skills: ', ' '.join(cmd))
    # Dry capability: SKIP_INSTALL=1 only validates pins
    if os.environ.get('SKIP_INSTALL') == '1':
        continue
    r = subprocess.run(cmd)
    skill_md = Path('.agents/skills') / skill / 'SKILL.md'
    if r.returncode != 0:
        print(f"prepare-skills: installer failed for {skill} (exit {r.returncode})", file=sys.stderr)
        if e.get('required', False):
            failed = True
        continue
    if not skill_md.is_file():
        print(f"prepare-skills: missing required primary .agents skill output for {skill}", file=sys.stderr)
        if e.get('required', False):
            failed = True
        continue
    if skill == 'tdd' and not Path('.cursor/skills/tdd/SKILL.md').is_file():
        print('prepare-skills: missing required Cursor TDD skill output', file=sys.stderr)
        if e.get('required', False):
            failed = True
        continue
    # Red-stage candidate: exercise the test suite before applying the override.
    print(f"prepare-skills: ok {skill} @ {rev}")

if failed:
    sys.exit(1)
print('prepare-skills: summary complete')
PY
