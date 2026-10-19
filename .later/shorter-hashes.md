# Use shorter hashes to reduce token usage

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `refactor-inner-loop`
- **Start later:** new session, `./ask start-work <new-work-id>`
- **First stage:** 01 Grill
- **Tags:** token-efficiency, git
- **Attribution:** human request
- **Affected responsibilities:** hash and commit identifier representation in prompts, artifacts, and CLI output
- **Publication status:** draft

## Why

Full hashes consume many tokens in agent-facing context. Determine where shorter identifiers are safe and establish a consistent representation that retains enough information for reliable lookup and verification.

## Proposed What (unapproved)

Review hash usage across prompts, workstream artifacts, and command output. Adopt shorter hashes where unambiguous, while preserving full hashes where required for durable identity, audit evidence, or exact git operations.

## Note

This is a deferred efficiency improvement; it does not change the active workstream.
