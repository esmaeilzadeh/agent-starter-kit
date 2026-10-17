# WB-009 preliminary full test-design review

Verdict: **REJECTED / INCOMPLETE DESIGN**. This is not candidate integration
approval or a declaration that production repairs must wait for every unrelated
test-design correction. Genuine source-metadata/loading and focus-contrast red
observations described below support bounded repairs now.

Reviewer: `/root/review_wb009_tests`, independent child of `/root`, Codex runtime.
Resolved reviewer binding: `gpt-6.1-sol`, high; parent model not supplied.
Primary test/harness checkpoint:
`109976ce13304f9f3d48983be009263450310a7c`.
Sequential harness/fixture correction audited separately:
`e7f721a5c67c1ba8cfeb1490fbc0af8dee82bf17`.
Detached snapshots under `/tmp/ask-wb009-design-review-109976c` and
`/tmp/ask-wb009-design-review-e7f721a` preserve both exact revisions. This reviewer
edited no shared production/test source and made no commits.

Authority: accepted plan/test plan, canonical specification revision 3,
WB-009 handoff, original six-finding draft review, evidence correction and both
earlier browser-design reports. Reviewed all sixteen WB-009 IDs against browser,
migrated AppTest, performance and benchmark source. Accepted ownership, pins,
criteria and all sixteen assignments remain unchanged. The extra performance
test method does not acquire a new accepted ID through this review.

## Blocking test/harness findings

1. **P1 — Latency report persistence currently fails before browser work.**
   At e7f721a, `_ask/ui/benchmark_workbench.py:204` defines `persist_partial`, then
   assigns `output_path = Path(output_path)` inside that nested function. Python
   therefore treats `output_path` as local; line 205 reads it before assignment.
   Rename the inner variable `target_path` and preserve the captured parameter.
   Independent latency-case execution fails at test line 237 because no report
   was created. This is a harness setup defect, not latency behavior-red evidence.
   Report initialization also occurs only after structural workload execution;
   an earlier fixture/read/structural exception still leaves no partial report.
   Initialize candidate/environment/workload/error state early and retain it on
   every meaningful failure path. Persist completed samples as they arrive and
   failed sample stage/elapsed information before propagating the error.

2. **P1 — Cache mutation assertions do not yet isolate authoritative outcomes.**
   At e7f721a, `_ask/tests/test_engineering_workbench_performance.py:115` loads
   default current HEAD, whose evidence is unavailable after fixture adoption.
   Line 124 picks an arbitrary first retained log; it may be an unrelated red
   execution. Requiring its mutation to change already-unavailable current
   evidence is an invalid oracle. Select the actual retained final-green execution
   log, for example `consumer.green['executions'][0]['output_artifact']`, and bind
   the baseline load to its historical candidate. First assert U's actual passed
   outcome and candidate/case/execution/runner identity, then mutate that exact log,
   reload through the same cache and require invalid/unavailable evidence.
   Review mutation at lines 144–149 checks only identity, never reloaded displayed
   evidence. The accepted-ref mutation is then performed with the bad review still
   present, so invalid evidence cannot establish the ref's independent effect.
   Restore each input before the next mutation, reload for each cause, and assert
   the authoritative changed state. Same-mtime source mutation is now real, but
   lines 174–178 still check identity only; reload and inspect changed qualified
   source content. Preserve unchanged-cache reuse and guard checks.

3. **P1 — The mapped performance case does not execute its app-laziness checks.**
   The accepted `WB-performance` binding is
   `test_lazy_work_and_integrity_bound_cache_invalidation`. The actual AppTest
   instrumentation was placed in a separate newly discovered method,
   `test_overview_is_lazy_and_selected_details_are_cached`, at line 183. The
   accepted runner filters to exact accepted case IDs, so those app checks are
   absent from mapped task evidence. Invoke a helper containing those assertions
   from the mapped method; do not change accepted IDs/pins to hide the omission.
   Its current `count > 0` assertions also allow eager loading of every test.
   Check the selected test IDs/paths and exact bounded work. Assert refresh
   clears/revalidates affected content, underlying model/spec/plan changes update
   identity and results, and unchanged metadata navigation avoids repeated parse/
   evaluation work. None of those observations is currently established. The
   `edit(..., '0' * 64, ...)` check is a useful guard regression but does not show
   an actual previously displayed identity becoming stale after definition edits.

