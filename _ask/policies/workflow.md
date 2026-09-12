# Workflow guidance (not a lock)

The kit’s default path is Explore (if foggy) → Grill → Spec → Challenge → Plan → Implement → Review → Refactor → Verify → Accept.

That path is **guidance**. It must feel like a guide, not a lock. The human may leave it at any time. The agent must not trap them in stage ceremony.

## Default

Unless the human chooses otherwise, the agent:

1. Recommends and performs the **next kit stage** for the active work-id.
2. Auto-continues after a stage’s exit criteria are met, stopping only for human judgment (Grill decisions, spec acceptance, Accept) or escalation.
3. Runs `./ask check-workstream <work-id>` before Implement as the **default** precondition check.

## Own way (allowed)

The human may skip or reorder stages (including intent → implementation).

When that happens the agent **must**:

1. **Warn** — name the skipped stage(s), what the kit would have produced, and the risk (unowned What/Why, no acceptance criteria, unverifiable result).
2. **Ask once** whether to stay on the kit path or continue their way.
3. **Follow** their choice. Do not block, nag every turn, or invent extra gates.
4. Note the deviation in `work/<work-id>/intent.md` (Human decisions) or the next commit message so `./ask status` and later stages can rejoin.

Do **not** silently skip. Do **not** refuse the labor solely because a prior artifact is missing.

## Still hard (safety, not workflow theater)

These remain refusals, not warnings:

- Dirty worktree without grilling (`_ask/policies/worktree.md`)
- Silent stash/reset
- Claiming verify/accept without running checks or recording a commit SHA
- Changing What/Why or acceptance criteria without Spec Change

## Status

`./ask status` may flag `code-without-plan` (or similar) as a **warning** on a live branch: labor outside `work/<id>/` and `specs/` while stage is still `seeded` / `explored` / `intent`. That is a signal, not a failure.
