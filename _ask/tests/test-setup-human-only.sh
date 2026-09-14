#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ASK="$ROOT/ask"

"$ASK" setup --help | grep -q 'human-only'
"$ASK" setup --help | grep -q 'OpenSpec'
"$ASK" setup --help | grep -q 'skip'

before=""
[[ -f "$ROOT/.ask.env" ]] && before="$(wc -c < "$ROOT/.ask.env")"

npm_log="$(mktemp)"
npm_bin="$(mktemp -d)"
cat > "$npm_bin/npm" <<EOF
#!/usr/bin/env bash
echo invoked >> "$npm_log"
exit 0
EOF
chmod +x "$npm_bin/npm"

set +e
PATH="$npm_bin:$PATH" "$ASK" setup </dev/null >/tmp/ask-setup-notty.out 2>/tmp/ask-setup-notty.err
code=$?
set -e
[[ "$code" -ne 0 ]]
grep -q 'human-only' /tmp/ask-setup-notty.err
[[ ! -s "$npm_log" ]]
rm -f "$npm_log"
rm -rf "$npm_bin"

after=""
[[ -f "$ROOT/.ask.env" ]] && after="$(wc -c < "$ROOT/.ask.env")"
[[ "$before" == "$after" ]]

echo "PASS: setup --help works; non-TTY setup refuses and does not write .ask.env"
