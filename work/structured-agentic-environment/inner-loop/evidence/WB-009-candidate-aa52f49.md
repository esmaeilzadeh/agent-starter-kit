# WB-009 preliminary applicability/candidate review

Verdict: **REJECTED / INCOMPLETE**, exact SHA
`aa52f4942e982fd24e4da81ebb555c5f984914be`. This is a bounded preliminary audit,
not final task integration approval. Browser changes still under construction
were not inspected or executed.

Reviewer `/root/review_wb009_tests`, independent child of `/root`; Codex runtime;
resolved reviewer binding `gpt-6.1-sol`, high; parent model not supplied. Detached
snapshot `/tmp/ask-wb009-candidate-review-aa52f49`. No shared production/test edits
or commits. Same accepted revision-3 authority, sixteen IDs, ownership, original
six draft findings, previous reports and evidence correction apply.

## Material findings

1. **P1 — Applicability hashes only one accepted source file.**
   `workbench_loading._source_file_digest` selects the module-matching test file
   and ignores other accepted `source_paths`. Whole-file hashing correctly detects
   an import/helper edit inside that file, but not a separate accepted dependency.
   This matters on the actual pilot, where accepted tests declare both their test
   module and `engineering_fixture.py`.

   Independent exploratory diagnostic constructed a disposable Consumer with
   `source_paths=['test_app.py','app.py']` in its accepted plan before recording
   runs. The exact U final-green row had valid output and matching source. Changing
   accepted helper `app.py` from uppercase behavior to `return value.lower()` kept
   the selected method snippet unchanged and changed the cache identity. Reload
   still reported `working_source_applicability='matches selected source'` with
   valid retained output. This is a genuine source applicability defect, not the
   known synthetic route-test failure. Compare complete path→digest maps for all
   accepted files, using confined working bytes or immutable Git blobs according
   to context; missing/unsafe/unreadable paths make applicability unavailable.
   Preserve the separate selected snippet used for presentation.

   Diagnostic script/log:
   `/tmp/ask-wb009-candidate-review-aa52f49-helper-diagnostic.py` and `.log`.
   The fixture was adapted externally before acceptance/runs; application source
   was unmodified. This is supplemental diagnostic evidence, not an accepted
   mapped task run.

2. **P2 — Explicit historical inspection hides authority/integrity failures.**
   `_historical_contract_evidence` skips all statuses except `historical`.
   `inspect_historical_contract_candidate` therefore returns an empty list for
   invalid/tampered, unavailable or incomplete old-contract evidence as well as
   genuinely unmatched selected identity. The renderer tells the user no outcome
   matches the exact selected identity. Return a structured status/diagnostic plus
   qualified records, so a selected invalid candidate explains its real integrity
   or authority failure. Retain exact accepted test/case/runner checks and the
   no-current-contract-verification disclaimer. Failed historical executions
   should remain inspectable without claiming complete workstream verification.

3. **P2 — Candidate workflow is conditional and state-isolation assertions are
   still missing.** A lazy explicit Historical contract candidate/Inspect candidate
   workflow now exists, hides hashes until inspection, and evaluates only the
   chosen retained candidate. Its session keys use detail identity and selected
   candidate; that identity incorporates work, test, source context, HEAD, refs
   and evidence bytes. No foreign write or edit-guard bypass was found in the
   inspected wiring. However the control is supplied only when current-contract
   history has no rows; it does not provide general explicit candidate selection
   when current-contract rows already exist. Test switching test/work/source and
   selected candidate before/after inspection, foreign read-only behavior,
   evidence/ref invalidation and refresh independently. Existing UI-inspect covers
   only one matching old-contract selection and human outcome disclosure.

4. **P1 — Accepted performance/structural/pilot gaps remain unchanged.** The
   mapped case now covers current Git evidence separately from working-source
   applicability, including an unchanged selected method with a changed import
   inside its module. It still does not invoke the separate real app lazy/reuse/
   refresh method. Review mutation still checks only identity; structural
   100/1,000-task fixtures are not admitted real-app lazy/selected workloads.
   Real-pilot raw benchmark results remain absent, and immutable browser/harness
   sources still need qualified outcome/readiness corrections. Retain all
   sixteen IDs, fixed budgets, twenty warm/five cold samples and prior guidance.

## Independently verified repairs

- Working-tree source uses actual local bytes; captured Git source remains
  revision-bound. Cache identity includes explicit selected candidate and current
  HEAD separately. Existing regression assertions remain.
