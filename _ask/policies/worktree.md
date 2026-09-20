# Worktree, branch, and commit policy

## Never start dirty

Agents **must not** begin Explore, Grill, Plan, Implement, Review, Refactor, Verify, or Accept labor on an unclean Git working tree.

Before any of that work:

1. Run `./ask check-clean` (or equivalent `git status --porcelain` check).
2. If the tree is dirty, **stop**. Do not stash, reset, or absorb changes silently.
3. **Grill the human** on what to do with every uncommitted and untracked path. Present the file list and ask them to choose per item or batch, for example:
   - commit now (with an agreed message)
   - stash (explicit human request only)
   - discard (explicit human request only)
   - move to another branch / workstream
   - leave for a different work-id (then switch away without touching those files)
4. Resume only after `./ask check-clean` exits 0.

## One plan → one branch

Every plan / workstream starts on its **own dedicated branch** (default: `agent/<work-id>` via `./ask start-work <work-id>`). Do not implement a plan on `main`/`master` or on another workstream’s branch.

That dedicated branch is the **safety boundary**: stepwise commits land on the workstream branch, not on `main`/`master`, so they do not put the default branch at risk.

## Commit at each meaningful step (hard)

While executing a plan on `agent/<work-id>`, agents **must commit after each meaningful step**.

**Do not wait** for the human to say “commit,” “please commit,” or similar. Waiting for permission to commit on the workstream branch is a **policy violation**.

This kit rule **overrides** any global agent/Cursor habit or user-level instruction that says “only commit when asked,” for as long as labor proceeds under this policy on a dedicated workstream branch. (Pushing, force-push, amend-of-pushed-commits, and merges to `main`/`master` still require explicit human direction.)

Meaningful steps include (non-exhaustive): scaffold landed, module split complete, policy/script added, stage contract added, binding synced, verification green for a slice, ticket closed with evidence.

Commits must leave the tree attributable and recoverable. Prefer small, intentional commits over one end-of-plan dump.

## No concurrent conflicting workstreams

Do **not** run multiple related workstreams or branches **in parallel** when they will modify overlapping / common files and are likely to conflict (same protocol paths, same modules, shared scripts, generated `.cursor` projections, etc.).

Serialize such work: finish or park one branch (merged, closed, or explicitly set aside with a clean handoff) before starting the next that touches the same surfaces.

Unrelated workstreams that touch disjoint paths may proceed in parallel when the human explicitly accepts that split.

## Inner-loop writers (in-workstream)

Default checkout is the coordinator worktree `agent/<work-id>`.

A Plan may add an optional task worktree/branch `agent/<work-id>/task/<id>`
for an isolated writer. Branch roles: `_ask/policies/git-flow.md`.

**One writer.** At most one task may have unintegrated commits. The runner
starts the next ready task only after integrate.

**Integrate.** Fast-forward only onto the coordinator: the task branch is a
descendant of `coordinator_sha`. Cherry-pick and rebase onto the coordinator
are forbidden.

**Spawn.** Optional task worktree spawn is runner-owned and empty of
uncommitted files. That spawn is not a human dirty-tree grill.

Inner-loop task branches stay inside this workstream. Cross-workstream overlap
stays under **No concurrent conflicting workstreams** above.

## Inventory (not the checkout)

`work/<work-id>/` is committed on `agent/<work-id>`, so artifact state is **branch-local**. Do not use the current working tree as the workstream inventory.

- **Live:** `./ask status` reads local `agent/*` that are **not** fully merged into the default branch (no checkout).
- **Archive:** `work/*` on `main`/`master` once that work-id has no unmerged `agent/*` (leftover merged branches do not stay live).
- **Later:** parked `.later/*.md` on this checkout (not live).

Do not write a committed `work/INDEX.md` — it would split the same way.
