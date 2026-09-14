## Context

See `proposal.md` Why. Trainer, viewer, and `./ask record-run` already
exist from `demo-nn-train`. This change only produces two committed
configs, two trains, and two registry rows on `agent/demo-moons-run`.

`./ask start-work` always creates `agent/<id>` from the default branch
(`main`). This branch was created from `agent/openspec-governance-integration`
HEAD so the unmerged OpenSpec engine is on the tree under test.

## Goals / Non-Goals

**Goals:**
- Two Path A runs with distinct HEAD SHAs in `results/RUN_REGISTRY.md`.
- Marked-pilot gates (`check-workstream`, `verify --work-id`,
  `openspec-archive` after Accept) succeed for `demo-moons-run`.

**Non-Goals:**
- Editing `train_moons.py` / `view_runs.py` unless Path A is blocked.
- Changing `record-run` refusals.
- Forking this work-id from `main`.

## Decisions

- Mark `Engine: openspec` so this demo is a pilot, not a non-pilot
  regression-only run. Alternative: omit the marker and never hit
  OpenSpec gates. Rejected because the ask is to test the redesign.
- Keep kit `plan.md` and `specs/{proposals,current}/demo-moons-run.md` as
  pointers. Canonical spec/plan is this change directory.
- Commit each run's `config.yaml` on its own commit, train, then
  `record-run`, then commit registry artifacts. If `train_output.json` is
  untracked, `record-run` will refuse (dirty tree). Then commit that
  output before `record-run` so HEAD still names the trained config.

## Risks / Trade-offs

- [start-work from main] → Create `agent/demo-moons-run` from OpenSpec
  HEAD; record as a walkthrough finding, do not silently change
  `start-work.sh` in this workstream.
- [record-run vs trainer output dirty] → Commit generated
  `train_output.json` before `record-run` if the demo script as written
  leaves the tree dirty.
- [origin/agent/demo-moons-run is a stale unrelated ref] → Local branch
  from OpenSpec HEAD; do not reset to origin.

## Open Questions
