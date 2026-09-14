# Intent: SHA-bound moons MLP demo (OpenSpec dogfood)

Engine: openspec

Risk: LOW

## What

Add run `moons-narrow` (`hidden_layer_sizes: [8]`) and run `moons-wide`
(`hidden_layer_sizes: [32]`). Each run's `config.yaml` lives in
`results/<run-id>/`. Commit that config (and any trainer edit) before
training. Record each metric with `./ask record-run` bound to HEAD.

This workstream is a marked OpenSpec pilot of the kit moons demo Path A.
It exercises the OpenSpec engine after `openspec-governance-integration`.

## Why

A score without path + SHA is not citable. The same Path A must still
complete under the OpenSpec redesign: one work-id for branch, change, and
kit evidence; kit commands remain the surface; `record-run` / verify /
Accept / openspec-archive still close the loop.

## Non-goals

- PyTorch, MNIST, changing kit Accept policy.
- Merging OpenSpec machinery onto `main`.
- The later two-or-three-pilot adopt / revise / abandon evaluation.
- Changing trainer or viewer code unless a bug blocks Path A.

## Known assumptions

- Explore skipped: destination already clear.
- Branch created from `agent/openspec-governance-integration` HEAD. `./ask
  start-work` forks from `main` and would omit unmerged OpenSpec machinery.
- Existing vehicle: `scripts/train_moons.py`, `scripts/view_runs.py`,
  `./ask record-run`. Dataset: sklearn `make_moons`.
- `record-run` refuses a dirty tree; `--commit-sha` must be HEAD.
- `developing-with-streamlit` is already pinned.

## Open questions

None. Path A seed from `_ask/docs/demo/end-to-end-plan.md` is the What.

## Human decisions

Walk through moons Path A on the current OpenSpec redesign. Mark as
`Engine: openspec` so gates, pointer plan, and openspec-archive run.
