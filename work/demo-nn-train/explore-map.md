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

None from the human yet. Facts below are research, not decisions.

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

- Demo-doc-only vs also shipping a tiny trainer in this repo.
- Where the NN lives (this repo vs a sibling ML repo).
- Provenance shape: extend `record-result`, copy ILP registry, or both.
- How small the net/dataset must be (CPU minutes vs hours).
- Whether Path A/B kit-pipeline shape stays.

## Out of scope (provisional)

- Porting Popper / 1d-ARC / Cloud Agent VPS eval from the ILP repo.
- Changing dirty-tree / work-branch / Accept policy.
- Phase 3 / CI farm.

## Handoff to Intent

**Status: STILL_FOGGY** — destination named, grill frontier open.

**Owned so far:** Why = stop citing scores without a path + SHA. What (draft) = replace `kit-status` as the demo vehicle with a tiny NN experiment loop that records each run like ILP provenance.

**Blocked on:** scope (doc vs code), home of the NN, provenance artifact shape, experiment size. See Explore grill round 1.
