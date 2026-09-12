# Intent: ask status across workstream branches

## What

Add `./ask status` that lists live kit workstreams from `agent/*` branches (no checkout) and infers each plan’s furthest artifact state. Optionally show archived `work/*` on the default branch that no longer have an `agent/*` branch.

## Why

`work/<id>/` is branch-local, so a checkout cannot be a global board. Status must be computed from refs, not a committed INDEX.

## Non-goals

Writing `work/INDEX.md`. External trackers. Checking out branches.

## Human decisions

- Live inventory = unmerged local `agent/*`
- Archive = `work/*` on default with no unmerged `agent/*`
- Kit path is the **default**, not a lock: humans may leave the path; the agent must **warn** (what was skipped, risk, how to rejoin) and then follow. Do not refuse Implement solely for missing spec/plan.
