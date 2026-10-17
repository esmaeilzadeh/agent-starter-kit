# WB-009 preliminary partial-candidate review

Verdict: **REJECTED / INCOMPLETE**. This is an independent audit of partial
candidate `463f7f04e338a4250611bd1ce4bd5ab3d519b4ff`, not final task integration
approval. A refreshed final candidate, complete retained task result and real-pilot
evidence still require independent review.

Reviewer: `/root/review_wb009_tests`, child of `/root`; Codex runtime; resolved
review binding `gpt-6.1-sol`, high; parent model not supplied. Reviewed an immutable
detached snapshot at `/tmp/ask-wb009-candidate-review-463f7f0`. No shared production
or test source was edited and no commits were made. This scratch report is
attributable to the stated SHA only.

Authority: accepted WB-009 handoff, plan, test plan, canonical specification
revision 3, original six-finding draft review, session evidence correction and
this reviewer's reports at 3caf633, 28b37d9 and 109976c/e7f721a. All sixteen
accepted IDs, pins and ownership remain unchanged. Protocol: kit 07 Review;
version-matched Streamlit skill discovered from the pinned environment. Scope
is now partial production correctness plus retained test design and continuity.

## Material production findings

1. **P1 — Invalid retained executions are still presented as passed.**
   `_ask/ui/workbench_tests.py:68–78` prints each row's `outcome` without checking
   `output_status` or `source_status`. The backend correctly rejects tampered
   retained bytes, but leaves the claimed outcome alongside its diagnostic.
   Independent diagnostic mutated the exact
   `consumer.green['executions'][0]['output_artifact']`, reloaded U and then opened
   the actual application result panel. Backend row: `outcome=passed`,
   `output_status=invalid`, diagnostic `execution log digest does not match retained
   bytes`; UI: `Outcome: Passed`. Render invalid/stale/unavailable states explicitly
   and distinguish the untrusted claimed outcome from a verified retained outcome.
   Do not promote that row to success. The same panel omits absent timestamps and
   durations rather than explaining unavailable fields, omits failure detail and
   run/execution/contract/source provenance, and says no recorded execution is
   attached even while displaying historical executions. Preserve honest current
   versus historical versus invalid presentation, with qualified per-run identity.

2. **P1 — Default candidate/HEAD is missing from selected-detail cache identity.**
   `workbench_loading.py:165–179` computes and looks up the key before resolving
   HEAD; `detail_identity` hashes the optional argument, which is `None` for current
   working-source UI loads. Independent disposable-fixture diagnostic loaded U,
   made an empty Git commit and loaded U again through the same cache: new HEAD
   differed, `same_object=true`, returned candidate remained the old HEAD. Evidence
   currency and displayed Git revision can therefore be stale without any source
   or definition edit. Resolve immutable candidate/current-head authority before
   forming the key; include all values used by source/evidence currency checks.
   `workbench_context.reset_for_work` also never clears
   `_engineering_selected_detail_cache`; explicit Refresh can reuse the previous
   verdict when the hash is unchanged. Connect `clear_detail_cache` to refresh and
   source/work reset, or prove equivalent mandatory revalidation semantics.

3. **P1 — Planned tests without a model test node cannot receive an evidence
   projection.** `streamlit_app.py:927–935` defaults the model `node_id` to planned
   test ID E; `project(...node_id='E')` raises unknown Engineering Model node.
   Diagnostic: E qualified source is loaded, execution history has three retained
   rows, but evidence is unavailable with `unknown Engineering Model node: E`.
   The connected outline intentionally includes planned tests, so its detail
   loader must support their canonical plan reference without inventing model
   nodes. Keep selected-only evaluation and work/test/contract qualification.
   This is distinct from the hierarchy fixture's changed-plan issue below.

4. **P2 — Gitless and invalid evidence reasons are suppressed; actionable debug
   command coverage regressed.** `workbench_tests.py:57–78` displays a generic
   current-unavailable message but never renders `evidence_state.diagnostic` or
   history's top-level diagnostic. Independent UI-gitless red confirms the real
   reason `Git evidence inspection is unavailable` is absent. `workbench_debug.py`
   renders only `git show` and `./ask model show`; the previously retained
   `./ask traceability check-completion` command is missing. Show the actual
   Git-unavailable/invalid reason and qualified inspect commands in the appropriate
   expanded detail, while keeping source inspection usable.

5. **P2 — Resolved decision routes have two authorities.**
   `streamlit_app.py:890–903` appends resolved routes only after `render_outline`;
   `_open_related_route` and reset paths call `build_outline`, which does not know
   those routes. The new direct button and persistence are real and pass the
   browser journey, but related navigation/history cannot consistently resolve
   the same canonical decision. Put resolved routes in the shared outline builder
   and preserve ancestors/history there. Correct migrated tests to the resulting
   canonical route rather than preserving obsolete `route:decision` selectors.

