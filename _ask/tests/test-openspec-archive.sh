#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"
PAYLOADS="$(mktemp -d)"
trap 'rm -rf "$TMP" "$PAYLOADS"' EXIT
git init -q "$TMP"
cd "$TMP"
git config user.email t@e.com
git config user.name t
echo x > README.md
mkdir -p _ask/scripts work/demo openspec/changes/demo
cp "$ROOT/_ask/scripts/openspec-archive.sh" \
   "$ROOT/_ask/scripts/openspec_cli.py" \
   "$ROOT/_ask/scripts/check-clean-worktree.sh" \
   _ask/scripts/
cp "$ROOT/_ask/openspec-pin.yaml" _ask/openspec-pin.yaml
chmod +x _ask/scripts/*.sh _ask/scripts/*.py
printf 'schema: spec-driven\n' > openspec/changes/demo/.openspec.yaml
printf '# Intent\n\nEngine: openspec\n' > work/demo/intent.md
git add . && git commit -q -m init

set +e
./_ask/scripts/openspec-archive.sh demo >/tmp/oa-out.txt 2>/tmp/oa-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'no accepted commit SHA' /tmp/oa-err.txt

# direct archive without Accept: preflight fails
mkdir -p openspec/changes/archive/2026-09-14-demo
mv openspec/changes/demo/.openspec.yaml openspec/changes/archive/2026-09-14-demo/
rmdir openspec/changes/demo 2>/dev/null || rm -rf openspec/changes/demo
set +e
python3 _ask/scripts/openspec_cli.py --root "$TMP" preflight demo >/tmp/oa-out.txt 2>/tmp/oa-err.txt
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'no Accept SHA' /tmp/oa-err.txt

# restore active change; add Accept SHA; stub archive
mkdir -p openspec/changes/demo
printf 'schema: spec-driven\n' > openspec/changes/demo/.openspec.yaml
rm -rf openspec/changes/archive/2026-09-14-demo
cat > work/demo/acceptance.md <<'EOF'
# Acceptance

## Accepted commit SHA

abcdef1234567
EOF
cat > _ask/scripts/openspec-stub.sh <<'STUB'
#!/usr/bin/env bash
echo "$@" >> "${STUB_LOG}"
case "${1:-}" in
  --version) echo 1.13.0; exit 0 ;;
  archive) echo '{"archivedAs":"2026-09-14-demo","root":{"path":"/tmp","source":"nearest"}}'; exit 0 ;;
  *) exit 2 ;;
esac
STUB
chmod +x _ask/scripts/openspec-stub.sh
export OPENSPEC_BIN="$TMP/_ask/scripts/openspec-stub.sh"
export STUB_LOG="$PAYLOADS/stub.log"
: > "$STUB_LOG"
./_ask/scripts/openspec-archive.sh demo >/tmp/oa-out.txt
grep -q 'archive demo -y --json' "$STUB_LOG"
grep -q 'archived demo' /tmp/oa-out.txt

echo "PASS: openspec-archive refuses without Accept SHA; detects direct archive; archives after Accept"
