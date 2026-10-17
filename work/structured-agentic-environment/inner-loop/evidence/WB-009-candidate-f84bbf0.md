# WB-009 preliminary source/evidence candidate review

Verdict: **REJECTED / INCOMPLETE**, exact candidate
`f84bbf0c454a6e133b72ca95141abf9a509042d3`. Final browser/performance/pilot work
and refreshed candidate review are still required; this grants no integration
approval.

Reviewer `/root/review_wb009_tests`, independent child of `/root`; Codex runtime;
resolved review binding `gpt-6.1-sol`, high; parent model not supplied. Immutable
detached snapshot `/tmp/ask-wb009-candidate-review-f84bbf0`; no shared source edits
or commits. Authority is unchanged: accepted WB-009 handoff/plan/test plan,
canonical revision-3 specification, sixteen IDs, original six draft findings,
previous reports and session evidence correction. This continues the c9 report.

## Current findings and dispositions

1. **P1 — Explicit Evidence candidate workflow remains absent.** The active
   `streamlit_app.py` test/result branch supplies only source-context commit or
   current HEAD. There is no `Evidence candidate` control or equivalent explicit
   historical-candidate selection at this SHA. Old unused rendering helpers do
   not restore that workflow. Automatic prior-contract inspection is useful but
   cannot substitute for choosing a retained candidate while preserving current
   source selection. Bind candidate state to work/source/test, reset it on context
   changes, retain foreign-source read-only behavior, and independently verify the
   chosen candidate's exact retained evidence.

2. **P1 — Default historical detail now exposes raw provenance hashes.**
   `workbench_tests.py` historical-contract block renders candidate, source, spec
   and plan SHA strings directly in the default detail pane. The modified
   UI-inspect case explicitly requires the historical SHA there, replacing its
   former no-default-hashes assertion. This is not the previous AppTest hidden
   expander false red: these new fields are outside an expander. Keep the human
   historical outcome/current-contract disclaimer visible, put raw identifiers
   inside collapsed explanatory provenance controls, and separately test default
   visibility and expanded qualified identity. Preserve the no-default-hash
   observation when restoring historical-contract coverage.

3. **P2 — Working-source applicability must be distinct from Git-candidate
   currency.** The source regression is repaired: working-tree context now reads
   exact local bytes even when evidence candidate is pinned; captured Git context
   resolves its immutable commit. However `execution_history` compares source
   digests against the Git evidence candidate, not the displayed working bytes.
   Uncommitted source edits can therefore display alongside a row labelled
   `Source currency: current/historical` without explaining that the retained run
   did not execute those displayed bytes. Compare selected working-source digests
   for applicability or explicitly label currency as relative to the Git
   candidate and mark the working bytes unverified. The new mapped marker test
   verifies source content/status only, not this evidence consequence.

4. **P2 — Historical inspection only exposes completed passing old contracts.**
   `_historical_contract_evidence` uses canonical accepted-contract inspection
   and requires status `historical`, exact planned test/case/runner and matching
   historical test/case. This prevents an old contract from becoming current
   verification; that authority boundary is sound in the inspected happy path.
   But `inspect` uses `historical` status only for passing full completion; failed,
   invalid or unavailable prior-contract evidence is skipped entirely. Qualified
   failed historical executions and actionable invalid reasons remain useful
   records without granting completion. Preserve their authority/integrity
   diagnostics using retained historical contracts plus qualified history rather
   than silently equating history availability with full completion. Do not relax
   current plan-digest filtering. The helper also scans every ledger candidate and
   reevaluates whole workstreams when no current-contract history exists; actual
   pilot timings must account for this work honestly.

5. **P2 — Some provenance remains explicitly unavailable despite retained data.**
   The renderer no longer invents execution ID from artifact basename: it clearly
   says unavailable, and adds runner-validation description, phase/scope/task,
   source revision and artifact. That is honest and materially improves c9.
   Historical-contract records expose the canonical execution ID directly.
   Current-history runner is still drawn from selected plan metadata rather than
   a retained row field, and available actual failure detail/invalid completion
   errors are not comprehensively exposed. Keep available/missing field
   distinctions explicit; changing accepted domain ownership merely to surface
   a backend field would require coordinator handling rather than silently
   editing an unowned reader.

6. **P1 — Existing mapped-performance and benchmark gaps remain.** Actual
   app-lazy/reuse/refresh assertions are still in a separate unaccepted method;
   the mapped WB-performance case does not invoke them. Review mutation and
   same-mtime source mutation still lack reloaded authoritative outcomes beyond
   identity. Valid admitted 100/1,000-task app lazy/selected checks and real-pilot
   retained samples remain missing. The historical fixture repairs do not resolve
   browser duplicate/qualified outcome selectors or benchmark hardcoded fixture
   route/count assumptions. Keep all budgets, twenty warm sessions and five cold
   process restarts. Do not interpret this focused run as performance acceptance.

## Independent execution

Ran unmodified snapshot with pinned Python/Streamlit/Playwright environment:

