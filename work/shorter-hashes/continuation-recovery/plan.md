# Plan: durable continuation and task evidence recovery

Status: **SUPERSEDED AS A PLANNING DRAFT**. This draft's R1–R4 design gaps
were resolved in the separately reviewed and accepted
`work/continuation-recovery/plan.md` (revision 13); its result records CR-1
through CR-4 integrated. That workstream stopped before product adoption or
scheduling. Keep this draft and its original review findings as history.

The newly authorized product-history reconciliation is scoped by
`execution-authorization.md`; its current product preimage and non-mutating
adoption proposal are `current-audit.json` and `current-proposal.json`. This
step records evidence only and does not advance product task state.

Requirements baseline: `spec-change.md` in this directory, criteria CR-01–CR-08.
Authorization and explicit stop: `../continuation-recovery-authorization.md`.

## Endpoint

Prepare and independently review this plan, its task graph and test mapping,
commit the artifacts, then stop. Do not initialize a repair writer, change the
active product contract, repair runtime state or resume `shorter-hashes` now.
This plan describes future execution after an explicit direction supersedes the
stop and the proposed interrupt contract receives the required approval/review.

## Design

Use `_ask/scripts/inner_loop/checkpoint.py` for immutable checkpoint publication
and `_ask/scripts/inner_loop/recovery.py` for reconciliation. Keep state.py's
public lifecycle API; checkpoint reads/writes are its persistence boundary.

Each checkpoint is a Git commit under `refs/ask/inner-loop/<work-id>`, parented
by the preceding checkpoint, with versioned JSON state/manifest and the required
artifact blobs. The manifest contains the original initialization/source anchor,
current source context, attempt identities, accepted spec/test-plan/TaskGraph
identities and authority pins, state generation, artifact paths and digests.
Checkpoint commits are records, not implementation candidates or approval refs.
Parse them as data; never execute code loaded from a checkpoint.

Capture the transitive evidence required to revalidate the recorded milestones:
TaskResult, actual run records and referenced logs, Refactor outcome, independent
review records/artifacts and integration reports/logs. Validate relative paths,
schema and digests; reject traversal, symlinks escaping the repository, missing
objects and unsupported records. Capture only declared evidence closure, not
arbitrary runtime scratch trees. Tests cover loss of the entire ignored cache.

Under the existing coordinator lock: validate observed checkpoint generation and
contract, create immutable objects, CAS-publish the checkpoint ref, then atomically
replace the worktree state cache. A failed publication cannot advance state.
After publication, a cache-write failure leaves a replayable checkpoint. Treat
checkpoint ref drift as conflict, not a retry that overwrites another writer.
Specify one lock order before connecting traceability/reference publication;
test cross-process contention rather than nesting locks opportunistically.

`run`/`resume` reconcile before selecting tasks. A validated checkpoint can
restore its exact missing/older cache and artifacts. Any different contract,
attempt, unexplained newer cache, incompatible Git context or conflicting
evidence returns `recovery_required`. It never chooses a new base merely because
state is missing. Status reports separate execution milestones from integration.

For legacy repositories without checkpoints, inspect retained results, task
branches, run/review records and committed runtime snapshots. For an apparently
fresh state, inspect owned-path changes since the original accepted task-contract
anchor; ambiguous post-anchor implementation changes require reconciliation.
Source presence or those changes are suspicion, not completion evidence. Preserve
the original anchor across amendments so a later acceptance does not erase this
history. A truly new workstream at its initialization anchor remains startable.
An explicit reviewed legacy adoption record selects original attempts and states
which evidence applies; it cannot create missing approval or integration.

Record real Red and Green checkpoints at run publication time, not only when a
TaskResult is eventually written. Record Refactor, review and integration before
reporting each transition complete. Evidence failure leaves the prior valid
checkpoint and a diagnosable unfinished transition. Add interrupted-finalization
recovery where evidence was written but checkpoint publication did not finish.

## Work breakdown

All tasks are serial on the existing branch; no second related workstream.
Task IDs below are supplemental proposal IDs, not yet in the active graph.
`tasks.yaml` and `test-plan.json` in this directory have the same ownership and
case mapping. Merge them into one reviewed executable contract before execution;
do not register this draft as if the active ten-task graph already contains them.

