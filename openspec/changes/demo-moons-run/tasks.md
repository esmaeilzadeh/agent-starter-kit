## 1. Workstream skeleton

- [x] 1.1 Intent with `Engine: openspec` and Explore-skipped line exists at `work/demo-moons-run/intent.md` (`grep -E '^Engine:[[:space:]]*openspec[[:space:]]*$'`)
- [x] 1.2 OpenSpec change `openspec/changes/demo-moons-run/` has proposal, delta spec, design, tasks (`openspec validate demo-moons-run --strict`)
- [x] 1.3 Kit `work/demo-moons-run/plan.md` and `specs/proposals/demo-moons-run.md` plus `specs/current/demo-moons-run.md` are pointers only (`./ask check-workstream demo-moons-run`)

## 2. moons-narrow

- [x] 2.1 Commit `results/moons-narrow/config.yaml` with `hidden_layer_sizes: [8]` on a clean tree (`git show HEAD:results/moons-narrow/config.yaml`)
- [x] 2.2 Train `python3 scripts/train_moons.py --run-id moons-narrow` so `results/moons-narrow/train_output.json` contains `accuracy`
- [x] 2.3 Commit `train_output.json` so the tree is clean (`./ask check-clean` exits 0). Literal Path A (train then record-run) is expected to refuse here; that is a walkthrough finding, not a silent demo-doc edit.
- [x] 2.4 `./ask record-run --run-id moons-narrow --commit-sha "$(git rev-parse HEAD)" --metric` equal to that file's `accuracy`; SHA equals HEAD
- [x] 2.5 Commit record-run artifacts (`run_manifest.json`, `summary.json`, `results/RUN_REGISTRY.md`) so the next run starts clean

## 3. moons-wide

- [x] 3.1 Commit `results/moons-wide/config.yaml` with `hidden_layer_sizes: [32]` on a clean tree after 2.5
- [x] 3.2 Train `python3 scripts/train_moons.py --run-id moons-wide` so `results/moons-wide/train_output.json` contains `accuracy`
- [x] 3.3 Commit `train_output.json` so the tree is clean
- [x] 3.4 `./ask record-run` for `moons-wide` writes a registry row whose `git_sha` differs from `moons-narrow`
- [x] 3.5 Commit `moons-wide` record-run artifacts and the registry update

## 4. Close

- [x] 4.1 Viewer data: Python load of `scripts/view_runs.py` `_rows()` returns both run-ids with parsed configs
- [ ] 4.2 `./ask verify --work-id demo-moons-run` pass, including OpenSpec preflight and `validate --strict`
- [ ] 4.3 `./ask record-result --work-id demo-moons-run --commit-sha HEAD --result pass` then Accept SHA in `acceptance.md`
- [ ] 4.4 After Accept SHA: `./ask openspec-archive demo-moons-run` moves the change under `openspec/changes/archive/`
