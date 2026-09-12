# Plan

## Specification

`specs/current/demo-nn-train.md`

## Approach

Add kit `record-run` first (tests, no ML deps). Then ship the moons trainer, Streamlit viewer, and rewrite the facilitator demo.

## Work breakdown

1. `record-run.sh` + dispatcher help + refuse/write tests.
2. `results/` layout (README, empty registry) + `scripts/train_moons.py`.
3. Streamlit `scripts/view_runs.py`.
4. Rewrite `_ask/docs/demo/end-to-end-plan.md`; point README if needed.
5. Verify + Accept.

## Risks

Facilitators skip the commit-before-run step. Mitigation: `record-run` refuses dirty / SHA ≠ HEAD.

## Verification approach

- `_ask/tests/test-record-run-*.sh`
- `./ask verify` (kit tests; no sklearn required)
- Manual: two commits, two runs, registry shows two SHAs

## Out of scope for this plan

PyTorch. Merging other branches.