4. **P1 — Structural workloads and pilot benchmarking remain incomplete.**
   `benchmark_workbench.structural_workload` genuinely constructs and times
   100/1,000-task projections/outlines and checks counts. However it constructs
   `Snapshot` directly from incomplete plan metadata, never validates/adopts the
   fixture, and never exercises overview source/evidence counters or bounded
   selected loading at those sizes. `workbench-design.md:157` requires those
   structural lazy-work observations to be repeated at both sizes. One declared
   `test_scale.py` path is counted as a source file although no file is supplied;
   either provide representative source bytes or label it as declared metadata.
   The duplicate `_structural_workload` helper in the test module is unused.
   e7f721a correctly labels the browser workload `isolated-consumer-fixture`;
   that correction does not supply the separately required real-pilot evidence.
   Hardcoded Purpose/scenario/build/U routes cannot benchmark an arbitrary actual
   pilot despite accepting `--work-id`. Discover qualified route/content targets
   from its admitted data or accept explicit target descriptors; retain separate
   fixture and real-pilot reports. Do not claim the fixture measured the pilot.

5. **P1 — Latency readiness and fixed cold threshold remain insufficient.**
   e7f721a adds useful warm overview/scenario content assertions and preserves
   20 new browser contexts on one warm server plus five process restarts. Warm
   overview/navigation/filter/source budgets remain 1500/500/500/1000ms.
   But `ready()` at harness lines 134–139 checks only top heading and selected
   outline button; the five cold measurements stop there at line 285, before
   usable overview content is established. Reuse full overview readiness for warm
   and cold. Filter measurement checks dropdown option `aria-selected`, not the
   resulting displayed row set. Source checks show qualified metadata but not
   source assertion content; result measurement stops at `Recorded execution`
   heading, not actual selected outcome/provenance. Wait for those exact semantic
   contents before recording samples. In the test, lines 260–262 compare cold
   samples to the report's own `limits['cold']`, with no assertion that this value
   equals 4000; use literal 4000 and assert the declared limit too. Keep nearest-
   rank p95 and failure reporting, without reducing correctness for timing.

6. **P2 — Exact-filter helper has a rerender race.**
   e7f721a now enumerates all normalized filter-row keys and checks row count,
   resolving the earlier false-pass subset check. But browser lines 72–79
   enumerate immediately after click, before awaiting `Clear filter`. Independent
   execution at 109976c returns an empty set; a diagnostic that first awaits
   `Clear filter` sees the correct exact scenario rows. Await filter readiness
   and expected row count before enumerating. The normalized Streamlit classes
   were verified in the DOM as `st-key-overview-filter-open-scenarios-scenario`
   and `st-key-overview-filter-open-scenarios-scenario-other`. Earlier suggested
   literal-colon classes were incorrect; the new normalization helper is correct.
   Prefer a stable detail/filter region over `.last` border-container selection.

7. **P2 — Remaining AppTest oracles need correction and non-vacuous coverage.**
   `_ask/tests/test_engineering_ui.py:81` requires `Planned assertions for C1`,
   while `workbench_model` defines criterion `P-001`. Correct that canonical
   identity; its earlier missing-source failure is still a genuine observation.
   `UI-expander-ids` checks unique labels but does not require both repeated nested
   records' values to render, so a single debug expander could satisfy uniqueness.
   Supply selected-test-qualified nested evidence, assert both repeated records
   exist, and verify distinct addressable controls; preserve warning rather than
   error severity. `UI-gitless` does not expand its AppTest debug trace, and
   `UI-decision-object` checks Build but never asserts its blocked state. Add
   those accepted observations. `UI-inspect` checks U and canonical assertion
   text but not its full case/revision provenance in the displayed UI.

