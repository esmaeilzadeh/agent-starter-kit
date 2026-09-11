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

failed = False
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
    # also check nested paths
    if r.returncode != 0 or not skill_md.exists():
        # search
        matches = list(Path('.agents/skills').glob(f'**/SKILL.md')) if Path('.agents/skills').exists() else []
        ok = any(skill in str(p) for p in matches)
        if not ok:
            print(f"prepare-skills: failed to verify SKILL.md for {skill}", file=sys.stderr)
            if e.get('required', False):
                failed = True
            continue
    print(f"prepare-skills: ok {skill} @ {rev}")

if failed:
    sys.exit(1)
print('prepare-skills: summary complete')
PY
