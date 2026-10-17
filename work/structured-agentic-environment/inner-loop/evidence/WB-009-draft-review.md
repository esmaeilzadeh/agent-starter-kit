# WB-009 preliminary draft review

Verdict: **NOT APPROVED / INCOMPLETE**. This is an attributable test-design and
handoff report, not a candidate integration or workstream completion decision.

Reviewer: `/root/review_wb009_amendment` (independent child agent, Codex runtime).
Reviewed checkout HEAD: `1abf6237bea49f95c5abb74898de55b90e541f3d`, together with
the uncommitted drafts identified below. These hashes identify the actual bytes
inspected; a later checkpoint commit may include additional changes and requires
fresh candidate-bound review.

| Uncommitted draft | SHA-256 |
| --- | --- |
| `_ask/tests/test_engineering_ui_browser.py` | `b55d57660aacd3a56d8a67d427c4d60269b0775834f4575d586245fed4897e4a` |
| `_ask/tests/test_engineering_workbench_browser.py` | `290325efe3fd60abbebd52aeabafdaef70d4bc1a3c18704cd271eb90450cfe2e` |
| `_ask/tests/test_engineering_workbench_performance.py` | `b1d3964396e018740b791dd2fe57b2ec3f039664ed081b1a1db187924d5e037d` |
| `_ask/ui/benchmark_workbench.py` | `a625432e3e1f3d2ab47ac3ebf77d10a38d0061ffb8eafbf918d1a6f405020d0c` |
| `_ask/ui/workbench_loading.py` | `ea040ed3df1d832e57b382e362fcc8d6ad8c7a5a6e1bcc126b3b94236e3d9e91` |

Scope: compare the accepted WB-009 obligations and specification revision 3 with
the draft browser, performance and loading checks. Source was read and selected
draft changes were reread before this report. **No tests, browser journeys,
screenshots, benchmarks or final Verify were executed by this reviewer for these
drafts.** There is no independent approval of their red/green history or production
implementation. Earlier coordinator-reported runs are not this reviewer's runs.

## Open findings

1. **Required browser hierarchy and branch journey is incomplete.**
   `_ask/tests/test_engineering_workbench_browser.py:56` uses `evidence_workbench()`
   and navigates scenario → test → result. That fixture has no recorded story for
   this journey, and the case does not traverse a completed task, summary filters,
   a second branch or a new-session default-work selection. Inspecting a historical
   evidence candidate is not cross-branch source selection. HEAD/refs/model-byte
   comparisons surround no actual foreign-source interaction, and a filename plus
   “historical” does not establish qualified source/result identity. For
   `WB-browser-journey`, construct the required story/task/shared-test/second-branch
   data, traverse the full connected chain and exact summary record sets, verify
   chosen source and actual outcome identity, attempt or establish disabled foreign
   edits, compare checkout/refs/files afterward, and verify current-work default in
   a fresh browser context.

2. **Accessibility coverage does not establish the accepted journey.**
   `_ask/tests/test_engineering_workbench_browser.py:87` tests only 390px.
   Programmatic `focus()` followed by mouse clicks is not keyboard navigation.
   The case does not inspect task/source/debug, exercise both widths, assert
   non-color status text or reload the choice/task consequence in another session.
   `select_option()` at line 107 targets a native HTML select API, whereas Streamlit
   renders a custom combobox. Normal-text contrast for one route does not establish
   large-text contrast or focus-indicator contrast; outline/shadow presence alone
   is insufficient. Exercise actual keyboard controls at 390px and 1440px, confirm
   labels and visible focus throughout the primary journey, measure rendered normal
   text ≥4.5:1, large text ≥3:1 and focus ≥3:1 against resolved adjacent backgrounds,
   inspect source/debug, and verify attributed choice plus unblocked task after a
   fresh session. Transparent backgrounds need ancestor/compositing handling in
   contrast calculations.

3. **Legacy browser migration loses evidence and task-consequence assertions.**
   `_ask/tests/test_engineering_ui_browser.py:69` creates historical evidence but
   does not inspect it or missing evidence in the stale/persistence case. Canonical
   assertions/provenance and the derived unblocked task must remain observable;
   the new browser session currently checks actor/rationale only. Preserve the
   historical/missing evidence inspection before the decision journey and inspect
   the task consequence after reload. No-write rejection should compare published
   model/definition state around the stale submission, not only decision lifecycle
   and history.

