# Enforce develop as the shared later inbox across work branches

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `structured-agentic-environment` side conversation (2026-10-09)
- **Start later:** new session, `./ask start-work later-inbox-develop-routing`
- **First stage:** 01 Grill; destination is clear, safe publication mechanics need confirmation

## Why

The human requested that parked tasks live on develop instead of the active work branch. The status command previously read `.later/` from the current checkout, so a committed card on develop disappeared from the inbox view on an agent branch. This listing defect is fixed by the `later-inbox-develop-routing` workstream; the missing dedicated later-add command and publication safeguards remain separate parked work.

## Proposed What (unapproved)

- When the human asks to add something to the later inbox, agents must invoke the canonical Ask command (proposed `./ask later add`) instead of manually writing cards or assembling Git operations. That command owns card creation and publication on develop, including commit and push when authorized.
- Route every newly parked later card to develop, or the configured integration branch, regardless of the current workstream branch. Keep live engineering work on its dedicated agent/<work-id> branch.
- Make the entry instruction and later-add/publication command resolve the same integration-branch policy. Refuse an accidental card commit on a work branch with an actionable explanation.
- Read the durable inbox from the integration ref when listing later work, including while an agent branch is checked out. **Implemented:** committed cards are read from local `develop` or `origin/develop`. Still to decide/implement: how to show unpublished local cards separately.
- Preserve the current workstream and its uncommitted files when publishing cards. Respect the dirty-worktree gate; do not silently stash, reset, overwrite, or merge unrelated implementation changes.
- Make repeated additions idempotent and expose commit/push failures. Push when explicitly requested or covered by existing authorization; otherwise report the local publication state.
- Verify the add/list command on both develop and a work branch, duplicate additions, a dirty checkout, and failed publication. Preserve existing cards and show phase-coordinator-models from develop on a work-branch inbox view (the listing portion is covered by the completed regression test).

## Note

This is a regression/enforcement follow-up to later-inbox-script.md and later-inbox-tracker-sync.md, not a replacement for those proposals. Historical cards still describe a gitignored local inbox, although current policy requires durable cards on develop; reconcile those descriptions when implementing the shared workflow. The committed-card listing gap is fixed; incorrect new-card publication remains unreproduced. The human explicitly requested this additional record if the rule was absent or buggy.