8. **P2 — Browser identity/keyboard coverage is improved but not complete.**
   The tests now traverse story/scenario/completed Build/U/results; use normalized
   result keys; restore positive retained pass, current-unavailable and historical
   states; inspect canonical assertions; check source metadata; open gitless debug
   and require the actionable reason and inspect commands. e7f721a fixes the
   dangling task result path, restores single execution ownership and verifies
   U's scenario-mediated association to review-build, and captures stale-publication
   baseline after the legitimate external edit. Retain these repairs.
   However browser source/evidence checks still do not compare actual displayed
   run/execution/contract/candidate values against the fixture tuple; domain
   preflight assertions alone do not prove correct attachment in the UI. The
   alternate branch only checks selected work/U, unique source marker and missing
   execution, not its resolved source commit identity. Assert those provenance
   values in expanded debug while keeping raw hashes collapsed by default.
   Keyboard inspection covers both widths, mandatory status, normal/large/focus
   contrast and controlled debug expansion. Decision submission now runs at 390
   only; option/actor/rationale/submit focus visibility/contrast are not checked.
   Complete the primary decision/control coverage at 1440 as well, using fresh
   open-decision fixtures/sessions as needed. Preserve real keyboard navigation,
   chosen option ID, attribution and new-session task consequence.

## Genuine red observations supporting bounded production repairs

At immutable 109976c, the admitted projection has U but omits required `case_id`,
`runner_id` and source metadata despite valid canonical plan/source bytes. The
mapped performance test fails at line 110 on missing `case_id`; independent
AppTest selected-route instrumentation fails with `_working_source.call_count == 0`
at line 213. Canonical source/expected assertion absence in UI-test-source,
UI-overview-hierarchy and UI-inspect, and selected evidence not being evaluated
in UI-overview-results, are genuine accepted behavior observations. These support
bounded projection/selected-loading/render wiring repair now, while invalid
downstream test oracles and unrelated harness defects are corrected separately.

Focus was independently checked against the actual rendered control, not just
theme constants. Before focus: outline width 0, shadow none. After actual Tab
focus: active element is the scenario button, outline width 0, and visible ring
`rgba(15, 92, 94, 0.5) 0px 0px 0px 3.2px`; button background is
`rgba(146, 173, 191, 0.15)`. The unchanged helper measures **2.305:1**, below the
accepted 3:1. This supports a bounded focus styling repair now. Diagnostic log and
screenshot: `/tmp/ask-wb009-design-review-109976c-diagnostic-wait.log` and
`/tmp/ask-wb009-design-review-109976c-focus.png`.

The first immediate filter enumeration failure is a test race, the wrong
pre-edit publication baseline at 109976c is an invalid oracle (fixed in e7f721a),
and the report-persistence defect at e7f721a is setup failure. None is valid
latency/stale-publication/summary behavior-red proof. Preserve genuine red
assertions and exact candidate identities through later changes; do not relabel
these distinct failures or manufacture historical continuity.

## Sixteen-obligation coverage inventory

