# Explore Map: NN training demo with per-experiment SHA binding

## Destination

Replace the current facilitator demo vehicle (`kit-status` script) with a **simple neural-net training plan** where each experiment is recorded with **result + commit-hash binding**, in the style of `object-based-ilp-1d-arc` (`eval-run-meta/v1`, `run_manifest.json`, `results/RUN_REGISTRY.md`).

A facilitator finishing the demo should be able to answer: *Which experiment? Which metric? Which git SHA? Which artifact path?*

## Notes

- Kit 00 Explore (not Cursor Explore). Skills: wayfinder (local map), grilling, research facts from this repo + the ILP repo.
- Do not implement the trainer in Explore.
- Standing preference from prior kit work: artifacts over ceremony; SHA required to claim a result (`./ask record-result` already refuses a missing SHA).

## Tracker map (optional)

None. Canonical map is this file.

## Decisions so far

- **Q1 (scope + run model):** The demo ships a trainer you can actually run. **Both** trainer-code edits **and** hyperparameter edits are part of the commit whose SHA the result binds. Not doc-only; not “point at the ILP repo.”
- **Q7 (config location):** Hyperparams are a **config file in that run’s directory** (`results/<run-id>/config.yaml`, not a shared `configs/` tree). Create/edit it → commit (with any code change) → train → `record-run` against that SHA.
- **Q2:** Tiny **real** dataset (option 2 / B) — not XOR-only, not ILP-scale.
- **Q3:** New **`./ask record-run`** writing the ILP-shaped schema (option C). `record-result` stays for workstream Accept. Comparison to B is in this Explore turn.
- **Q4:** Keep Grill→Accept Path A/B. Only the vehicle changes (train + record-run instead of `kit-status`).
- **Q5:** Dataset = sklearn `make_moons` (all recs).
- **Q6:** Framework = numpy + sklearn MLP (all recs).
- **Q8:** `./ask record-run` refuses a dirty tree; `--commit-sha` must be `HEAD` (all recs).
- **Config format (default):** YAML `results/<run-id>/config.yaml`.

## Research facts (not decisions)

### Current kit demo (`_ask/docs/demo/end-to-end-plan.md`)

- Audience: developer learning the kit. Duration ~45–90 min Path A; Path B +~20 min Explore.
- Vehicle: `scripts/kit-status.sh` — print OK/MISSING for kit paths. **Not implemented in this repo**; the demo *script* tells the facilitator to build it as `demo-kit-status`.
- Proves: intent + spec, clean tree + `agent/<id>`, `./ask verify` + SHA, spec-change interrupt, pinned skills.
- Links: root `README.md`, `AGENTS.md`.

### Current kit provenance

- `./ask record-result --work-id --commit-sha --result [--notes]` writes `work/<id>/result.json`.
- Refuses missing SHA. Shape is workstream pass/fail, **not** an experiment campaign (no metric, host, config knobs, registry).
- `./ask verify` prints `commit_sha` and writes gitignored `verification-result.json`.

### ILP reference (`object-based-ilp-1d-arc`)

- Skill: `eval-run-provenance` (`eval-run-meta/v1`).
- Collector: `solver/run_meta.py` → `git_sha`, `git_branch`, `git_dirty`, host, knobs, timestamps.
- Per campaign: `results/<id>/…/run_manifest.json` + `summary.json` (`run_meta`) + per-task rows.
- Index: `results/RUN_REGISTRY.md` — cite **path + git_sha + metric** (e.g. `40/54`).
- Missing SHA labeled `best_effort_historical`; do not invent SHAs.
- Result trees that will be cited are **not** gitignored.

### Gap

Kit demo SHA-binds a **workstream**. ILP SHA-binds each **experiment run**. The request is to teach the latter in the kit demo.

## Not yet specified

None. `record-run` flags and registry append are implementation defaults (spec).

## Out of scope (provisional)

- Porting Popper / 1d-ARC / Cloud Agent VPS eval from the ILP repo.
- Changing dirty-tree / work-branch / Accept policy.
- Phase 3 / CI farm.

## Handoff to Intent

**Status: DESTINATION_CLEAR.**

**Why:** Scores without path + SHA are not citable.

**What:** Replace `kit-status` as the Path A/B vehicle. Ship a moons + sklearn MLP trainer and a Streamlit run viewer. Each run is `results/<run-id>/config.yaml` plus any code change, committed, trained, then `./ask record-run` (ILP schema; dirty refuse; SHA = HEAD). `record-result` still closes the workstream.

**Locked:** Q1–Q8 as listed under Decisions so far. Pin `developing-with-streamlit` @ `streamlit/agent-skills#v1`.
