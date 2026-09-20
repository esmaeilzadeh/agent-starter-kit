# /00-explore clones the repo multiple times

- **Status:** parked (not live; no `agent/*`)
- **Found during:** free chat after `/00-explore` (NN demo); diagnosis 2026-09-12
- **Tracker:** https://github.com/esmaeilzadeh/agent-starter-kit/issues/43
- **Start later:** new session, `./ask start-work explore-clone-fanout`
- **First stage:** 01 Grill if dest stays ownable; 00 only if naming/UX is still foggy

## Why

`/00-explore` is a kit protocol stage. It does not clone this repo. Extra clones
come from Cursor treating “explore” as its built-in Explore subagent, dual
command+skill projection, repeated skill-source fetches, and background agents.

## Proposed What (unapproved)

- Rename command/skill away from `explore` (for example `/00-chart`).
- Tell 00 not to launch runtime Explore/background agents unless requested.
- Fetch each pinned skill source once during `./ask prepare`.

## Note

Durable repository card mirrored by the GitHub issue above.
