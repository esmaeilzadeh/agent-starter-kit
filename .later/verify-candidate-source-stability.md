# Diagnose Verify's isolated candidate source stability failure

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `structured-agentic-environment` / WB-009 compatibility update
- **Start later:** explicitly select this inbox item after the active task finishes
- **First stage:** 00 Explore; cause is not established

## Why

`./ask verify` at candidate `f76170981496d14d7d1512705e1f0d61aa8000ea`
reported all 37 static checks passing, then rejected the isolated checkout with
`candidate source/CheckPlan changed during verification`. The coordinator checkout
remained clean at the same HEAD. This failure must not be reported as a pass.

## Proposed What (unapproved)

Reproduce the failure and identify which check mutates tracked candidate source.
Inspect differences before isolated-worktree cleanup. Fix the actual cause while
preserving candidate immutability and the source-stability guard.

## Note

One lead, not a confirmed cause: running `./ask sync` during this session changed
four generated `.codex/agents/kit-0*.toml` model/effort settings to match current
bindings. Those changes were reverted before this candidate was tested. A parity
check that regenerates those files may therefore dirty the isolated checkout.
The static receipt and test run are retained in the workstream traceability output.
