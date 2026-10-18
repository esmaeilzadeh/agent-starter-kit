# Explore map: RWB-104 baseline test classification

## Handoff

The card's proposed defect is already resolved on `develop` before this workstream started. The amended task test plan classifies `RWB-HISTORICAL` as an inherited regression and maps it to the existing read-only cross-branch snapshot test. The `RWB-104` result retains exact-candidate final-green evidence for commit `757462690641c6f6f823a1f6aec81fb0f83007d9`, run `dd31eec442334299a1f652ac1dbc8b55`. No implementation change is required; close the stale card and preserve all original workstream evidence.

## Evidence inspected

- `work/revising-workbench/test-plan.json` maps `RWB-HISTORICAL` to `_ask.tests.test_engineering_workbench_sources.WorkbenchTests.test_cross_branch_snapshot_is_consistent_and_read_only` with `change_kind: regression`.
- `work/revising-workbench/inner-loop/results/RWB-104.json` records exact candidate and final-green run.
- `work/revising-workbench/inner-loop/evidence/RWB-104-review-7574626-red-refresh.md` records the accepted amended-plan red and final-green evidence.
- `work/revising-workbench/inner-loop/state.json` preserves the amendment rationale and prior evidence history.

## Decision

No source or accepted-plan edits. Remove the obsolete `.later/rwb104-baseline-test-classification.md` card after recording this audit on the fresh work branch.
