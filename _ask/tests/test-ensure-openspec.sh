#!/usr/bin/env bash
# ensure-openspec.sh: pin validation, skip paths, stub npm, timeout, HOME isolation.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HELPER="$ROOT/_ask/scripts/ensure-openspec.sh"
chmod +x "$HELPER"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HOME="$TMP/home"
export HOME
mkdir -p "$HOME"

# python3 lives here; node/npm on this machine do not.
BASE_PATH="/usr/bin:/bin"

write_pin() {
  cat > "$TMP/pin.yaml" <<EOF
package: "@fission-ai/openspec"
revision: "${1:-1.13.0}"
schema: spec-driven
profile: core
EOF
}

run_helper() {
  ASK_OPENSPEC_PIN="$TMP/pin.yaml" ASK_OPENSPEC_NPM_TIMEOUT="${ASK_OPENSPEC_NPM_TIMEOUT:-5}" \
    "$HELPER" >"$TMP/out.txt" 2>"$TMP/err.txt"
}

# missing pin
set +e
ASK_OPENSPEC_PIN="$TMP/missing.yaml" "$HELPER" >"$TMP/out.txt" 2>"$TMP/err.txt"
code=$?
set -e
[[ "$code" -eq 2 ]]
grep -qi 'missing pin' "$TMP/err.txt"

# latest
write_pin latest
set +e
run_helper
code=$?
set -e
[[ "$code" -eq 2 ]]
grep -qi 'latest' "$TMP/err.txt"

# empty package
cat > "$TMP/pin.yaml" <<'YAML'
package: ""
revision: "1.13.0"
YAML
set +e
run_helper
code=$?
set -e
[[ "$code" -eq 2 ]]

# missing npm
write_pin 1.13.0
empty="$TMP/empty-path"
mkdir -p "$empty"
set +e
PATH="$empty:$BASE_PATH" run_helper
code=$?
set -e
[[ "$code" -eq 1 ]]
grep -q '@fission-ai/openspec' "$TMP/err.txt"
grep -q '1.13.0' "$TMP/err.txt"

# already-correct version skips npm
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/openspec" <<'BIN'
#!/usr/bin/env bash
echo 1.13.0
BIN
chmod +x "$HOME/.local/bin/openspec"
log="$TMP/npm.log"
cat > "$TMP/npm" <<EOF
#!/usr/bin/env bash
echo npm >> "$log"
exit 1
EOF
chmod +x "$TMP/npm"
: > "$log"
set +e
PATH="$TMP:$empty:$BASE_PATH" run_helper
code=$?
set -e
[[ "$code" -eq 0 ]]
grep -q 'matches 1.13.0' "$TMP/out.txt"
[[ ! -s "$log" ]]

# stub npm install + conflicting binary
cat > "$HOME/.local/bin/openspec" <<'BIN'
#!/usr/bin/env bash
echo 9.9.9
BIN
chmod +x "$HOME/.local/bin/openspec"
cat > "$TMP/npm" <<EOF
#!/usr/bin/env bash
echo "\$@" >> "$log"
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/openspec" <<'INNER'
#!/usr/bin/env bash
echo 1.13.0
INNER
chmod +x "$HOME/.local/bin/openspec"
exit 0
EOF
chmod +x "$TMP/npm"
: > "$log"
# node stub
cat > "$TMP/node" <<'EOF'
#!/usr/bin/env bash
exit 0
EOF
chmod +x "$TMP/node"
set +e
PATH="$TMP:$empty:$BASE_PATH" run_helper
code=$?
set -e
[[ "$code" -eq 0 ]]
grep -q -- '--prefix' "$log"
grep -q -- '--force' "$log"
grep -q '@fission-ai/openspec@1.13.0' "$log"
"$HOME/.local/bin/openspec" --version | grep -qx 1.13.0

# mismatch after install
cat > "$TMP/npm" <<EOF
#!/usr/bin/env bash
mkdir -p "$HOME/.local/bin"
cat > "$HOME/.local/bin/openspec" <<'INNER'
#!/usr/bin/env bash
echo 0.0.1
INNER
chmod +x "$HOME/.local/bin/openspec"
exit 0
EOF
chmod +x "$TMP/npm"
rm -f "$HOME/.local/bin/openspec"
set +e
PATH="$TMP:$empty:$BASE_PATH" run_helper
code=$?
set -e
[[ "$code" -eq 1 ]]
grep -qi 'mismatch' "$TMP/err.txt"

# unwritable prefix
write_pin 1.13.0
rm -rf "$HOME/.local"
mkdir -p "$HOME"
touch "$HOME/.local"
set +e
PATH="$TMP:$empty:$BASE_PATH" run_helper
code=$?
set -e
[[ "$code" -eq 1 ]]
grep -qi 'cannot write' "$TMP/err.txt"
rm -f "$HOME/.local"
mkdir -p "$HOME/.local/bin"

# timeout kill
cat > "$TMP/npm" <<'EOF'
#!/usr/bin/env bash
sleep 30
exit 0
EOF
chmod +x "$TMP/npm"
rm -f "$HOME/.local/bin/openspec"
set +e
ASK_OPENSPEC_NPM_TIMEOUT=1 PATH="$TMP:$empty:$BASE_PATH" ASK_OPENSPEC_PIN="$TMP/pin.yaml" \
  "$HELPER" >"$TMP/out.txt" 2>"$TMP/err.txt"
code=$?
set -e
[[ "$code" -eq 1 ]]
grep -qi 'timed out' "$TMP/err.txt"

# setup.sh wires the helper
grep -q 'ensure-openspec.sh' "$ROOT/_ask/scripts/setup.sh"

# overlay/install/self-install do not invoke the helper
! grep -q 'ensure-openspec' "$ROOT/_ask/scripts/install-kit.sh"
! grep -q 'ensure-openspec' "$ROOT/askit"

echo "PASS: ensure-openspec pin, skip, stub install, timeout, wiring"