- Selected module full-file digest detects import-only changes even when AST
  method snippet is unchanged. Git candidate currency is explicitly separated
  from working/selected-source applicability. Finding 1 limits the completeness
  of that repair.
- Default old-contract panel no longer prints raw candidate hashes before an
  explicit Inspect action. UI-inspect restores both preselection and selected-
  but-uninspected no-hash assertions, then requires the exact historical candidate
  after inspection. This repairs f84's default-hash regression without removing
  attribution or the current-contract disclaimer.
- Automatic full history scanning was removed from ordinary selected detail;
  candidate inventory reads ledger identities only, explicit inspection filters
  to the chosen candidate. Current source selection does not change when choosing
  historical evidence.
- The ten migrated AppTests independently pass, including persistence, stale
  rejection/refresh, Gitless usability, source content, real retained-result
  provenance and repeated execution controls. Their earlier residual coverage
  limits remain: explicit blocked-task observation and nested record value
  identity need stronger assertions.

## Independent execution

Unmodified immutable source, pinned environment:

```text
PYTHONPATH=_ask/tests:_ask/ui:_ask/scripts ASK_BROWSER_CHANNEL=chrome
/tmp/ask-wb009-venv/bin/python -m unittest
test_engineering_workbench_performance.WorkbenchTests.test_lazy_work_and_integrity_bound_cache_invalidation
test_engineering_ui -v
```

Result: **11 accepted cases, 10 pass, 1 assertion failure, 0 errors, 8.434s**.
Log `/tmp/ask-wb009-candidate-review-aa52f49-focused.log`.
The mapped case passes source/applicability/integrity/HEAD observations, then
fails its synthetic shared-route test as at c9/f84: importing executable
`streamlit_app` without a fixture root can stop before installing the supplied
projection. Source central route authority remains repaired. This failure is
qualified as an oracle/environment issue, not proof of a production route defect.
Worker-reported mapped 1/1 is not the independent result. No browser, latency,
full Verify or accepted full task-run execution was performed here.

## Sixteen-ID continuity

| Accepted ID | This audit / remaining observation |
| --- | --- |
| WB-browser-journey | Not rerun; foreign source/result authority and no-write tail need immutable refreshed browser execution. |
| WB-browser-accessibility | Keyboard/contrast thresholds retained; 463f independent pass remains historical only. |
| WB-performance | Independent synthetic-route assertion fail after current-source/module-applicability/cache observations pass; separate accepted-helper and multi-file gap. |
| WB-latency-budget | Not run; admitted structural work, pilot/raw readiness and report obligations remain. |
| UI-inspect | Independent pass for explicit old-contract inspection, preinspect hidden hashes and historical identity/disclaimer. |
| UI-persist | Independent pass. |
| UI-conflict | Independent pass. |
| UI-browser | Immutable source not rerun; qualified duplicate outcomes, stale no-write/reload tail still required. |
| UI-empty | Independent pass. |
| UI-gitless | Independent pass. |
| UI-decision-object | Independent pass; original explicit blocked-task assertion still missing. |
| UI-overview-results | Independent pass; prior actual execution-ID/failure-detail limitations remain explicit. |
| UI-overview-hierarchy | Independent pass. |
| UI-test-source | Independent pass, canonical P-001 and actual code/assertion retained. |
| UI-expander-ids | Independent pass for two distinct controls; both repeated values/qualified identities should be asserted. |
| UI-browser-gitless | Immutable source not rerun; actual result-route/debug readiness still requires fresh check. |

The retained 9b59ecd red task artifacts contain sixteen mapped case identities and
candidate/task/spec/plan/runner/source authority; reported 10 pass/6 fail/0 errors
is coordinator evidence, not this reviewer's execution. The added current-source
and same-module helper/import applicability assertions precede this production
repair and remain intact. The new independent separate-file counterexample
requires its own committed regression before a bounded fix. Preserve earlier
109976c and 463f genuine red observations, while keeping known selector/import/
fixture/harness failures qualified. No accepted pin/spec/ID/contrast-threshold
change was observed. AppTest source paths remain in accepted WB-009 ownership;
report/traceability additions are attributable evidence for coordinator handling.

Full selected-candidate negative/state tests, all-sixteen current-candidate browser
and performance results, real-pilot measurements and final independent review
remain outstanding. No integration approval is granted.
