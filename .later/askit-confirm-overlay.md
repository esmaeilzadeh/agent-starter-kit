# Finish askit-confirm-overlay

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `openspec-governance-integration` (status sweep)
- **Start later:** new session, `./ask start-work askit-confirm-overlay`
- **First stage:** 01 Grill (dest clear; Explore skipped in intent)
- **Tracker:** [BAC-1101](https://jira.partcorp.ir/browse/BAC-1101)

## Why

`askit` in an ordinary git repo dumped commands and could overlay without asking.

## Proposed What (unapproved)

Confirm before overlay when git but not ask-based; refuse non-git; ask-based ≡ `./ask`. See `work/askit-confirm-overlay/intent.md` on `main`.

## Note

Reconcile with `askit-global-cli` before implementing both.
