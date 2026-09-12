# Workflow guidance (not a lock)

The kit’s default path is Explore (if foggy) → Grill → Spec → Challenge → Plan → Implement → Review → Refactor → Verify → Accept.

That path is **guidance**. It must not feel like a lock, and it must not feel like optional paperwork you can omit while still “on the kit.”

## On the path (default)

If the human is using the kit:

1. **Artifacts are not optional.** Each next stage stands on the previous document (handoff, intent, spec, plan, …). Skipping those files is meaningless — there is nothing to move forward on.
2. **Prepare, then continue.** The agent writes the artifact for the current stage and proceeds to the next. Auto-continue in the same conversation after exit criteria; stop for human judgment at the confirms below (and escalation).
3. **Skip = skip extra approvals, not documents.** After Grill recommendations, one explicit confirm — *“I approve these defaults are OK”* — covers later prepared artifacts (spec marked CURRENT unless they asked to stop, plan, review). Do not re-ask a bless on Plan / Review / Refactor.
4. **Second confirm: Accept.** Close the workstream with `10 Accept` (evidence + commit SHA).
5. **Missing artifacts but still on the path:** prepare them from the accepted defaults, confirm once if that confirm has not happened yet, then continue. Do not jump to implementation with empty `plan.md` / no spec.

`./ask check-workstream <work-id>` is the machine check that the **default path is complete**. Exit non-zero means “incomplete,” not “forbidden.” On-path response: prepare what is missing.

## Off the path (this session only)

Every new Cursor session starts **on-path**. There is no durable off-path flag in git.

`/off-path` (`.cursor/commands/off-path.md`, source `_ask/cursor-commands/off-path.md`) switches **only the current chat**. Warn once, then follow. Do not write `work/*/kit-path` or record off-path in `intent.md`.

A new chat is on-path again. Saying “skip the kit” / “just code” in an on-path session has the same session-only effect (warn once, follow) without needing the slash command.

## Still hard (safety, not ceremony)

- Dirty worktree without grilling (`_ask/policies/worktree.md`)
- Silent stash/reset
- Claiming verify/accept without running checks or recording a commit SHA
- Changing What/Why or acceptance criteria without Spec Change (or a new defaults confirm that owns that change)

## Status

`./ask status` may flag `code-without-plan` on a **live** branch that changed files outside `work/<id>/` and `specs/` while stage is still `seeded` / `explored` / `intent`. Signal that labor left the path without artifacts — not a failure by itself.

Parked later-tasks in `.later/` are not live and do not appear on this board.
