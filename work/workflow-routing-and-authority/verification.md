# Verification results

Tested production candidate: `e7d7c19f9e34b93dc68e377f54dc1d4e4c21ba16`.
Evidence commits after that candidate only retain reports; they do not change the tested code.
Frozen kit authority remains `0e303265ceae1fbcdc9b2261bd922b003ab68924`.

## Functional checks

- `./ask verify`: **41/41 required checks pass** on the final candidate. Receipt:
  [checkplan-e7.json](evidence/checkplan-e7.json). This covers all 38 shell suites
  plus the three configured Python suites.
- Expanded discovery found **307 cases**. Run the two measured performance cases
  separately to avoid concurrent timing workloads; all 305 other cases executed.
  On `d25ce752`, the full run had 304 passes, one focus-contrast failure and no skips
  in 1,863.779 seconds. The failure reproduced independently twice at 1.168:1.
- The final focus repair passed all six revising-browser cases (73.428 s) and both
  engineering-workbench browser cases (99.568 s), including the failed case and
  both light/dark-control contrast journeys. The final structured performance
  module also passed its two functional lazy-loading/cache cases.
- No known functional test failures remain. The entire 305-case run was not
  repeated after the CSS/helper-only repair; affected browser cases and the full
  required CheckPlan were rerun at the final candidate.
- Independent reviews approved the process changes, cache/launcher changes, and
  final focus repair without outstanding findings. Retained reviews are in
  [evidence](evidence/).

## Remaining performance failures

Both measured performance tests still fail their existing budgets. Browser journeys
complete and assert their expected content, but timing assertions fail. This is
not an all-green expanded suite, and the workstream is not marked accepted.

Final measurements use Playwright 1.63.0, Streamlit 1.59.2, Python 3.10.12 and
bundled Chrome for Testing **153.0.8010.12**, with no other test suite running.
Interaction values are nearest-rank p95 across 20 samples. Every one of five
cold-start samples must meet its limit.

| Metric | Limit | Structured | Revising |
|---|---:|---:|---:|
| overview | 1500 ms | 777 ms | 569 ms |
| metadata_navigation | 500 ms | 441 ms | 224 ms |
| filter | 500 ms | 637 ms | 368 ms |
| source_result | 1000 ms | 1578 ms | 1635 ms |
| cold start (each sample) | 4,000 ms | 4339–5968 ms | 3902–4888 ms |

The earlier system-Chrome-134 runs also failed. Both original and bundled raw
reports are retained in `evidence/performance-*.json`; no thresholds were raised.
The repeated evidence fingerprint reads 440 / 2,029 files before cache lookup.
Its diagnostic timings were approximately 80–230 / 230–530 ms respectively;
these diagnostics were collected during verification, not as acceptance timings.
They identify repeated work but do not establish the full cold-start cause.
Remaining performance work is Results refresh cost and cold-start diagnosis.

## Reproduction and limits

Required checks: `./ask verify`. Expanded tests use unittest discovery over
`_ask/tests`; exclude only `test_measured_pilot_latency_budgets` and
`test_real_pilot_twenty_warm_five_cold_samples_respect_budgets` from the concurrent
functional run, then execute their modules separately with 20 warm / five cold
samples. Temporary Node 22.18.0 executes the Node-dependent cases without skips.
The final browser comparison sets `ASK_BROWSER_CHANNEL` to an empty value and
`PLAYWRIGHT_CHROMIUM_EXECUTABLE` to the installed bundled executable.

Use independent full-history checkouts, matching `agent/<work-id>` branches for
working-pilot timings, the original retained ledger bytes documented in
[repair.md](repair.md), and a separate runtime output root. Do not export a broad
`PYTHONPATH` into nested worktree checks. Preserve the pilot's tracked admission
pointer across benchmark execution. Raw log paths and SHA-256 values are retained
in `evidence/log-digests.json`.

No live provider calls, publication, merge, release or push was performed.
Standby is requested after these results and local commits are saved.
