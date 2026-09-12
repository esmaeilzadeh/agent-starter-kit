#!/usr/bin/env bash
# Smoke: explore-map handoff gate concept + verify prints SHA
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# Fresh repo with kit overlay
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo x > README.md
git add . && git commit -q -m init
SKIP_INSTALL=1 "$ROOT/_ask/scripts/install-kit.sh" --skip-prepare "$TMP" >/dev/null
cd "$TMP"
# Need clean tree after install
git add -A && git commit -q -m "install kit" || true

# Seed accepted spec + start work
mkdir -p specs/current
cat > specs/current/demo.md <<'SPEC'
# Specification: demo
## Status
CURRENT
## Goal
smoke
## Acceptance criteria
- works
SPEC
git add specs && git commit -q -m "spec"

./_ask/scripts/start-work.sh smoke-demo
# 00 creates the map (start-work does not seed it)
cp _ask/templates/explore-map.md work/smoke-demo/explore-map.md
# Fill handoff
python3 - <<'PY'
from pathlib import Path
p=Path('work/smoke-demo/explore-map.md')
t=p.read_text()
t=t.replace('## Handoff to Intent\n\n','## Handoff to Intent\n\nDestination clear: smoke demo What/Why owned.\n\n',1)
# ensure non-empty handoff section content
p.write_text(t)
PY
# Check handoff non-empty
python3 - <<'PY'
from pathlib import Path
import re,sys
t=Path('work/smoke-demo/explore-map.md').read_text()
m=re.search(r'## Handoff to Intent\n+(.*?)(\n## |\Z)', t, re.S)
body=(m.group(1) if m else '').strip()
# strip HTML comments
body=re.sub(r'<!--.*?-->','',body,flags=re.S).strip()
if not body:
    sys.exit('empty handoff')
print('handoff ok')
PY

git add work && git commit -q -m "explore handoff" || true
./_ask/scripts/check-workstream.sh smoke-demo
# Do not invoke full verify.sh here — it would re-run this smoke test.
sha=$(git rev-parse HEAD)
test -n "$sha"
./_ask/scripts/record-result.sh --work-id smoke-demo --commit-sha "$sha" --result pass
test -f work/smoke-demo/result.json
echo "PASS: workstream smoke Explore handoff to verify SHA"
