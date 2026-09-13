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

echo "PASS: setup --help works; non-TTY setup refuses and does not write .ask.env"
