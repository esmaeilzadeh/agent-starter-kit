#!/usr/bin/env bash
# Cursor session-start adapter for the shared project access check.
set -u
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
if output="$("$ROOT/ask" access-check 2>&1)"; then
  printf '%s\n' '{"additional_context":"Project access preflight passed. Continue with the user request."}'
else
  printf '%s\n' "$output" | python3 -c 'import json,sys; print(json.dumps({"additional_context":"STOP: project access preflight failed. Do not begin or resume project work until the user restores access.\n" + sys.stdin.read()}))'
fi
