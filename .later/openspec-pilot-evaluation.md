# OpenSpec pilot evaluation (adopt / revise / abandon)

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `openspec-governance-integration`
- **Tracker:** https://github.com/esmaeilzadeh/agent-starter-kit/issues/48
- **Start later:** new session, `./ask start-work openspec-pilot-evaluation`
- **First stage:** 01 Grill if dest stays ownable; 00 only if the representative changes are still unnamed

## Why

`openspec-governance-integration` Accepts on machinery plus a recorded
baseline. The spec's two-or-three-change comparison (time, duplication,
missed requirements, semantic-change handling, command-surface adherence,
review/verification quality, merge conflicts, readability) is a separate
workstream.

## Proposed What (unapproved)

Run two or three serialized marked-pilot changes, compare against
`work/openspec-governance-integration/baseline.md`, record adopt, revise, or
abandon. Name the representative changes when that workstream starts. This
dogfood work-id is not one of those evaluation changes unless that workstream
says so.

## Note

Durable repository card mirrored by the GitHub issue above. Do not start
`agent/openspec-pilot-evaluation` while
`agent/openspec-governance-integration` is live and touching `openspec/` or
shared gates.
