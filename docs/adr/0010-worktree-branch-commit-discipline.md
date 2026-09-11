# Worktree, branch, and stepwise-commit discipline

Agents must not start labor on a dirty worktree. When dirty, they grill the human about uncommitted/untracked files and must not silently stash or reset. Each plan runs on its own `agent/<work-id>` branch; commits happen after each meaningful step (not only at plan end). Related branches that would conflict on shared files must be serialized, not parallelized. Policy: `part-engineering/policies/worktree.md`.
