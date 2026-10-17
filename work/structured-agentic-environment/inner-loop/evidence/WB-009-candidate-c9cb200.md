# WB-009 preliminary bounded-candidate review

Verdict: **REJECTED / INCOMPLETE**, bound to
`c9cb2009ee4c93ac4c500fec0557d04487e771df` only. This is not final integration
approval. Final browser/performance/real-pilot work remains underway.

Reviewer: `/root/review_wb009_tests`, independent child of `/root`; Codex runtime;
resolved binding `gpt-6.1-sol`, high; parent model not supplied. Immutable detached
snapshot: `/tmp/ask-wb009-candidate-review-c9cb200`. No shared production/test edits
or commits. This unique scratch report follows kit 07 Review and continues the
463f7f0 report against the same accepted revision-3 specification, ownership and
sixteen IDs. Earlier reports and withdrawn-evidence correction remain applicable.

## Material findings

1. **P1 — Current working-source inspection now reads committed HEAD instead of
   working-tree bytes.** `workbench_loading.load_selected_detail` resolves an
   omitted candidate into `chosen_commit`, then always calls `qualified_source`
   when Git exists. The ordinary UI passes working-tree context and no candidate,
   so uncommitted source edits are ignored. The identity still hashes working
   bytes, meaning a source edit invalidates the cache but reloads unchanged Git
   content. Separate source selection from evidence candidate resolution:
   working-tree context reads confined working bytes; captured Git context reads
   its immutable selected commit. Resolve HEAD independently for evidence. This
   finding was promptly sent to the coordinator. The subsequent de993222 mapped
   regression and writer's three reported reds are not this reviewer's execution
   at c9; they preserve the reported current-source/HEAD counterexamples for the
   next bounded repair.

2. **P1 — Explicit-candidate cache identity still omits current HEAD.** The omitted
   candidate defect is repaired, but for an explicit historical/foreign candidate
   `detail_identity` hashes only the selected candidate, while source/evidence
   currency depends on current HEAD too. Moving HEAD with unchanged selected
   source, definitions, refs and evidence can reuse old `current` versus
   `historical` classification. Include current HEAD separately from selected
   commit in the key, using the same captured values during evaluation. Preserve
   the working-tree/Git source distinction in finding 1.

3. **P2 — Per-execution provenance remains incomplete and execution ID is inferred.**
   `workbench_tests.py` now explicitly distinguishes recorded outcome, output
   integrity and source currency, and provides real per-run expanders. Those are
   useful repairs. But the expanded record omits actual runner, source SHA, phase,
   scope and task identity; the planned `Case … via r` line is not per-run
   authority. `Execution ID` is derived from the artifact filename instead of
   retained case `execution_id`. The backend validates execution linkage and path
   confinement but does not enforce basename equals ID. Carry authoritative
   fields into the row and render them; do not fabricate an ID from a path.
   Failure detail currently shows only failure_kind, not available actual
   assertion/log detail. Invalid completion reasons stored under
   `completion.errors` are still hidden unless a top-level diagnostic was supplied.
   Real invalid records need the same actionable reason coverage as the synthetic
   migration test.

4. **P1 — Accepted WB-performance coverage is still incomplete.** Exact
   final-green artifact selection and invalid/untrusted rendered-state assertions
   now replace the invalid arbitrary-log oracle appropriately. Accepted-ref
   mutation is independent of the restored review. However review mutation still
   checks only identity, source same-mtime mutation only key difference, and the
   real app lazy/reuse/refresh body remains a separate unaccepted method. The
   accepted runner filters exact mapped case IDs, so it excludes that passing
   body. Invoke a helper from the accepted method. Assert exact selected IDs and
   source bytes, not merely positive call counts; repeat lazy/selected/cache work
   on valid 100/1,000-task fixtures. No canonical ID or pin changes are needed.

5. **P2 — Two independent focused reds require test-oracle qualification.**
   The mapped cache case's final shared-related-route AppTest imports executable
   `streamlit_app` without fixture `ASK_MODEL_ROOT`; its import can call `st.stop`
   before the synthetic script installs its projection/calls the helper. The
   central resolved outline entry is correct in source, and actual persistence
   tests pass. Run the actual app with a fixture root and invoke related navigation
   in its live session, or isolate the helper without executable import effects.
   This failure alone does not prove resolved routes remain broken.

   UI-inspect's `text(app)` collects all expander descendants, including closed
   provenance content. Its no-historical-SHA assertion now fails because the
   actual SHA is inside a closed execution expander. That is not independent
   proof of a visible default-pane hash leak. Preserve the no-default-hashes
   observation by inspecting the visible browser region or an AppTest extractor
   that excludes collapsed details; separately expand and assert exact provenance.

6. **P2 — Nested control assertions improved but still need value identity.**
   UI-expander-ids now supplies selected-test-qualified history and requires two
   distinct execution controls, so the old single-expander false pass is fixed.
   Also require both run IDs/execution IDs and repeated record contents to render,
   and test multiple executions under one retained run where supported. Unique
   labels are not equivalent to unique authoritative execution keys. Keep warning
   severity for migration diagnostics and explicit untrusted execution state.

7. **P1 — Benchmark correctness/evidence obligations remain open.** The harness
   removes the unreachable collapsed `Snapshot digest` wait, and the test now
   explicitly asserts cold limit 4000. Preserve these fixes and unchanged warm
   20/cold 5 plus 1500/500/500/1000 budgets. New source/result readiness checks
   hardcode two Passed and two valid rows without identifying selected retained
   run/case/candidate/source tuples or source assertion content. Check real fixture
   history, including red and both green records, rather than adapting counts
   blindly; qualify outcome and source readiness before timing. Early input and
   structural exceptions still precede partial-report initialization. Structural
   workloads remain projection/outline-only and unadmitted. The browser workload
   is honestly fixture-labeled, but no required real-pilot report is supplied.