4. **Cache checks do not verify application laziness, selected loading or integrity
   consequences.** `_ask/tests/test_engineering_workbench_performance.py:30`
   projects metadata and checks that a newly created local cache is empty; it never
   runs the app overview with source/evidence counters or metadata-navigation
   revisits. Its line-38 fallback to canonical test-plan data hides a missing
   projection test record. Require the actual projection metadata, instrument the
   application paths to prove zero overview source/evidence work, selected-only
   detail loading, unchanged metadata reuse and refresh behavior. Mutating an
   arbitrary `selected-cache-probe.json` and checking a key difference does not
   prove that real retained logs, review records or accepted refs invalidate
   authoritative displayed evidence. Mutate those actual inputs, reload through
   the cache, assert changed/invalid/unavailable evidence as appropriate, and
   confirm admission/guard checks remain active. Source mutation is conditional
   and can silently perform no check; use a guaranteed source. The “same-mtime”
   claim does not restore mtime; set it explicitly when testing that counterexample.

5. **Required structural workloads and retained benchmark evidence are absent.**
   The performance case does not construct 100-task or 1,000-task fixtures or
   report their graph/test/file sizes and timing. The latency test calls `run()`
   and checks its in-memory result, but does not save candidate-bound raw samples
   and environment. The CLI's optional output argument is not exercised by this
   case. Build the deterministic structural fixtures and retain raw pilot and
   structural reports with exact candidate/workload identity. Source hashes should
   cover the relevant repaired modules; recording a subset must not imply complete
   source identity. Fixture and real-pilot benchmark evidence must be labeled
   accurately.

6. **Warm overview timing is overwritten and metadata navigation has the wrong
   limit.** `_ask/ui/benchmark_workbench.py:137` assigns initial overview time to
   `navigation`, then line 140 overwrites it with scenario-navigation time. The
   reported `navigation` limit remains 1500ms, although metadata navigation/filter
   must meet 500ms. Retain separate overview, metadata-navigation/filter and selected
   source/result samples with respective p95 limits 1500/500/1000ms. Readiness must
   establish the requested route and its content, not merely a changed render serial.
   Selecting an already-selected “All” option may not cause a rerun; measure a real
   changed filter. Preserve five full cold starts ≤4000ms and 20 warm sessions.

## Earlier feedback and observed draft corrections

The initial feedback also identified a warm loop that restarted the server for
every sample, silent no-op route selection, incorrect model-size accounting and
a stale test that revised the model's purpose title. Those exact issues have
received source corrections in the hashed drafts: the warm loop now shares one
server, missing route selection raises, `digest_tree()` uses its supplied root
and separates model/code byte maps, and the legacy stale change uses an empty
command list with linked spec/plan file changes. Its combobox helper also replaces
the earlier native-select call in that legacy module. These corrections have not
been executed or approved here. The new accessibility case still uses
`select_option()`, and the open coverage findings above remain.

## Prior plan decisions are separate

This reviewer approved only the exact hierarchy compatibility contract at
`291db209c9af2e8c5335b2c9233ee8f826bfad11` and repair ownership amendment at
`1898b635e67d50056cb7006d27037dfc84358970`. Their attributable JSON records are
`traceability/wb009-hierarchy-plan-review.json` and
`traceability/wb009-repair-ownership-plan-review.json` under this workstream.
Those approvals preserve all 57 IDs and 16 WB-009 assignments and authorize the
reviewed sequential ownership. They do not approve this draft implementation,
execution evidence, TDD continuity or completion. The six migrated regression
cases are explicitly `changed` and require genuine assertion-red/final-green
continuity; selector migration is not an exemption.

The earlier WB-006–WB-008 approval/TDD claims remain withdrawn as documented in
`inner-loop/evidence/session-evidence-correction.md`. This report does not restore
them. Dark mode and verification-tooling work remain outside WB-009.

## Handoff

Preserve this report with the draft checkpoint for transfer. Address the findings
without removing accepted assertions, capture genuine behavior-red evidence before
production changes, then complete and execute all 16 WB-009 cases, required real
browser/visual checkpoints and benchmarks. Request independent review bound to
the eventual exact committed candidate and actual test/evidence bytes. Record
partial/incomplete status honestly until the remaining requirements and evidence
are satisfied. This reviewer has not committed or pushed any files.
