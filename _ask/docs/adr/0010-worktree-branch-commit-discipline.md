# Worktree, branch, and stepwise-commit discipline

Agents must not start labor on a dirty worktree (`./ask check-clean`). When dirty, they grill the human about uncommitted/untracked files and must not silently stash or reset. Each plan runs on its own `agent/<work-id>` branch (`./ask start-work`); commits happen after each meaningful step (not only at plan end). Related branches that would conflict on shared files must be serialized, not parallelized. Policy: `_ask/policies/worktree.md`.
