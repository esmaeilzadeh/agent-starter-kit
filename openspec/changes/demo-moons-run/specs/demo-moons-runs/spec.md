## Purpose

Cite two named sklearn moons MLP runs in the eval registry: each row is
path plus git SHA plus metric, and the two runs bind to different HEAD
commits.

## ADDED Requirements

### Requirement: Per-run YAML
Each named run SHALL store hyperparameters in
`results/<run-id>/config.yaml`. The file MUST exist before training that
run.

#### Scenario: Config present
- **WHEN** `scripts/train_moons.py --run-id moons-narrow` runs
- **THEN** it reads `results/moons-narrow/config.yaml` and writes
  `results/moons-narrow/train_output.json` containing `accuracy`

#### Scenario: Config missing
- **WHEN** that trainer runs for a run-id with no `config.yaml`
- **THEN** it exits non-zero and does not write a metric file

### Requirement: Commit before train
The `config.yaml` for a run MUST be committed on `agent/demo-moons-run`
before that run is trained. Training MUST NOT start on a dirty tree.

#### Scenario: Clean config commit
- **WHEN** `results/moons-narrow/config.yaml` is the only new run input
  and `git status --porcelain` is empty after that commit
- **THEN** training of `moons-narrow` may start

### Requirement: Named runs
This workstream SHALL record exactly these two runs:

- `moons-narrow` with `hidden_layer_sizes: [8]`
- `moons-wide` with `hidden_layer_sizes: [32]`

Shared fields unless a later Spec Change says otherwise: `seed: 0`,
`n_samples: 200`, `noise: 0.25`, `learning_rate_init: 0.01`,
`max_iter: 400`.

#### Scenario: Narrow hidden size
- **WHEN** `results/moons-narrow/config.yaml` is committed
- **THEN** `hidden_layer_sizes` is `[8]`

#### Scenario: Wide hidden size
- **WHEN** `results/moons-wide/config.yaml` is committed
- **THEN** `hidden_layer_sizes` is `[32]`

### Requirement: SHA-bound record-run
Each trained run SHALL be recorded with `./ask record-run` using
`--commit-sha` equal to HEAD. `record-run` contract stays the existing
kit command (`specs/current/demo-nn-train.md`, Build Spec §25): refuse
missing SHA, dirty tree, and SHA ≠ HEAD. This spec does not redefine
those refusals.

The two registry rows MUST have different `git_sha` values. Each row MUST
cite path + git SHA + metric. After record-run, the run directory MUST
contain `config.yaml`, `run_manifest.json`, and `summary.json`.

#### Scenario: Distinct SHAs
- **WHEN** both `moons-narrow` and `moons-wide` have registry rows
- **THEN** the two `git_sha` values are not equal

#### Scenario: Dirty refuse (existing command)
- **WHEN** `./ask record-run` runs on a dirty tree
- **THEN** it exits non-zero and does not write a passing registry row
  for that invocation

### Requirement: Viewer lists both configs
`scripts/view_runs.py` SHALL list both named runs with their registry
SHA and the hyperparameters from each `config.yaml`.

#### Scenario: Both rows visible
- **WHEN** the viewer loads `results/RUN_REGISTRY.md` after both
  record-run invocations
- **THEN** it exposes run-id, metric, git_sha, path, and parsed config
  for `moons-narrow` and `moons-wide`