```text
PYTHONPATH=_ask/tests:_ask/ui:_ask/scripts ASK_BROWSER_CHANNEL=chrome
/tmp/ask-wb009-venv/bin/python -m unittest
test_engineering_workbench_performance.WorkbenchTests.test_lazy_work_and_integrity_bound_cache_invalidation
test_engineering_workbench_performance.WorkbenchTests.test_overview_is_lazy_and_selected_details_are_cached
test_engineering_ui.UiIntegrationTests.test_historical_evidence_candidate_is_inspectable_without_being_current
test_engineering_ui.UiIntegrationTests.test_overview_loads_results_on_demand_and_explains_debug_identifiers -v
```

**4 cases, 3 pass, 1 assertion failure, 0 errors, 6.459s**. Log:
`/tmp/ask-wb009-candidate-review-f84bbf0-focused.log`. The mapped cache test reaches
and passes working-source marker, exact invalid-log state, plan-only historical
evidence, omitted/explicit candidate HEAD-key assertions, then fails the same
synthetic related-route import test described in c9. That test imports executable
app code without a fixture root; it does not establish a remaining central route
production defect. Extra app-lazy/refresh, historical-contract separation and
actual retained-result/provenance cases pass. Worker-reported 4/4 is not this
independent result. No fresh browser or full Verify run was performed here.

## All sixteen IDs and continuity

| Accepted ID | Observation / remaining coverage |
| --- | --- |
| WB-browser-journey | Not rerun; old-contract fallback changes outcome presentation, so full chain/foreign-source/no-write tail needs fresh execution. |
| WB-browser-accessibility | No thresholds or real keyboard assertions removed; 463f pass remains historical, not this candidate's run. |
| WB-performance | Focused assertion fail at synthetic related-route oracle; preceding genuine source/cache/integrity assertions pass; app/structural mapping incomplete. |
| WB-latency-budget | Not run; pilot/structural/readiness/report gaps remain. |
| UI-inspect | Focused pass for old-contract outcomes/disclaimer; changed fixture/expectation loses default no-hash observation. |
| UI-persist | Source retained; c9 independent pass not rerun. |
| UI-conflict | Source retained; c9 independent pass not rerun. |
| UI-browser | Fresh qualified outcomes/stale no-write/reload continuation still needed. |
| UI-empty | Source retained; c9 independent pass not rerun. |
| UI-gitless | Source retained; c9 independent pass not rerun. |
| UI-decision-object | Source retained; original explicit blocked-task assertion still absent. |
| UI-overview-results | Focused pass with source/phase/runner description and explicit unavailable execution ID; actual ID/failure-detail limits above. |
| UI-overview-hierarchy | Source retained; c9 independent pass not rerun. |
| UI-test-source | P-001 correction and real source assertion retained; c9 pass not rerun. |
| UI-expander-ids | Qualified two-control assertions retained; require both record values/identity and real duplicate nesting. |
| UI-browser-gitless | Fresh result-route/debug synchronization and exact actionable reason assertions still needed. |

The de993222 task red report is now retained with candidate/task/spec/plan/source
identities and all sixteen case IDs; reported aggregate 9 pass/7 fail/0 errors is
coordinator evidence, not an independently executed run here. New working-source
and pinned-HEAD assertions were committed before f84 production repair and are
present unchanged. Earlier genuine 109976c metadata/loading/focus and 463f
tampered-log observations remain valid; known setup/oracle/harness reds remain
qualified separately. No accepted IDs/pins/spec/contrast thresholds changed.
Production paths remain in the accepted WB-009 seams. Inspected captured-identity
edit guards and foreign-source read-only behavior were not weakened. No completed
independent foreign browser journey is claimed.

## Concrete performance guidance sent to the writer

Read-only `validate_current(snapshot_root, 'structured-agentic-environment')`
at this SHA returned no diagnostics. Metadata-only project/build_outline yields:

- Epic route `agent-workstream`; heading
  `Make agent-assisted engineering work explicit and reviewable`.
- Scenario route `representative-model-is-accepted`; heading
  `A representative model with canonical references validates`.
- Test/result routes `test:MV-valid` / `result:MV-valid`; case
  `test_engineering_model.ModelValidationTests.test_valid_broad_model_and_external_refs`;
  runner `engineering-model`.

Discover descriptors from actual admitted projection/outline rather than hardcode
the fixture. Derive filter IDs using `summary_records(projection)`. Precompute
qualified AST source snippet and actual retained result tuple/status outside the
timed interval; readiness waits selected route primary state plus matching
heading/source/assertion and actual qualified outcome or unavailable reason.
Select the requested Workstream before readiness because detached checkout
defaults can differ. Benchmark an exact disposable snapshot of real pilot bytes
and refs, recording original/snapshot input hashes and honest workload kind;
do not add synthetic story or passed evidence to the pilot.

For 100/1,000 tasks, create temporary complete canonical spec/markdown, test plan
with spec digest/obligations/runner/scenario/assertions, one-owner scopes, task
graph and actual representative source methods. Require validate/admit diagnostics
empty. Instrument real AppTest source/history/evidence paths before overview:
zero overview/metadata reads, exact bounded selected loading, unchanged reuse,
same-mtime source change with changed content/applicability, refresh revalidation
and stale edit guard. Invoke those helpers from the mapped accepted case. Record
actual documents/source files/bytes/nodes/edges/tasks/tests and distinct timing
samples; no large-fixture numerical SLA is assumed. Retain pilot raw samples and
all misses with candidate/environment/workload identities.

Final candidate-bound task result, full checks, honest retained pilot measurements
and independent final review remain outstanding.
