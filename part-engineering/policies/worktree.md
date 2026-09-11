# Worktree, branch, and commit policy

## Never start dirty

Agents **must not** begin Explore, Grill, Plan, Implement, Review, Refactor, Verify, or Accept labor on an unclean Git working tree.

Before any of that work:

1. Run `part-engineering/scripts/check-clean-worktree.sh` (or equivalent `git status --porcelain` check).
2. If the tree is dirty, **stop**. Do not stash, reset, or absorb changes silently.
3. **Grill the human** on what to do with every uncommitted and untracked path. Present the file list and ask them to choose per item or batch, for example:
   - commit now (with an agreed message)
   - stash (explicit human request only)
   - discard (explicit human request only)
   - move to another branch / workstream
   - leave for a different work-id (then switch away without touching those files)
4. Resume only after `check-clean-worktree` exits 0.

## One plan → one branch

Every plan / workstream starts on its **own dedicated branch** (default: `agent/<work-id>` via `part-engineering/scripts/start-work.sh`). Do not implement a plan on `main`/`master` or on another workstream’s branch.

## Commit at each meaningful step

While executing a plan, **commit after each meaningful step** — do not wait until the whole plan is finished.

Meaningful steps include (non-exhaustive): scaffold landed, module split complete, policy/script added, stage contract added, binding synced, verification green for a slice, ticket closed with evidence.

Commits must leave the tree attributable and recoverable. Prefer small, intentional commits over one end-of-plan dump.

## No concurrent conflicting workstreams

Do **not** run multiple related workstreams or branches **in parallel** when they will modify overlapping / common files and are likely to conflict (same protocol paths, same modules, shared scripts, generated `.cursor` projections, etc.).

Serialize such work: finish or park one branch (merged, closed, or explicitly set aside with a clean handoff) before starting the next that touches the same surfaces.

Unrelated workstreams that touch disjoint paths may proceed in parallel when the human explicitly accepts that split.
