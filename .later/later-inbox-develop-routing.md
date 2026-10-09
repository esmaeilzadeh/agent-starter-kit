# Enforce develop as the shared later inbox across work branches

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `structured-agentic-environment` side conversation (2026-10-09)
- **Start later:** new session, `./ask start-work later-inbox-develop-routing`
- **First stage:** 01 Grill; destination is clear, safe publication mechanics need confirmation

## Why

The human previously requested that newly parked tasks be added to develop instead of the active work branch. This rule already exists in _ask/policies/git-flow.md, _ask/policies/worktree.md, and .later/README.md, but the entry instruction only says to park a card in .later/<slug>.md. The status implementation reads .later from the current checkout. In this session, develop contained phase-coordinator-models.md while the active agent/structured-agentic-environment checkout did not, making a parked item disappear from the normal inbox view. No dedicated later-add command currently enforces the publication rule.

## Proposed What (unapproved)

- Route every newly parked later card to develop, or the configured integration branch, regardless of the current workstream branch. Keep live engineering work on its dedicated agent/<work-id> branch.
- Make the entry instruction and later-add/publication command resolve the same integration-branch policy. Refuse an accidental card commit on a work branch with an actionable explanation.
- Read the durable inbox from the integration ref when listing later work, including while an agent branch is checked out. Identify unpublished local cards separately so existing in-progress additions are not hidden.
- Preserve the current workstream and its uncommitted files when publishing cards. Respect the dirty-worktree gate; do not silently stash, reset, overwrite, or merge unrelated implementation changes.
- Make repeated additions idempotent and expose commit/push failures. Push when explicitly requested or covered by existing authorization; otherwise report the local publication state.
- Verify adding and listing from both develop and a work branch, duplicate additions, a dirty checkout, and failed publication. Preserve existing cards and show phase-coordinator-models from develop on a work-branch inbox view.

## Note

This is a regression/enforcement follow-up to later-inbox-script.md and later-inbox-tracker-sync.md, not a replacement for those proposals. Historical cards still describe a gitignored local inbox, although current policy requires durable cards on develop; reconcile those descriptions when implementing the shared workflow. The observed listing gap is confirmed; an incorrect new-card commit was not reproduced in this session. The human explicitly requested this additional record if the rule was absent or buggy.
