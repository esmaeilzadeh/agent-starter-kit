# Specification: SHA-bound NN experiment demo

## Status

CURRENT

## Goal

Facilitators run a tiny moons MLP, change config and/or code via git commits, and cite each run as path + SHA + metric. The kit Path A/B demo uses this vehicle instead of `kit-status`.

## Non-goals

PyTorch, MNIST, ILP/Popper, durable off-path, CI farm.

## Behavior

### Run directory

`results/<run-id>/config.yaml` holds hyperparameters. Optional trainer code edits go in the same commit as that config (or a later commit before the run).

### `./ask record-run`

Kit command. Canonical contract: `_ask/spec/04-scripts-and-git.md` §22.9 and §25.1.

This demo uses that command. It does not redefine it.

### Trainer and viewer

- `scripts/train_moons.py --run-id <id>` reads that run’s YAML, trains an sklearn MLP on `make_moons`, writes accuracy into the run dir (does not record SHA itself).
- `scripts/view_runs.py` is a Streamlit app that lists registry rows (run-id, metric, SHA, config).

### Demo doc

`_ask/docs/demo/end-to-end-plan.md` Path A/B uses this vehicle. README/AGENTS keep pointing at the demo.

## Acceptance criteria

- `./ask record-run` refuses missing SHA, dirty tree, and SHA ≠ HEAD.
- A recorded run has `config.yaml`, `run_manifest.json`, `summary.json`, and a registry row with path + SHA + metric.
- Trainer and Streamlit viewer exist; demo doc no longer uses `kit-status` as the vehicle.
- `./ask verify` passes without requiring sklearn/streamlit in the default kit test set.

## Source intent

`work/demo-nn-train/intent.md`