| Task | Outcome | Depends on | Owned paths | Tests | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| CR-1 | Reconcile missing/stale/pending state before writer admission; diagnose legacy evidence without discarding it | none | `_ask/scripts/inner_loop/recovery.py`; `_ask/scripts/inner_loop/driver.py`; `_ask/scripts/inner_loop/state.py`; `_ask/scripts/inner_loop/__main__.py`; `_ask/tests/inner_loop_recovery.py`; `_ask/tests/test-inner-loop-recovery.sh` | CR-T01–CR-T04 | Immutable behavior Red/Green at public scheduling entry points; unchanged state/ref on conflicts; independent exact-candidate review; normal verification/integration |
| CR-2 | Publish durable checkpoints and replay validated evidence after cache loss | CR-1 | `_ask/scripts/inner_loop/checkpoint.py`; `_ask/scripts/inner_loop/state.py`; `_ask/scripts/inner_loop/recovery.py`; `_ask/tests/inner_loop_recovery.py` | CR-T05–CR-T09 | Process-interruption and CAS assertions, restored artifact byte equality, Red/Green, explicit Refactor result, independent review and normal integration |
| CR-3 | Capture each execution milestone and enforce guarded recovery across CLI and generic state mutations | CR-2 | `_ask/scripts/inner_loop/evidence.py`; `_ask/scripts/inner_loop/state.py`; `_ask/scripts/inner_loop/driver.py`; `_ask/scripts/inner_loop/recovery.py`; `_ask/scripts/inner_loop/__main__.py`; `.agents/ask/verification/traceability/adapters.py`; `.agents/ask/verification/traceability/cli.py`; `_ask/tests/inner_loop_recovery.py`; `.agents/ask/task-loop.md`; `.agents/ask/stages/06-implement.md`; `_ask/docs/inner-loop-evidence.md`; `_ask/policies/workflow.md`; `AGENTS.md`; generated binding projections from `./ask sync` | CR-T10–CR-T14 | Real executed run checkpoint assertions; no synthetic milestone promotion; interruption/contract-drift tests; existing protocol regressions; exact-candidate independent review and normal integration |
| CR-4 | Reconcile this workstream's old attempts, retain valid Red/Green, and prepare its exact next task step | CR-3 | `_ask/tests/inner_loop_recovery.py`; `work/shorter-hashes/continuation-recovery/**`; `work/shorter-hashes/inner-loop/{state.json,results/**,evidence/**}`; `work/shorter-hashes/traceability/**`; reviewed amendments to `work/shorter-hashes/{plan.md,test-plan.json,inner-loop/tasks.yaml,traceability-accepted.json}` only where evidence requires them | CR-T15–CR-T16 | Read-only inventory first, reviewed evidence applicability/adoption record, explicit unmet milestones, verified checkpoint export/reload; no fabricated integration or automatic product scheduling |

Tasks share persistence/scheduler/test files and therefore form a linear graph.
CR-4 repairs operational evidence, not a new product feature; its fixture tests
and actual audited report establish the adoption procedure. New discovered
implementation outside these paths requires an amended reviewed scope before
work. Traceability's actual run writer is `adapters.py::run_tests`, with CLI
entry in `cli.py`; checkpointing must preserve their pinned-runner isolation.

## Test and verification contract

`test-plan.json` lists 16 proposed executable cases with scenarios, expected
assertions, criterion mapping, task ownership and concrete unittest entry points.
All are new behavior assertions; preserve real failing revisions. Fixture TDD
strings in existing reliability tests are not product execution evidence.
Tests for previously executed tasks assert retention of their original Red/Green
identities and absence of a newly fabricated Red run or replacement base.

Future primary checks:

```bash
PYTHONPATH=_ask/scripts python3 _ask/tests/inner_loop_recovery.py
bash _ask/tests/test-inner-loop.sh
bash _ask/tests/test-inner-loop-reliability.sh
bash _ask/tests/test-stages-inner-loop.sh
./ask sync
./ask verify
```

Run applicable traceability run/authority suites and workflow-reference tests for
the touched publication paths. Existing tests of one-writer CAS, stale review,
candidate drift, FF-before-state-fold and source repair remain mandatory. The
new shell wrapper participates in the existing aggregate shell-test discovery.
Register the reviewed interrupt obligations before implementation. Record actual
result/commit evidence after execution; planning is not a verification pass.

## E2E and migration

Applies. Use disposable Git repositories and actual CLI subprocesses. Execute
real failing/passing tests, persist checkpoint and approval, kill at publication
boundaries, remove all ignored runtime files, start a fresh process and assert
the recovered milestone/original base. Exercise changed contracts and missing
checkpoint refs in a second local clone; provide actionable transfer/reconcile
diagnostics without claiming recovered completion. No network or production
datastore is needed. Reset removes fixture worktrees/processes/refs only.

For this branch, audit Tasks 1–5: original bases, code commits, Red/Green source
and test continuity, reviews, accepted-contract revisions and any integration
receipts. Retained Task 2 approval at `0d9089f` is historical and may need renewed
review/checks for the current candidate. Task 3–5 code already exists too; do not
repeat the same restart mistake after recovering Task 2. Keep Tasks 6–10 pending
unless independently supported evidence exists. Correct the regression-only
amendment only through explicit reviewed contract history, never silent relabeling.

## Risks and escalation

- Checkpoint refs are cooperative local authority; candidate/result files cannot
  self-register approval or accepted-tests authority.
- Checkpoint storage includes real logs; measure growth on the retained fixture,
  document retention and explicit export needs. Do not prune required history.
- A missing trusted original contract anchor is a legacy recovery question,
  not permission to select current HEAD as a new task base.
- Contract changes can invalidate applicability while preserving historical
  truth. Report these separately and renew the smallest necessary evidence.
- If existing source/candidate checks cannot adopt legacy history without
  weakening exact-candidate/FF requirements, report the unmet step and obtain
  a reviewed recovery amendment. Do not mark the task integrated to unblock it.

## Planning validation

Run the supplemental graph validator and check criterion/case/task uniqueness,
dependency ordering, executable entry-point names and plan/graph path agreement.
Independently review these exact proposal artifacts and retain their hashes in
`plan-review.md`. No active authority ref or runtime state changes during planning.
