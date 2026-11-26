# Intent: Keep the frozen dogfood checkout available across sessions

## What

Keep the frozen AskIt checkout at commit `0e303265ceae1fbcdc9b2261bd922b003ab68924` at the persistent sibling path `../ai-agent-start-kit-dogfood-0e303265`. Track the exact pin, path, and recreation command in this repository.

## Why

The prior location was under `/tmp`; it disappeared between sessions and had to be recreated before work could resume.

## Non-goals

- Do not commit the frozen worktree contents.
- Do not change or upgrade the pinned commit during this task.
- Do not add automatic cleanup or general worktree-management tooling.

## Known assumptions

- The source repository and frozen worktree share the same Git object database through `git worktree`.
- A different checkout can recreate the sibling worktree from the recorded commit.

## Open questions

None.

## Human decisions

- The user authorized fixing the missing dogfood directory after the CWH work.

## E2E

Applicability: `not_applicable`

Reason: this is a local workflow-continuity issue; verify the registered worktree path, exact commit, and documented recreation command directly.