6. **P2 — Task verified-completion wording still trusts path existence.**
   `workbench_tasks.py:27` defines `verified` as a truthy result path plus status
   completed, without checking result bytes, candidate or authority. This is
   pre-existing within the reviewed task surface, not introduced by this repair.
   The accepted distinction between lifecycle and verified completion remains
   unresolved for missing/invalid task results. Use qualified result state or
   describe merely a recorded result reference. Do not label it verified from a
   path alone.

## Test and harness defects requiring separate repair

7. **P1 — Hierarchy fixture changes the contract after retaining its executions.**
   `_hierarchy_fixture` rewrites `task_scopes` after `evidence_workbench` created
   retained Consumer runs. `load_selected_detail` correctly asks history for the
   new captured plan digest, and `execution_history` correctly excludes old-plan
   entries. Independent hierarchy run reaches E, qualified case/source and
   assertion text, then fails missing Passed. Construct/run the final fixture
   contract before recording executions, or explicitly present old-contract
   historical evidence with its original contract identity. Do not remove or
   weaken digest matching. One-owner U/build and E/review-build plus U's
   scenario-mediated shared relation are now correctly asserted in source.

8. **P1 — The mapped cache test still mutates an arbitrary execution log.**
   `test_engineering_workbench_performance.py:126` uses first `glob('*/*.log')`;
   changing to historical candidate did not bind this to the selected final-green
   run. Independent mapped case fails at line 144 because evidence is equal after
   mutation; this alone is not proof of an authoritative final-green failure.
   Choose the exact final-green artifact from its retained report and assert the
   baseline test/case/runner/candidate/execution tuple. Restore and reload each
   mutation independently: review currently checks identity only; accepted-ref
   mutation occurs with the bad review still present; source mutation checks only
   key difference. Assert actual source/output states after each reload. The
   separate genuine tampered-log UI observation in finding 1 is not dependent on
   this defective oracle.

9. **P1 — Accepted WB-performance still excludes actual app lazy-work assertions.**
   The passing AppTest instrumentation is a separate unaccepted method
   `test_overview_is_lazy_and_selected_details_are_cached`; exact accepted case
   filtering does not run it. Move its assertion body to a helper invoked by the
   mapped case, retaining all assertions. Count selected IDs/paths rather than
   merely positive source/evidence work; cover unchanged parse/evaluation reuse,
   explicit refresh, admitted definition changes and selected-only bounded work.
   Repeat those observations on valid 100/1,000-task fixtures. Current structural
   helper still creates an unadmitted, incomplete Snapshot and times only
   projection/outline. Its source-file count is declared metadata, not real source.

10. **P1 — Benchmark remains fixture-only and has unreachable readiness.**
    Cold `ready()` now checks usable overview content, filter rows are actually
    enumerated, report persistence no longer has the UnboundLocalError, and warm
    20/cold 5 plus 1500/500/500/1000/4000 declarations are retained. Preserve those
    corrections. But source/result timing waits visible `Snapshot digest` without
    opening the collapsed debug expander; `render_debug` returns before rendering
    it. This will time out even after outcome wiring is fixed. Wait for qualified
    source assertion and actual retained result/provenance content, opening debug
    if that content is required. The cold test still trusts `limits['cold']`
    without asserting it equals 4000. Partial report initialization happens after
    input parsing and structural work, so early failures can still leave no report;
    failed stages/elapsed partial samples are not retained. Fixture labeling is
    now honest, but there is still no real-pilot workload report, and hardcoded
    purpose/scenario/E routes cannot serve arbitrary pilot data.

11. **P2 — Migrated test failures need qualified corrections, not weakened
    observations.** UI-test-source expects C1 whereas fixture defines P-001.
    UI-persist/conflict seek obsolete `route:decision` after resolution whereas
    actual `resolved-decision:choice` is independently reachable. UI-overview-results
    patches only `inspect_evidence`, but the renderer now consumes
    `execution_history`; its fabricated Passed is disconnected from the rendered
    rows. UI-expander-ids injects nested evidence that is never rendered and
    checks uniqueness vacuously. Supply selected qualified history/nested records,
    require both repeated values and independently addressable controls, and keep
    diagnostic warning severity and actionable debug assertions. UI-browser's
    first Passed assertion now matches TWO real retained outcomes in strict mode;
    scope by the exact retained tuple, rather than choosing an arbitrary first row.
    UI-browser-gitless clicks a result route whose selected-test caption already
    existed, then immediately opens debug; independent failure shows missing
    Snapshot digest after the details element was momentarily open. Await the
    selected result route's primary state before interacting with its debug key
    and rerun before treating this as a production focus/debug failure.

