#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ASK="$ROOT/ask"

"$ASK" setup --help | grep -q 'human-only'

before=""
[[ -f "$ROOT/.ask.env" ]] && before="$(wc -c < "$ROOT/.ask.env")"

set +e
"$ASK" setup </dev/null >/tmp/ask-setup-notty.out 2>/tmp/ask-setup-notty.err
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'human-only' /tmp/ask-setup-notty.err

after=""
[[ -f "$ROOT/.ask.env" ]] && after="$(wc -c < "$ROOT/.ask.env")"
[[ "$before" == "$after" ]]

# verify scaffold is the same human-only class
python3 "$ROOT/_ask/scripts/verify_scaffold.py" --help | grep -qi 'human-only'
set +e
python3 "$ROOT/_ask/scripts/verify_scaffold.py" --root "$ROOT" </dev/null >/tmp/ask-vscaf-notty.out 2>/tmp/ask-vscaf-notty.err
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'human-only' /tmp/ask-vscaf-notty.err

echo "PASS: setup --help works; non-TTY setup refuses and does not write .ask.env; verify scaffold refuses non-TTY"