## Previous production findings: disposition

| 463f7f0 finding | c9 observation |
| --- | --- |
| Invalid log displayed as verified pass | Bounded repair present: Recorded outcome, explicit invalid integrity and untrusted error; mapped case reaches and passes these assertions independently. Full per-run provenance still incomplete. |
| Omitted-HEAD cache key | Omitted candidate resolved before key; independent mapped assertions pass before unrelated final route-test red. Explicit candidate/current-HEAD issue remains. |
| Refresh retains cache | reset_for_work removes selected-detail cache; independent extra app test passes selected-source/history/evidence reread after refresh. |
| Plan-only test unknown node | Canonical workstream fallback present; mapped historical E assertion independently passes before final route-test red. It is workstream completion, not proof of selected-test execution; qualified history remains essential. |
| Gitless reason/debug commands hidden | Independent UI-gitless and real retained-result/debug AppTests now pass. Verification command restored. Browser exact text and debug synchronization still need current-candidate execution. |
| Resolved route authority split | Central build_outline now owns resolved entry; duplicate app append removed. Independent persistence/conflict AppTests pass. Synthetic helper test needs fixture/import repair. |
| Task path presented as verified completion | Table now says Result reference; detail states contents unverified. Honest wording repair avoids claiming verification. Actual result verification remains outside what this view establishes. |

## All sixteen accepted IDs and independent observations

| ID | Observation at c9 |
| --- | --- |
| WB-browser-journey | Source unchanged; not rerun here. Previous changed-plan fixture/evidence authority and foreign-source tail gaps remain. |
| WB-browser-accessibility | Source/thresholds retained; not rerun here. Independent 463f keyboard/contrast pass is historical evidence only. |
| WB-performance | Independent assertion fail only at synthetic related-route helper after integrity/plan-only/HEAD observations pass; mapping/source/structural gaps above. |
| WB-latency-budget | Source audited, not independently executed; readiness/report/pilot gaps above. |
| UI-inspect | Independent assertion fail: closed-expander descendant included in no-SHA text oracle. |
| UI-persist | Independent pass, including reload, attribution and Ready task consequence. |
| UI-conflict | Independent pass, including stale rejection, refresh and attributed reload consequence. |
| UI-browser | Not rerun; prior strict-mode duplicate Passed and stale/reload tail require corrected qualified selectors. |
| UI-empty | Independent pass. |
| UI-gitless | Independent pass for actionable unavailable reason and usable source. |
| UI-decision-object | Independent pass; explicit original blocked-task observation still absent. |
| UI-overview-results | Independent pass with real fixture history, integrity/currency/unavailable fields and restored debug commands. |
| UI-overview-hierarchy | Independent pass for overview/default hidden source and connected selected test. |
| UI-test-source | Independent pass after canonical P-001 correction; actual source/assertion retained. |
| UI-expander-ids | Independent pass for two controls/warning severity, with value-identity gap above. |
| UI-browser-gitless | Not rerun; prior result/debug rerender synchronization and exact reason-string mismatch require qualification. |

## Execution, continuity and boundary

Unmodified snapshot command:

```text
PYTHONPATH=_ask/tests:_ask/ui:_ask/scripts ASK_BROWSER_CHANNEL=chrome
/tmp/ask-wb009-venv/bin/python -m unittest
test_engineering_workbench_performance.WorkbenchTests.test_lazy_work_and_integrity_bound_cache_invalidation
test_engineering_workbench_performance.WorkbenchTests.test_overview_is_lazy_and_selected_details_are_cached
test_engineering_ui -v
```

Result: **12 cases, 10 pass, 2 assertion failures, 0 errors, 10.397 seconds**.
Log: `/tmp/ask-wb009-candidate-review-c9cb200-focused.log`. Eleven accepted IDs
plus one extra unaccepted method were run. No browser, final latency benchmark,
full Verify or candidate-bound accepted runner was independently executed here.
Pinned environment is unchanged from the previous report. Worker-reported 8/8
and d6 red runs are not substituted for these independent results.

Retained d6a6b853 task report is included under
`traceability/runs/293cfdef0ed7439e8b9380ddbf7b5f10/results.json`, linked by the
execution ledger with candidate/spec/plan/scope/task and exact filtered sixteen
case IDs. The report records 16 collected, 5 passed, 11 failed, zero errors and
phase red. That label alone does not establish all eleven as valid production
reds: known selector, fixture, import/oracle and harness failures remain separately
qualified. This review did not execute d6 or approve its semantic continuity as a
whole. The genuine 109976c metadata/loading/focus reds and the exact tampered-log
463f diagnostic remain valid antecedent observations. The mapped final-green
selection/invalid-state assertions were committed at d6 before the bounded c9
repair. P-001, schema-correct resolution and actual-history fixture changes correct
oracles without removing their accepted observations. No accepted ID/pin/spec or
contrast threshold changes were found. Extra app tests still need mapped reach.

Production/test diff remains within accepted WB-009 owned seams; evidence/report
additions are attributable artifacts for coordinator policy handling. Inspected
guarded write and foreign read-only wiring were not weakened. No independent
foreign-source browser/no-mutation completion is claimed at this SHA. Original
six draft findings are partly repaired, but full browser source/result identity,
accepted mapped performance/structural work and real-pilot retained measurements
remain outstanding. Final fresh-candidate review is required.