## Accepted-ID observation matrix

| ID | Independent observation at this SHA / remaining qualification |
| --- | --- |
| WB-browser-journey | Assertion fail: E result missing Passed; full chain/exact filter IDs reached first. Foreign-source/no-write tail not executed. |
| WB-browser-accessibility | Pass: real Tab traversal, normal/large/focus contrast, source/debug and attributed decision journeys at 390/1440; fresh-session narrow choice and unblocked task observed. |
| WB-performance | Assertion fail: arbitrary-log evidence equality; mapped app/structural/refresh coverage incomplete. |
| WB-latency-budget | Source audited; not independently executed at this SHA. Fixture-only readiness/report gaps above; no pilot result. |
| UI-inspect | Pass for U current missing plus historical outcome/assertions; complete per-run UI provenance still absent. |
| UI-persist | Assertion fail at obsolete resolved route; browser independently proves attributed resolution persistence. |
| UI-conflict | Assertion fail at obsolete final resolved route; stale rejection/refresh guard portion passed before it. |
| UI-browser | Assertion fail: Passed strict-mode ambiguity; stale/reload tail not reached. |
| UI-empty | Pass. |
| UI-gitless | Assertion fail: actionable Git-unavailable reason suppressed. |
| UI-decision-object | Pass for decision access; blocked-task assertion still absent. |
| UI-overview-results | Assertion fail: mocked completion not connected to history renderer; debug command regression also unresolved. |
| UI-overview-hierarchy | Pass for overview, deferred source and connected test/result buttons. |
| UI-test-source | Assertion fail only after real qualified source rendered: fixture P-001 vs obsolete C1 oracle. |
| UI-expander-ids | Assertion fail: injected migration diagnostic absent; repeated nested records not rendered. |
| UI-browser-gitless | Assertion fail at debug readiness; result-rerender synchronization needed; reason suppression independently confirmed. |

## Independent execution and continuity

Unmodified snapshot commands used pinned Python3.12, Streamlit1.59.2,
Playwright1.63.0, PyYAML6.0.3 and `ASK_BROWSER_CHANNEL=chrome`
(Chrome142.0.7444.162). No bundled-Chromium substitution or injected modules.

- Mapped cache case + extra app-lazy case + browser module: 4 tests, 2 pass,
  2 assertion failures, 0 errors, 32.077s.
  `/tmp/ask-wb009-candidate-review-463f7f0-targeted.log`.
- Migrated AppTest module: 10 tests, 4 pass, 6 assertion failures, 0 errors,
  5.048s. `/tmp/ask-wb009-candidate-review-463f7f0-ui.log`.
- Legacy browser module: 2 tests, 2 assertion failures, 0 errors, 13.778s.
  `/tmp/ask-wb009-candidate-review-463f7f0-legacy-browser.log`.
- Additional disposable-fixture diagnostic, not an accepted test:
  `/tmp/ask-wb009-candidate-review-463f7f0-diagnostic.py` and `.log` reproduce
  HEAD-cache reuse, plan-only-node failure and exact final-green tampered-log UI.

Fifteen accepted cases were executed, plus one extra unaccepted app-lazy method;
the latency case was not. These are not a full task runner or final Verify result.

The genuine 109976c missing projection metadata, missing selected source and
focus ratio 2.305 observations justified bounded repairs. Current source retains
the missing-field assertions and the browser retains real focus/contrast
thresholds. Independent extra app-lazy and keyboard cases now pass. Do not rewrite
the original reds as design errors because later unrelated oracles are defective.
No weaker thresholds, removed accepted IDs or pin/spec changes were observed in
the audited test diff. Exact filter ID enumeration replaced fragile status-panel
selectors; restore displayed status/state assertions where those old assertions
carried information beyond identity alone. The schema-correct `resolution` checks
are appropriate, while attribution/reload/task consequence assertions remain.
Earlier withdrawn WB006–008 and artificial-red claims remain withdrawn.

Boundary: e7f721a→candidate production/test/harness paths match accepted WB-009
owned paths. The additional committed benchmark-smoke JSON is evidence, not a
production seam; coordinator must apply the evidence-artifact policy when binding
the final task result. No edit-authority bypass was found in inspected wiring:
decision writes retain captured identity and public guarded edit; foreign view
remains read-only by source. This is limited source-audit evidence, not a completed
foreign-source browser run or a new independent full guard-suite result.

Original six findings remain partially open: hierarchy/foreign provenance (1),
keyboard coverage now improved and independently passing (2), legacy result and
stale continuation (3), cache semantics/mapping (4), structural/pilot evidence (5),
semantic latency/report qualification (6). Final candidate-bound raw retention,
review and integrated checkpoint are outstanding. **No task completion or
integration approval is granted.**
