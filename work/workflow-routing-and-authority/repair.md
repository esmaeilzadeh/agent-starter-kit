# Workflow verification repairs

## Authorization and route

Bug-fix continuation of `fix/workflow-routing-and-authority`. The human asked to
run all tests and check the flows, then explicitly requested: “do bug fixes with
kit enabled bug fix flow”. Preserve existing contracts and approval boundaries;
do not change product expectations to make checks pass.

## Frozen kit authority

Dogfooding enabled for these remaining repairs using commit
`0e303265ceae1fbcdc9b2261bd922b003ab68924` at
`/home/mohamad/Projects/UNI/ai-agent-start-kit-dogfood-0e303265`.
That detached checkout was verified clean. Keep this pin and copy unchanged.
Its workflow policy's reproduced-bug path governs diagnosis, repair, independent
review and verification. This working checkout remains the product under test.
No feature spec/plan or TaskGraph is adopted for this focused repair.

## Initial evidence

- At `36c12c062415e68931495005005e6f609ec5b55c`, all 41 repository CheckPlan
  checks passed using temporary Node 22.18.0 (including previously skipped cases).
- Expanded Python discovery on independent baseline `4c525115` ran 302 cases:
  20 failures and 4 errors. Log: `/tmp/ask-all-python.log`.
- The missing runner-adapter fixture failure is already repaired in `c384f72a`.
- Some browser/benchmark checks modified tracked evidence in that disposable
  checkout; later checks correctly refused dirty candidate provenance.
- Remaining failures require individual reproduction before any repair. Distinguish
  product defects, stale/incomplete fixtures, process-global test contamination,
  missing retained evidence and environment failures. Never weaken authority,
  provenance or isolation guards to obtain green results.

## Completion evidence

Pending focused reproductions, minimal repairs, independent review, and final
repository verification plus expanded test results at the resulting commit.

## Repairs and diagnosis

- Committed-source UI reads failed canonical validation because their Snapshot
  omitted decoded documents. Normalize each captured JSON record and retain its
  documents/references; malformed inputs still fail closed. Existing committed
  source, navigation and decision regressions now pass.
- Keyboard focus used a white outline against the light surface. Retain the
  contrasting teal outer shadow and use a black outline; verify both browser
  contrast journeys, including historical results.
- Provenance CLI fixtures omitted the clean checker's Python package. Restore
  the real dependency and keep dirty-source rejection assertions.
- Client-write fixtures now preserve a real client hook alongside exactly one
  kit hook; the injected installer interruption waits up to the fixture's
  existing 60-second operation allowance. Intervening edits still refuse recovery.
- Passage-admission fixtures now include model bindings and retain review bytes
  under the documented inner-loop evidence directory. Assertions distinguish the
  verified source commit from its later progress-publication commit.
- Lazy-detail checks follow the existing Results boundary and use the full
  captured test identity; source-only navigation must not inspect execution.
- The real-pilot benchmark updates a tracked admission-cache pointer. Restore
  its exact pre-test bytes with unittest cleanup, including after failed checks.
- Real inventory profiling found 100 Git subprocesses per refresh. Cache only
  model presence keyed by repository and immutable commit IDs; resolve refs,
  ancestry (one Git batch) and local cards anew. Never cache transient read errors. Regression: unchanged inventory reuses
  facts while moved refs, removed/restored models and merges remain visible.
  Real-repository baseline: 100 calls / 398 ms per refresh. Final measurements:
  65 calls / 233 ms cold; 8 calls / 29 ms warm.

## Verification fixture provenance

The historical execution ledger was removed from tracking by `24473ca4` and is
absent locally. Restore its original bytes only in disposable test fixtures:
`d21dfcc2cca1ebbacee5c7de4025b0d85e4e518a:work/structured-agentic-environment/traceability/executions.json`,
SHA-256 `b5ce6be822ee7903442b9695ae8585bac2e324046c6ae1b933c21f38cc5451a2`
(142 original rows, including the authority-checked WB-003 run). Do not synthesize
execution results. Keep browser output outside the candidate. Avoid exporting test
import paths into nested worktree tests. Measure each real working-tree pilot
from its matching workstream branch; the harness otherwise first loads a committed
source before selecting the working source. Preserve the original latency limits.
