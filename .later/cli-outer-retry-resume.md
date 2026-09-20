# Cursor Agent CLI: outer retry + resume until the run finishes

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `inner-loop-hardening` (off-path chat, 2026-09-20)
- **Start later:** new session, `./ask start-work cli-outer-retry-resume`
- **First stage:** 01 Grill (dest is ownable: headless wrapper around `agent -p` + `--resume`). Skip 00 unless Grill opens “also wrap the interactive TUI / ACP / SDK.”

## Why

Cursor IDE and CLI do not expose a setting for inner reconnect budget (retry count, backoff, how long to wait before the turn ends). Interactive CLI (`agent` with a TTY) has no `result` event and no reliable exit code, so a human must resubmit or run `agent --continue`. Unattended kit runs (long Implement/Verify, overnight jobs) need the process to keep going after `api2.cursor.sh` / agent streaming drops.

Headless print mode is the wrap surface: non-zero exit on failure, NDJSON `result` on success, `--resume <chatId>` continues the same session.

## Proposed What (unapproved)

Ship a kit script (candidate: `./ask agent-run` or `_ask/scripts/agent-until-done.sh`) that:

1. Creates a chat id with `agent create-chat` and pins `--resume "$CHAT_ID"` on every attempt (do not use `--continue`; another chat can steal “latest”).
2. Runs **headless only**: `agent -p --trust --force --approve-mcps --workspace … --output-format stream-json`.
3. Treats **done** as exit 0 **and** a stream event `{ "type": "result", "subtype": "success" }`. Missing `result` is a drop even if the process exits 0.
4. Wraps each attempt in GNU `timeout` so hung `Reconnecting…` is killed (exit 124) and the outer loop can resume. Inner CLI reconnect is unchanged and not a v1 knob.
5. On drop: exponential backoff, then `--resume` with a **continue** prompt (“interrupted by a connection drop; finish from the last checkpoint”). Resend the original prompt only on attempt 1.
6. Stops without retry on auth / 401 / 403 / invalid API key (stderr match). Retries connection, unavailable, timeout, missing `result`.
7. Caps attempts. Prints `chat_id` on start so a human can `agent --resume` manually if the wrapper gives up.

Out of scope unless Grill expands it: wrapping the interactive TUI (`expect`/tmux), changing Cursor’s inner retry, ACP custom clients, SDK `max_retries` (HTTP only, not task resume).

## Note

Local inbox card (gitignored). Constraints from the 2026-09-20 investigation: `network.useHttp1ForAgent` is transport, not retry policy; `agent persist` survives terminal/SSH disconnect, not API drops; stream-json may omit `tool_call:completed` after reconnect (consumers should treat `connection:reconnecting` as cancelling in-flight tools). This machine’s CLI at discovery: `2026.09.10-fd3934a` (`agent about` reported `2026.09.18-9a7762b` available). Grill must lock dispatcher name, timeout/attempt defaults, and whether this is kit-owned or a documented recipe only.
