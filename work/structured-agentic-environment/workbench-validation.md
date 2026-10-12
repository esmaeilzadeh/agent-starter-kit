# WB-009 workbench validation

This file records candidate-bound evidence for WB-009. A browser or latency
result from one candidate does not establish another candidate's result.

## Browser journeys

The accepted browser cases remain mapped to their existing test IDs. The stale
decision journey verifies a linked-spec edit is rejected without changing the
published model, an explicit refresh captures the new inputs, and the valid
resolution persists with actor and rationale in a new browser session. The
workbench journey reads historical evidence, selected source, tasks and branch
snapshots, then confirms a read-only branch disables decision submission.

At candidate `ef4f78fa`, the exact 16-case WB-009 traceability run collected all
cases. Fifteen passed; `WB-latency-budget` failed on `source_result` p95 at
1058.8 ms against the 1000 ms limit. The browser journeys passed. The raw report
and runner output are retained under `traceability/runs/229be985...`.

At candidate `72da8f1f`, a separate workstream-wide run collected 58 cases. The
historical contract selector journey failed because its second selection used
an unstable keyboard interaction; the focused repair now selects the exact
visible option. The latency case still measured the synthetic fixture and
failed the overview budget. That run is retained under
`traceability/runs/fc0568...`; it is not a final WB-009 pass.

## Latency and structural workload

Latency acceptance now targets the admitted workstream
`structured-agentic-environment` and selected case `MV-valid`
(`test_engineering_model.ModelValidationTests.test_valid_broad_model_and_external_refs`).
It derives the scenario, source path and expected recorded outcomes from the
current model and retained history. The runner records the exact model/source
digests and a screenshot of the initial overview. Isolated consumer fixtures
remain useful diagnostics and are labeled synthetic.

A full 20-warm/5-cold real-pilot run completed against candidate `8bf82acc`.
Nearest-rank p95 was 1586.9 ms for overview (limit 1500 ms), 323.8 ms for
metadata navigation (limit 500 ms), 336.9 ms for filtering (limit 500 ms), and
1350.3 ms for selected source/result (limit 1000 ms). Cold starts ranged from
2334 to 2396 ms (limit 4000 ms). The overview and source/result budgets failed.
The raw report and actual overview screenshot are archived as
`traceability/real-pilot-8bf82ac.json` and
`traceability/real-pilot-8bf82ac.overview.png`.

The scale fixtures now contain admitted canonical model, task graph, test
scope, source files and test nodes. Both `validate_current` and `admit` must
succeed before projection timings are recorded. The 1000-task fixture contains
1000 tasks, 1000 tests, 2003 model nodes, 2002 model edges and 1000 source files.
In the archived 100/1,000 structural run, evidence-free projection took
73.8–79.9 ms / 9.74–13.16 s across five samples; outline construction took
1.4–2 ms / 102–145 ms. These large-fixture numbers are diagnostics, not an SLA.

Profiling `MV-valid` detail loading found that cache identity hashed 1668 files,
including generated publication blobs and static verification logs. Cache
identity now hashes the runtime evidence inputs used by this view: completion,
execution ledger, retained runs and reviews. The selected-detail integrity test
still proves that retained log and review edits invalidate the cache. A direct
call on the real pilot fell from 608 ms to 204 ms, with identity hashing falling
from 429 ms to 59 ms. The full browser run reduced selected source/result p95
from the earlier 1469.5 ms to 1350.3 ms, still above budget. Overview also
missed by 86.9 ms in the full sample.

## Verification state and remaining evidence

`./ask verify` on candidate `72da8f1f` passed the repository shell and
traceability checks when run with an isolated Git config. Its final candidate
check failed because the mapped test runner appended an execution record while
verification was checking the candidate source/CheckPlan for changes. The exact
run is archived under `traceability/static-runs/5555...` and the corresponding
traceability run above. This verification failure remains unresolved.

WB-009 is not complete. Remaining work is a passing 16-case WB-009 run on one
committed candidate, an independent final candidate review, and resolution or
explicit disposition of the remaining real-pilot budget misses and verification
immutability failure. Earlier WB-006–008 historical red gaps remain outside
this candidate's pass claim.
