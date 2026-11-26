# Read-only performance diagnosis: candidate `d25ce752`

- Candidate: `d25ce7527181ca401a2576955f2ab53323eb8a06`
- Requested/resolved reviewer model: `gpt-6-luna` (frozen resolver selection)
- Self-reported backend identity: unavailable
- Runtime: Codex
- Parent model: GPT-6
- Scope: supplied WB-009 and RWB-109 benchmark reports plus benchmark/detail-loading code
- Verdict: **Evidence supports real repeated product work on the warm Results path; cold-start attribution is inconclusive. The benchmark flow itself does not appear invalid.**

## Evidence and diagnosis

Both supplied runs fail the unchanged budgets. WB-009 has source/result p95 1,418.6 ms, filter p95 582.7 ms, and cold samples 4,866–7,238 ms. RWB-109 has source/result p95 1,556.7 ms and cold samples 4,670–5,421 ms; filter p95 is 408.1 ms. Both current reports used Playwright 1.63 / Streamlit 1.59.2, but selected system Chrome 134 on Linux 6 / Python 3.10.12.

There is a concrete repeated cost on the warm Results path. `load_selected_detail` computes `detail_identity` before checking its session cache. When `include_evidence=True`, that identity calls `_traceability_fingerprint`, which recursively visits and reads/hashes every file under `traceability/runs` and `traceability/reviews`, plus the completion and execution ledger. The supplied model roots contain 440 files / 3.17 MB for the structured pilot and 2,029 files / 1.29 MB for the revising pilot in that fingerprint scope. The benchmark repeats the Test → Results flow 20 times, so it repeats this scan even after the detail payload is cached. This is valid freshness work, but the current implementation pays the full directory scan on each Results navigation. The measured `source_result` interval also includes both route transitions and all visible historical-output assertions, so it is an end-to-end Test → Results journey rather than isolated source rendering.

The high source/result time predates this candidate. Retained reference WB-009 candidate `8bf82ac` has p95 1,350.3 ms; retained RWB-109 candidate `68a1cea` has p95 1,593.0 ms. Both exceed the unchanged 1,000 ms limit. Current measurements are in the same range, so the evidence does not show that this repair caused a regression. It does show an existing performance-budget miss and a concrete scan that can be profiled/optimized while preserving cache invalidation and evidence validation.

Cold measurements are valid end-to-end startup-to-ready samples: the harness timestamps before starting Streamlit and waits for the selected workbench UI to be ready. They are not an invalid synthetic assumption. However, the current runs are not directly comparable to the retained environment: the forced `ASK_BROWSER_CHANNEL=chrome` chose system Chrome 134 even though Playwright’s bundled Chrome for Testing 153.0.8010.12 is installed; Python, kernel, and glibc also differ from retained references. An older WB-009 reference on Python 3.12 / Linux 7 / Chrome 142 reports cold samples around 2.33–2.40 s, but it predates substantial UI changes. Do not infer a cold-start regression or a pass against the current 4,000 ms budget from these cross-environment comparisons. Standardized measurement is needed after the active suites finish.

The benchmark’s `source_result` name can be clearer because it includes Test navigation plus Results navigation and evidence rendering. Its assertions nevertheless measure a real user flow. I found no basis to dismiss the failures as harness artifacts. Reports do not include per-function timings, so the exact contribution of the fingerprint scan versus evidence evaluation, Streamlit reruns, and browser rendering remains unmeasured.

## Limits

I inspected existing JSON reports and source only. I did not run tests, start servers, or repeat timings while suites were active. No budgets or product behavior were changed. This diagnosis does not claim the pending CheckPlan or expanded suite passed.
