# Review

## Model

- model: grok-4.6
- runtime: cursor
- parent_model: grok-4.6
- Note: same-family as Implement; walkthrough used cheap-pool default
  (Risk LOW) after the user asked to execute Path A. Child drafted in
  Ask mode; parent wrote this file from that draft.

## Scope

Independent inspect of `demo-moons-run` on `agent/demo-moons-run` against
canonical `openspec/changes/demo-moons-run/` (proposal, design, tasks,
delta `specs/demo-moons-runs/spec.md`). Intent:
`work/demo-moons-run/intent.md` (`Engine: openspec`, Risk LOW). Kit
pointers: `work/demo-moons-run/plan.md`, `specs/current/demo-moons-run.md`.

Parent re-measured after the child: tree clean at `ec3e85e`;
`view_runs._rows()` (Streamlit mocked) returns both runs; later
`./ask check-workstream` / `verify --work-id` run at 09.

## Findings

### Finding RV-001

Severity: LOW
Status: OPEN
08 disposition: ACCEPT WITH RATIONALE

Literal demo Path A A5 still trains then `record-run` with no commit of
`train_output.json`. Measured this walkthrough: after
`python3 scripts/train_moons.py --run-id moons-narrow`, porcelain showed
`?? results/moons-narrow/train_output.json` and `./ask record-run` exited
1 via `check-clean-worktree`. Implemented sequence commits that file
first. Design and spec-challenge already own this as a walkthrough
finding. Do not edit `_ask/docs/demo/end-to-end-plan.md` in this
workstream.

### Finding RV-002

Severity: LOW
Status: OPEN
08 disposition: FIX

Task 4.1 was still unchecked after both registry rows existed. 08 marks
it `[x]` after `view_runs._rows()` returned `moons-narrow` hidden `[8]`
and `moons-wide` hidden `[32]` with distinct `git_sha`.

## Suggested fixes

1. Tick task 4.1.
2. Leave Path A A5, `record-run` dirty refuse, and trainer cleanliness
   as-is for this work-id.

## Residual risks

- `--metric` is still any string; this walkthrough copied
  `train_output.json` `accuracy`.
- Bound SHA names the train-output commit, not the config-only commit.
  Spec allows HEAD.
- `origin/agent/demo-moons-run` is a stale unrelated ref. Local branch
  is from OpenSpec HEAD `518d771`.
- Close-out 4.2–4.4 remain for Verify / Accept / openspec-archive.

## Review verdict

ACCEPT WITH RATIONALE

Two SHA-bound registry rows, distinct SHAs, configs `[8]` / `[32]`,
record-run artifacts, pointer plan/specs, no OpenSpec-generated
`.cursor/commands`. 08 ticks 4.1 and accepts RV-001 without editing the
demo doc. No ESCALATE.
