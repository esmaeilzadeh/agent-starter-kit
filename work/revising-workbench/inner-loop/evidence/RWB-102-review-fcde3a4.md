# Independent RWB-102 review: fcde3a4

**APPROVED. Ownership boundary APPROVED.** Reviewer `/root/review_revising_plan`, independently selected `gpt-6.1-sol` / high. Exact candidate `fcde3a40792bc9ba4f332b4165ae3a3f1a439034`; admission base `c2635515f4f4643344b8483b86ea7d8e046d4bab`; accepted contract/inventory base `5964fbfb56128e95676f0b991852ac58529cb8f8`. Complete source/task history from original `c3c148c4d483d9b8cc9ad50915c81e60ea07abb5`, including pre-new-base WIP, remains included. Previous reports are preserved; reviewer changed only runtime review artifacts.

## Unadopted integration correction

Production delta from the independently approved 6cf34f5 is confined to `_ask/scripts/inner_loop/driver.py`: `integrate_ready` supplies the qualified execution selector when the workstream has adopted an Engineering Model; unadopted work supplies no model selector. The same selection is passed to nested Git integration. This restores the established unadopted kit-task integration route without changing TaskResult validation, independent review, source cleanliness, immutable verification, candidate/review rechecks, FF-only Git integration, resulting tree/SHA verification or state folding. Adopted v2 still supplies its explicit execution identity at both admission boundaries.

The new mapped regression invokes real `integrate_ready` on a committed unadopted repository with a running task. It now reaches mandatory TaskResult validation and refuses the absent result; it previously refused for an inapplicable adopted-model alias. That negative assertion alone does not prove successful integration, so I also ran the actual CheckPlan shell entrypoint in a clean immutable candidate archive:

- `bash _ask/tests/test-inner-loop-reliability.sh`: **29 tests pass**. This includes real successful in-place integration and executed lineage, required-check failure preventing FF/state advancement, independent review and ownership refusal, candidate/source/ref changes, locking and recovery paths.
- `python3 -m unittest _ask.tests.test_revising_context`: **all three mapped passage matrix cases pass**, including adopted-v2 missing-context refusal before candidate reads, adopted successful integration SHA/state lineage, valid-v1 routes, F9/F3b and direct/CLI F10 external-save assertions.

Both commands ran with ambient PYTHONPATH/PYTHONHOME removed and bytecode disabled; the shell entrypoint sets its own repository script import path. The candidate's actual CheckPlan includes this shell suite through the unchanged ask-kit mandatory shell-test glob. No real repository source, coordinator state, accepted ref or commits were mutated by reviewer execution.

## Prior findings, callers and obligations

The full source/caller assessments in the preserved 6cf34f5 and f70 reports remain applicable and were checked against the complete task history plus this two-file delta. F1-F10/F3b remain resolved: persisted resolution binding; qualified execution and actual plan ownership; actual review target derivation; real selected startup guard; safe missing historical content/no fallback; Markdown fence grammar; foreign case/mapping closure; valid-v1 compatibility; exact-snapshot schema dispatch; no generic publication on CLI scope refusal; one captured review body through admission/semantic validation/digest/recording.

All eight amended real caller paths remain assessed: verification `run.py`; traceability `cli.py` and `evidence.py`; engineering-model `__main__.py`; inner-loop `__main__.py`, `driver.py`, `evidence.py`, `integrate.py`. The only new production change is in the actual driver integration path described above. Current/committed safe passage resolution, complete-chain identity, exact headings/rows, ambiguity/fences, persisted reloads, foreign case/mapping/helper/source closure, current/full/cached freshness, optional unrelated gaps versus selected-task required companions, stale-action refusal, real foundation registry/order/lineage and retained baseline guard checks remain substantive. No accepted authority, immutable runner, integrity, CheckPlan, CAS or FF-only gate is weakened.

Machine decisions explicitly approve every assigned case and type: three passage cases plus ten unchanged guard cases; EM-001 integration, EM-002 integration, EM-007 unit/integration/e2e and EM-015 unit/integration. This certifies accepted RWB-102 scope, not later task or whole-workstream acceptance.

All 14 worker Python sources fit amended ownership. Accepted-contract inventory and full original-base Python source scope agree; three changed methods map to the accepted new cases; no unmapped test methods or inventory exclusions. Coordinator plan/design/TaskGraph amendment, accepted pin, audited state/base history and RWB-101 runtime archive remain explicit approved exclusions. Source already present in the refreshed task base received no review exemption.

Pinned digests remain unchanged: spec `626fab82df682bdc7b382e4188bc822e488a8bf4ca9682a209be535fcea119bd`; plan `936e4cb9a06d550476170c299c9a64e337cd6c9c833da3ce5952c871f87a2e7b`; graph `e691e26e2865f165d3a59f57d4d2144675fb48f1c16ded0804aff6dbb3f6160a`.

## TDD and exact retained evidence

Test-only red `d9ceb6ffde1b32d6c8f6ebc81f0eceedb8a500da`, registered run `019e708bb70b49a0b8b27d928793cd78`, has one expected passage-action `behavior_assertion` failure and 12 passes, all runners collected. Final registered run `a6fa8177ca6543fab1cc548cc7fb4e06` binds this exact candidate and passes all 13. Latest red/final test bytes are identical.

Both runs exist in coordinator `traceability/executions.json`. Canonical report-ledger digests, retained output hashes and every case's immutable Git source digest independently match. TaskResult's exact candidate, admission base and commands match this pair. Earlier registered assertion history for original behavior and F1-F10/F3b remains as assessed in preserved reports; no assertion weakening, exemption, regression relabel or unregistered supplemental red supports approval.

Exact evidence:

- `work/revising-workbench/traceability/runs/019e708bb70b49a0b8b27d928793cd78/results.json`
- `work/revising-workbench/traceability/runs/a6fa8177ca6543fab1cc548cc7fb4e06/results.json`
- `work/revising-workbench/inner-loop/results/RWB-102.json`

Machine input `work/revising-workbench/traceability/RWB-102-review-input-fcde3a4.json` passes `review_errors` with **zero errors**, including exact candidate/spec/plan/source/inventory bindings and complete per-case/type decisions. Coordinator may record this review and execute the integration CheckPlan for this candidate.
