# Intent: SHA-bound NN experiment demo

## What

1. Replace the facilitator demo vehicle (`kit-status`) with a tiny moons MLP trainer plus a Streamlit run viewer.
2. Each experiment lives under `results/<run-id>/` with `config.yaml`. Code and/or that config are committed; the result binds to that SHA.
3. Add `./ask record-run` (ILP-shaped manifest + summary + `RUN_REGISTRY.md`). `record-result` still Accepts the workstream.

## Why

A kit demo should teach citable experiments (path + SHA + metric), not only a workstream pass/fail.

## Non-goals

Porting Popper / 1d-ARC. PyTorch. MNIST download. Changing dirty-tree or Accept policy. Phase 3 / CI farm.

## Known assumptions

- Dataset: sklearn `make_moons`. Framework: numpy + sklearn MLP.
- Config: YAML in the run directory.
- `record-run` refuses a dirty tree; `--commit-sha` must be `HEAD`.
- `developing-with-streamlit` pinned at `streamlit/agent-skills#v1`.

## Open questions

None.

## Human decisions

Explore Q1–Q8 as recorded in `work/demo-nn-train/explore-map.md`. All remaining recs accepted.
