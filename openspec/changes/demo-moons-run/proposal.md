## Why

`openspec-governance-integration` Accepted on machinery plus a baseline.
Path A of the moons demo is the kit's documented end-to-end vehicle. This
change runs that vehicle as a marked OpenSpec pilot so the redesign is
exercised on a real work-id, not only unit stubs.

## What Changes

- Record two SHA-bound moons MLP runs: `moons-narrow` (hidden `[8]`) and
  `moons-wide` (hidden `[32]`).
- Each run's hyperparameters live in `results/<run-id>/config.yaml` and
  are committed before training.
- Each metric is recorded with `./ask record-run` bound to HEAD.
- Kit `plan.md` and optional `specs/` files for this work-id are pointers
  to this change directory.

## Capabilities

### New Capabilities

- `demo-moons-runs`: two named moons MLP runs cited in
  `results/RUN_REGISTRY.md` as path + git SHA + metric, with distinct
  HEAD SHAs for narrow vs wide.

### Modified Capabilities

## Impact

`results/moons-narrow/`, `results/moons-wide/`, `results/RUN_REGISTRY.md`.
Uses existing `scripts/train_moons.py`, `scripts/view_runs.py`, and
`./ask record-run` (contract already in `specs/current/demo-nn-train.md`
and `_ask/spec/04-scripts-and-git.md` §25). Does not redefine those
commands.

## Legacy source

Demo seed: `_ask/docs/demo/end-to-end-plan.md` Path A. Record-run
behavior is not copied here; this change owns only the two named runs.
