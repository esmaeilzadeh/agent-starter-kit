# Specification Change Proposal

## Current specification

`specs/proposals/inner-loop-hardening.md`

## Proposed change

Applied in the proposal file. Human confirmed 2026-09-20.

**Inner-loop writers are sequential.** Implement, review, and debug remain
separate spawned contexts (cc-sdd role trio). Only one task may **commit** at
a time. `(P)` / disjoint `owned_paths` are planning notes, not concurrent Git.

**Steering-shaped `owned_paths`:** Plan declares seam/module globs, not a
per-file list. Harness expands globs at spawn. New files matching the glob are
allowed. Steering-style project memory; not a file census.

**Three layers:**

- Readable: whole repo.
- Writable uncommitted: scratch (caches, tmp, coverage; gitignored). Never
  integrated.
- Committable: expanded `owned_paths` only.

Test **source** is in the glob and is committed. Production edits kept off the
branch are forbidden.

**Harness (tested, not markdown-only):** Git stage/commit reject paths outside
the glob. Reviewer runs `git diff --name-only` vs the glob. Filesystem does
**not** lock the whole tree to `owned_paths` (that blocks TDD runners).

**Boundary REJECTED taxonomy (stops retry loops):**

- Extra files not required by the task → revert those paths; counts as one
  remediation round.
- Files required by the task but outside the glob → **BLOCKED**; do not retry.
  Escalate or add a dependent task that owns that glob.

**Retry cap:** REJECTED rounds 1–2 → implementer with typed REMEDIATION.
Round 3 → debug in a **fresh** context. Max 2 debug rounds. Then `_Blocked` /
escalate. No further spawn.

**Integrate:** commits land on `agent/<work-id>` (fast-forward if a task branch
exists). Cherry-pick, rebase onto coordinator, and merge-conflict recovery are
forbidden. No second writer means no merge disaster path.

Plus Challenge round-1 encodings still in the spec: dirty-tree, resume/CAS,
OpenCode file-shape + Plan-recorded docs, human-only provisioning, kit-repo
E2E `not_applicable`, overlap without `depends_on` → `path_conflict`,
`context-audit.md`, `worktree.md` in scope.

## Why the change is needed

Concurrent Git writers plus cherry-pick would break branch semantics or invent
conflict handling. A write-allowlist equal to `owned_paths` blocks tests.
Per-file census is the cc-sdd steering anti-pattern. Untyped REJECTED loops.

## Impacted artifacts

`specs/proposals/inner-loop-hardening.md` (this commit). Later Plan:
`worktree.md`, verify scripts, templates, harness tests.

## Impacted workstreams

`inner-loop-hardening` only.

## Migration / transition notes

None until Implement.

## Acceptance criteria for the change

Met when the proposal spec contains the sequential-writer, glob, three-layer,
commit-allowlist, REJECTED taxonomy, 2+2 cap, and no-cherry-pick rules.

## Decision

**Accepted.** Human: confirm (2026-09-20).
