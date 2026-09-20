# Kit Protocol: 06 Implement

Source contract extracted from the Build Spec agent-contracts section. Portable SoT for this stage.

Requires: clean tree, dedicated branch, accepted spec, plan. Work under `work/<work-id>/`.

## 15.6 06 Implement Agent

Purpose:

```text
Perform delegated implementation labor.
```

Default preconditions (`./ask check-workstream`; **guidance**, not a lock — `_ask/policies/workflow.md`):

```text
clean working tree          ← still hard (safety)
dedicated branch
accepted spec               ← on-path: prepare from defaults if missing
active plan                 ← on-path: prepare from defaults if missing
no unrelated uncommitted changes
```

Default branch convention:

```text
agent/<work-id>
```

Must not:

```text
modify unrelated work
rewrite acceptance criteria to make tests pass
bypass policy
perform forbidden high-risk actions
continue through a mandatory escalation gate
```

At meaningful milestones, create commits so that important engineering states are recoverable and attributable. **Do not wait until the plan is finished** — commit after each meaningful step. **Do not wait for the human to ask** to commit on `agent/<work-id>`; the dedicated branch is the safety boundary (`_ask/policies/worktree.md`).

---

## Kit emphasis

- **Default:** run `./ask check-workstream <work-id>` before implementing. If it fails for missing spec/plan and they are still on the kit path, **prepare** those artifacts from accepted defaults (confirm “defaults OK” once if not already), then continue — do not implement on empty paper. Off-path (“just code”) only if they explicitly left: warn once and follow.
- If the tree is dirty: stop and grill the human per `_ask/policies/worktree.md` (never silent stash/reset). That refusal is safety, not workflow theater.
- One plan → one `agent/<work-id>` branch; do not start a second related branch that would conflict on shared files while this one is active.
- Commit after each meaningful step on the workstream branch **without waiting for the human to ask** (kit policy overrides global “only commit when asked”).

## Inner-loop

**Steering `owned_paths`:** seam/module globs in `work/<work-id>/inner-loop/tasks.yaml` (project memory, not a file census). Expand at spawn. Files created inside a glob are in scope.

When that TaskGraph file exists, run `./ask inner-loop run` (or `resume`). Scheduling, retry, CAS, and evidence fold live in `_ask/scripts/inner_loop/`. This contract does not copy the DAG.

One committing writer. Done when the current task is `integrated`, `blocked`, or `escalated`.

## E2E

Build the spec’s confirmed E2E journeys, or keep `not_applicable` plus reason. Missing E2E with no reason refuses Implement.
