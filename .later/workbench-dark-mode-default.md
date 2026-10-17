# Make dark mode the workbench default

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `structured-agentic-environment` / WB-009 compatibility update
- **Requested:** 2026-10-10, “add dark mode to ui and make it default”
- **Start later:** after the active task finishes, explicitly select this inbox item
- **First stage:** 01 Grill; destination is clear

## Why

The user wants the Engineering Workbench to open in dark mode by default.

## Proposed What (requested, not started)

Set the workbench's native Streamlit theme to dark by default. Preserve readable
text, controls, source blocks, tables, status labels and visible keyboard focus.
Keep theme configuration scoped to `_ask/ui/.streamlit/config.toml`. Verify a
fresh browser session and document the result. Retain a usable light-mode choice
if supported by the installed Streamlit configuration.

## Note

The user instructed: finish the running task through commit before accepting
another; unrelated new orders belong in separate later inbox records on develop
unless the user explicitly tells the agent to stop the running task. This card
queues the request and does not add it to WB-009 or claim implementation.
