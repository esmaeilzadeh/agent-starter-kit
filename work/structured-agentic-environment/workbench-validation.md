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

A one-warm/one-cold real-pilot smoke sample on the workstream model completed
against candidate `72da8f1f`: overview 1628.9 ms, metadata navigation 263.9 ms,
filter 300.9 ms, selected source/result 1375.9 ms, and cold start 2383.9 ms.
These single samples are diagnostic only and exceed the overview and
source/result budgets. The required 20 warm/5 cold real-pilot run is still
needed for acceptance.

The scale fixtures now contain admitted canonical model, task graph, test
scope, source files and test nodes. Both `validate_current` and `admit` must
succeed before projection timings are recorded. The 1000-task fixture contains
1000 tasks, 1000 tests, 2003 model nodes, 2002 model edges and 1000 source files.
Its measured evidence-free projection took 10.36–13.34 seconds across five
samples; outline construction took 108–117 ms. These large-fixture numbers are
diagnostics, not an SLA. The required full candidate run will archive its raw
structural measurements.

Profiling `MV-valid` detail loading found that cache identity hashed 1668 files,
including generated publication blobs and static verification logs. Cache
identity now hashes the runtime evidence inputs used by this view: completion,
execution ledger, retained runs and reviews. The selected-detail integrity test
still proves that retained log and review edits invalidate the cache. A direct
call on the real pilot fell from 608 ms to 204 ms, with identity hashing falling
from 429 ms to 59 ms. The full browser measurement must confirm the practical
effect.

## Verification state and remaining evidence

`./ask verify` on candidate `72da8f1f` passed the repository shell and
traceability checks when run with an isolated Git config. Its final candidate
check failed because the mapped test runner appended an execution record while
verification was checking the candidate source/CheckPlan for changes. The exact
run is archived under `traceability/static-runs/5555...` and the corresponding
traceability run above. This verification failure remains unresolved.

WB-009 is not complete. Remaining work is the exact 20-warm/5-cold real-pilot
measurement, a passing 16-case WB-009 run on one committed candidate, an
independent final candidate review, and resolution or explicit disposition of
the verification immutability failure. Earlier WB-006–008 historical red gaps
remain outside this candidate's pass claim.
