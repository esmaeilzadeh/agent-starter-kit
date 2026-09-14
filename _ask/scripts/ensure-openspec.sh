#!/usr/bin/env bash
# Install or confirm the pinned OpenSpec CLI under $HOME/.local.
# Exit 0 success, 1 skip/warn, 2 bad pin. No TTY required.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PIN="${ASK_OPENSPEC_PIN:-$ROOT/_ask/openspec-pin.yaml}"
PREFIX="${HOME:?HOME is unset}/.local"
BIN="$PREFIX/bin/openspec"
NPM_TIMEOUT="${ASK_OPENSPEC_NPM_TIMEOUT:-120}"

warn() { echo "ensure-openspec: $*" >&2; }

pin_field() {
  local key="$1"
  PIN="$PIN" KEY="$key" python3 - <<'PY'
import os, re
path = os.environ["PIN"]
key = os.environ["KEY"]
try:
    text = open(path, encoding="utf-8").read()
except OSError:
    raise SystemExit(2)
for raw in text.splitlines():
    line = raw.split("#", 1)[0].strip()
    m = re.match(r"^([A-Za-z0-9_-]+):\s*(.+?)\s*$", line)
    if not m or m.group(1) != key:
        continue
    val = m.group(2).strip().strip('"').strip("'")
    if not val or val[0] in "[{|>&*!" or val.lower() in ("null", "~", "true", "false"):
        raise SystemExit(1)
    print(val)
    raise SystemExit(0)
raise SystemExit(1)
PY
}

if [[ ! -f "$PIN" ]]; then
  warn "missing pin file $PIN"
  exit 2
fi

set +e
package="$(pin_field package)"
pkg_code=$?
revision="$(pin_field revision)"
rev_code=$?
set -e
if [[ "$pkg_code" -ne 0 || "$rev_code" -ne 0 || -z "${package:-}" || -z "${revision:-}" ]]; then
  warn "pin missing non-empty scalar package or revision (${package:-unset}@${revision:-unset})"
  exit 2
fi
rev_lc="$(printf '%s' "$revision" | tr '[:upper:]' '[:lower:]')"
if [[ "$rev_lc" == "latest" ]]; then
  warn "pin revision must not be latest (${package}@${revision})"
  exit 2
fi

trimmed_version() {
  ASK_OPENSPEC_BIN="$BIN" ASK_OPENSPEC_NPM_TIMEOUT="$NPM_TIMEOUT" python3 - <<'PY'
import os, subprocess, sys
bin_path = os.environ["ASK_OPENSPEC_BIN"]
timeout = float(os.environ["ASK_OPENSPEC_NPM_TIMEOUT"])
if not os.path.isfile(bin_path) or not os.access(bin_path, os.X_OK):
    raise SystemExit(1)
try:
    proc = subprocess.run(
        [bin_path, "--version"],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
except subprocess.TimeoutExpired:
    raise SystemExit(1)
if proc.returncode != 0:
    raise SystemExit(1)
print((proc.stdout or "").strip())
PY
}

set +e
got="$(trimmed_version)"
got_code=$?
set -e
if [[ "$got_code" -eq 0 && "$got" == "$revision" ]]; then
  echo "ensure-openspec: $BIN matches $revision"
  exit 0
fi

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  warn "node/npm missing; skip install of ${package}@${revision}"
  exit 1
fi

if ! mkdir -p "$PREFIX/bin"; then
  warn "cannot write $PREFIX for ${package}@${revision}"
  exit 1
fi
if [[ -e "$BIN" || -L "$BIN" ]]; then
  if ! rm -f "$BIN"; then
    warn "cannot replace $BIN for ${package}@${revision}"
    exit 1
  fi
fi

run_npm() {
  ASK_OPENSPEC_NPM_TIMEOUT="$NPM_TIMEOUT" python3 - "$1" "$2" "$PREFIX" <<'PY'
import os, signal, subprocess, sys
package, revision, prefix = sys.argv[1], sys.argv[2], sys.argv[3]
timeout = float(os.environ["ASK_OPENSPEC_NPM_TIMEOUT"])
cmd = ["npm", "install", "-g", "--prefix", prefix, "--force", f"{package}@{revision}"]
proc = subprocess.Popen(cmd, start_new_session=True)
try:
    rc = proc.wait(timeout=timeout)
except subprocess.TimeoutExpired:
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except OSError:
        proc.kill()
    proc.wait()
    raise SystemExit(124)
raise SystemExit(rc or 0)
PY
}

set +e
run_npm "$package" "$revision"
npm_code=$?
set -e
if [[ "$npm_code" -eq 124 ]]; then
  warn "npm install timed out after ${NPM_TIMEOUT}s for ${package}@${revision}"
  exit 1
fi
if [[ "$npm_code" -ne 0 ]]; then
  warn "npm install failed (exit ${npm_code}) for ${package}@${revision}"
  exit 1
fi

set +e
got="$(trimmed_version)"
got_code=$?
set -e
if [[ "$got_code" -ne 0 || "$got" != "$revision" ]]; then
  warn "post-install version mismatch for ${package}@${revision} (got ${got:-empty})"
  exit 1
fi
echo "ensure-openspec: installed $BIN $revision"
exit 0