| Accepted ID | Design assessment at e7f721a |
| --- | --- |
| WB-browser-journey | Chain, completed result fixture, shared single-owner relation and no-write branch/fresh default present; fix filter race and assert UI provenance/ancestor identity |
| WB-browser-accessibility | Real keyboard inspection at 390/1440, three contrast classes and debug present; actual focus red; complete decision controls at both widths |
| WB-performance | Genuine missing metadata red; repair log/candidate oracle, isolate review/ref outcomes, invoke mapped AppTest helper, add refresh/definition/selected-only/parse observations |
| WB-latency-budget | Correct sample counts and warm numerical limits declared; persistence setup defect, insufficient cold/filter/result readiness, missing fixed cold assertion and real-pilot execution |
| UI-inspect | Canonical assertion/current-unavailable/historical/pass observations restored; add full selected case/revision provenance |
| UI-persist | Valid guarded choice/actor/rationale/Ready reload and resolved-route assertions present; observed missing resolved decision route is an accepted behavior failure |
| UI-conflict | Incomplete and spec-only stale rejection, published identity, refresh recovery and reload assertions present; observed resolved-route absence, no claim of final pass |
| UI-browser | Qualified E/U positive/missing/historical journey restored; post-edit identity/pointer/generation/definition no-write baseline fixed; add displayed full evidence tuple |
| UI-empty | No-task/no-scenario and empty-summary assertions pass independently at 109976c; passing run alone supplies no missing historical red |
| UI-gitless | Usable/lazy overview and actionable result reason retained; AppTest debug inspection missing |
| UI-decision-object | Overview link opens choice; passed independently at 109976c; add explicit blocked-task assertion |
| UI-overview-results | Overview no inspect, selected evidence, passed outcome and inspect commands present; explanation assertions reduced to labels; retain explanatory meaning as well as labels |
| UI-overview-hierarchy | Visible hierarchy/no hashes/no eager source then selected source checks present; require planned assertion text too |
| UI-test-source | Genuine source-missing red; fix wrong C1 oracle to P-001 canonical assertion |
| UI-expander-ids | Migration warning severity present; require actual repeated nested records and distinct control identities, not label uniqueness alone |
| UI-browser-gitless | Selected test/result, expanded debug, actionable reason and commands restored; current independent run reaches debug but content absent |

## Independent execution

All runs used immutable snapshots, Python 3.12, Streamlit 1.59.2, Playwright
1.63.0, PyYAML 6.0.3 and explicit installed Chrome channel (142.0.7444.162).
No browser assertions were monkeypatched for these runs.

* At **109976c**, browser discovery: **4 failures, 0 errors, 27.001s**.
  First failures: gitless expanded debug lacks Snapshot digest (line 224),
  UI-browser lacks Passed on E result (line 115), focus 2.305:1 (line 408),
  immediate summary enumeration returns empty (line 291).
  Log: `/tmp/ask-wb009-design-review-109976c-browser.log`.
* At **109976c**, ten AppTest cases plus mapped cache case and extra app-lazy
  helper test: **12 cases, 10 failures, 2 passes, 7.156s**, no errors.
  Passes: UI-empty and UI-decision-object. Failures preserve source/evidence,
  resolved-route, warning severity, metadata and selected-loading observations.
  Log: `/tmp/ask-wb009-design-review-109976c-app-cache.log`.
* At **109976c**, independently called actual benchmark structural helper at
  100 and 1,000 tasks. Projection/outline count assertions passed. Five projection
  samples were approximately 8–22ms / 792–916ms respectively, and outline samples
  approximately 1.3–1.5ms / 107–112ms. These are **projection-only diagnostics**,
  not browser, admission, selected loading, a real pilot or an SLA pass.
* At **e7f721a**, direct mapped latency test with persistent `/tmp` evidence dir:
  **1 failure, 0 errors, 5.796s**, missing output report at test line 237. Source
  audit identifies the nested-variable setup defect above; no browser latency
  measurement was established. Log:
  `/tmp/ask-wb009-design-review-e7f721a-latency.log`.

The fourteen mapped non-latency cases plus mapped performance case were inspected
at 109976c; the extra helper test is additional diagnostic execution, not another
accepted obligation. The latency run is separately bound to e7f721a. This report
does not present the mixed revisions as one all-sixteen candidate run. Original
WB-006–008 correction and historical red gaps remain in force.

## Handoff

Finish the enumerated design corrections while preserving genuine 109976c red
observations for bounded source/loading/focus repairs. Record fixture, setup,
oracle and actual behavior outcomes distinctly. Retain candidate-bound raw
benchmark reports and actual real-pilot/structural evidence, then obtain fresh
independent full candidate review after all sixteen mapped cases and required
visual checks. This report authorizes neither integration nor Accept.
