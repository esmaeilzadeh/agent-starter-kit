# Plan

## Specification

This is a focused bug fix. The frozen dogfood checkout must remain at its recorded pin across sessions, and another clone must be able to recreate it from the tracked pin record.

## Approach

Move the clean detached worktree from `/tmp` to the persistent sibling path. Record the pin and exact `git worktree add --detach` recovery command in `frozen-copy.md`.

## Work breakdown

Break implementation into reviewable tasks before coding. Use one row per
cohesive outcome; one task is valid when the work is a single deliverable, with
the reason recorded. Keep IDs aligned with `inner-loop/tasks.yaml` and
`test-plan.json`'s `task_scopes`.

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| DDP-01 | Relocate the pinned worktree and record its durable location and recovery command | — | `work/dogfood-directory-persistence/**` | — | Verify `git worktree list`, exact `HEAD`, clean checkout, and recovery command |

Assign every planned test case to its responsible task. Give tasks without an
executable test a specific verification rationale. Create
`work/<work-id>/inner-loop/tasks.yaml` from `_ask/templates/inner-loop-tasks.yaml`.

## Risks

The sibling directory is local and is not included in Git clones. The committed pin record provides the exact command to recreate it.

## Verification approach

Confirm the temporary path is gone, the persistent sibling is registered and clean at the unchanged pin, and the tracked recovery command reproduces the registration if needed.

## Out of scope for this plan

Changing the pinned AskIt revision or automating dogfood worktree setup.

## E2E

Not applicable: no product runtime behavior or user-facing E2E journey changes.
