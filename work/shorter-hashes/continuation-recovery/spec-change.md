# Proposed change: recover task execution across continuations

Status: accepted requirements for the requested planning seal; execution stopped.
Revision 2 applies review R1–R4 under the explicit human sealing direction.
This is the single requirements baseline for the supplemental recovery plan.

## Current specification

`.agents/ask/task-loop.md` requires real Red → Green → Refactor, exact candidate
review and evidence-gated integration. `_ask/docs/inner-loop-evidence.md` defines
local runtime state, results and evidence. The product specification remains
`specs/current/shorter-hashes.json`, revision 7; none of its criteria changes.

State writes are atomic and locked, but `ensure_state`/`run_once` initialize a
missing state at current HEAD. Neither reconciles retained results and previous
execution before starting a pending task. Runtime evidence can be ignored by
Git. Atomic local storage alone does not make a continuation recoverable after
loss or replacement of that storage.

## Evidence and diagnosis

`reproduction.md` records a failing disposable-repository replay of the actual
scheduler: preserve TaskResult/review, remove state, run again. The task restarts
at its implemented candidate. No production files were changed for the replay.

Ranked explanations considered:

1. Missing state causes fresh initialization at HEAD: predicts the replay starts
   the executed task with its Green candidate as base. Observed.
2. All earlier execution evidence was lost: predicts no retained TaskResult or
   review. Contradicted by both the replay and current workstream evidence.
3. The test was always a regression: predicts no earlier failing behavior run.
   Contradicted by Task 2's retained review and implementation commits.

The demonstrated defect is missing reconciliation and durable recovery, not an
absence of historical Red or a requirement to loosen the integration gate.
Legacy artifacts alone still do not prove current integration eligibility.

## Proposed behavior and acceptance criteria

| ID | Requirement |
| --- | --- |
| CR-01 | Before initialization, scheduling or writer admission, reconcile the current task contract, state, retained task evidence, durable checkpoint and relevant Git ancestry. Missing or contradictory history returns `recovery_required` with task IDs, exact evidence locations and next actions before any new base/writer is recorded. |
| CR-02 | Persist coordinator checkpoints outside the ignored worktree cache, under `refs/ask/inner-loop/<work-id>`, with immutable Git objects. Bind work/task identities, stable original initialization anchor, state generation, contract identities, source/base/candidate commits, and referenced result/run/review/integration artifacts and their digests. Store the actual required artifact bytes, not only paths to ignored files. Required source/base/candidate/runner and historical authority commits must remain Git-reachable through checkpoint parent edges, and artifact bytes through its tree; validate the full closure after fixture GC and self-contained bundle transfer. |
| CR-03 | Checkpoint writes use the existing process lock and compare-and-swap ref publication. Publish the immutable checkpoint before replacing the state cache. Death before publication leaves the previous checkpoint; death after publication permits replay of the published checkpoint. Detect cache/ref divergence and concurrent checkpoint writers. Coordinator alone owns checkpoint publication; nested verifier children never acquire the parent state lock or import checkpoint modules. Use transaction-internal finalization, idempotent report/ledger recovery, and the pre-hook runner handoff in checkpoint-design.md. |
| CR-04 | Preserve separate execution milestones (Red, Green, Refactor, review and integration) and their exact provenance. Resume from the first unmet valid milestone. Historical Green does not authorize integration; review is reusable only for its exact bound candidate/result/contract. Completion requires the normal coordinator verification and integration receipt. |
| CR-05 | Restore a missing/older cache from a validated checkpoint only when identities, artifacts, contract applicability and Git context agree. A newer/divergent cache, unsupported schema, incomplete checkpoint, unrelated checkout or changed contract requires explicit reconciliation. Do not infer Red, approval or integration from passing tests, source presence or commit messages. |
| CR-06 | Handle pre-checkpoint workstreams through a read-only reconciliation report and a reviewed explicit adoption record. Preserve original base/candidate and run history; attribute missing milestones honestly and renew only the stale evidence. An adoption cannot label an unverified task integrated. Test reclassification remains an independently reviewed contract change, never an automatic response to Green on resume. Before CR-1, apply the reviewed bootstrap described in bootstrap.md using existing CAS/admission APIs; add CR IDs and start only CR-1 at its own approved baseline while preserving every old task record and the product context. |
| CR-07 | `run`, `resume`, `cas-init`, `spawn-writer` and generic state mutation share recovery guards. Report recoverable stage and evidence through `status`/`reconcile`. Protect recorded execution history against silent lifecycle rollback; deliberate reopen/contract amendment preserves the prior attempt and starts an explicitly identified attempt. The initial scoped suspension is an explicit coordinator instruction until CR-1 enforces it. Every case binds exact immutable production/assertion/fixture files; runtime state and wildcard source bindings are excluded. |
| CR-08 | The `shorter-hashes` reconciliation covers Tasks 1–5, whose code/history predates the restarted queue, before product scheduling resumes. Checkpoint recovery preserves one writer, CAS, exact approvals, task-owned paths, accepted-tests authority and FF-only integration. No extra task or new product behavior is introduced implicitly. Combined graph ordering is 1 -> CR-1 -> CR-2 -> CR-3 -> CR-4 -> 2 -> ... -> 10, validated with original shared paths. No implementation or bootstrap is authorized by the seal. |

## Impact

Affected components: inner-loop state, scheduling, evidence recording, CLI,
traceability run publication, continuation instructions and recovery tests.
Checkpoint publication follows the fixed lock ownership, retention and handoff
in checkpoint-design.md; bootstrap.md fixes the initial state transition. Do not change numeric
reference formats or accept arbitrary candidate-authored checkpoints as authority.

## Alternatives

- Commit only `state.json`: cannot recover ignored logs/results or resolve an
  interrupted multi-resource transition. Retain it as a cache if already tracked.
- Add continuation instructions only: leaves scheduler entry points able to
  restart executed tasks; insufficient for the reproduced defect.
- Permit any passing regression at the TDD gate: does not restore execution
  history and cannot establish that reclassification was correct.
- Use a coordinator checkpoint plus reconciliation: selected proposal; adds
  storage and recovery code while retaining current evidence requirements.

## Migration and limits

Local cooperative Git coordination; no hostile-writer authentication, automatic
remote ref synchronization, distributed consensus or universal power-loss claim.
Transfer the full self-contained checkpoint bundle including required Git object
closure; a clone missing that closure reports incomplete recovery.
Non-Git unit fixtures may use explicit ephemeral mode; public Git workflows use
durable checkpoints. Retain old evidence and authority refs unchanged.

## Decision

The user directed “apply all review changes and seal the plan and stop”. This
approves resolving R1–R4 and registering the independently reviewed combined
planning contract. The requirements here and in spec.json join the unchanged
product requirements through the combined canonical spec. The implementation
endpoint remains stopped; plan registration supplies no execution evidence.
Detailed persistence/bootstrap decisions are normative in checkpoint-design.md
and bootstrap.md. Exact review and registration are recorded in plan-seal.md.
