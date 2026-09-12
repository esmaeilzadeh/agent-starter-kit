# Review

## Scope

`specs/current/demo-nn-train.md` vs `record-run`, `scripts/train_moons.py`, `scripts/view_runs.py`, demo plan.

## Findings

None blocking. `record-run` refuses missing SHA, dirty tree, and SHA ≠ HEAD. Demo no longer uses `kit-status`. Streamlit viewer lists registry + per-run config. `developing-with-streamlit` is pinned at `v1`.

## Suggested fixes

None.

## Residual risks

Facilitators without sklearn cannot train; kit `./ask verify` still passes. Streamlit viewer needs `pip install -r scripts/requirements-demo.txt`.

## Review verdict

Pass. No refactor.
