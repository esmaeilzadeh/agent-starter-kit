# In-memory test-state adapters

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `inner-loop-hardening`
- **Tracker:** https://github.com/esmaeilzadeh/agent-starter-kit/issues/44
- **Start later:** new session, `./ask start-work in-memory-test-state-adapters`
- **First stage:** 00 Explore

## Why

In-memory databases can shorten local test loops, but a generic substitute can
hide production-engine behavior in constraints, transactions, migrations,
locking, collation, and vendor-specific data types.

## Proposed What (unapproved)

Add optional in-memory test-state adapters only where they pass the same
repository contract suite as the production database adapter. Keep integration
and E2E verification on an isolated ephemeral instance of the production
database engine.

## Note

The `inner-loop-hardening` workstream should define the adapter seam and test
tiers without implementing database-specific in-memory adapters.
