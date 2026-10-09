# Specification Change Proposal: scope semantic review to the active task

## Current specification

The accepted contract is pinned at `822c24338765f00cc66b189d863e247a2b688d38`. Its plan sequences nine tasks and explicitly says to add each task's future test module only when starting that task. WB-001 owns 25 mapped cases; later tasks collectively own 32 more cases, and their source modules are intentionally absent at the WB-001 boundary.

The task-level CheckPlan invocation runs the selected task's mapped behavior cases. Its completion check nevertheless loads a single unscoped semantic review whose validator requires all 12 criteria, all 57 tests, and source digests for every source path. `record_test_review` computes those digests from the candidate tree before recording the review. For candidate `0b14c15317d90c94435b045924d77adb304795ea`, that lookup fails because future WB-002–WB-009 test modules have not been introduced. Therefore WB-001 cannot produce truthful semantic-review evidence under the current task-level Verify flow.

## Proposed change

Amend the verification contract to support task-scoped semantic review for task-level candidate integration:

- A review records its scope (`task` plus task ID, or `workstream`) and binds the exact selected test IDs and criterion IDs.
- For task scope, source inventory and digests include only source paths referenced by that task's accepted test IDs. Per-test assessments cover every selected case; criterion assessments cover the criteria represented by those selected cases.
- Task-level completion validates the matching scoped review and its selected source digests. It continues to require every assigned case, red/green history, and current candidate identity.
- Workstream scope continues to require semantic review of all criteria and all accepted tests. No missing future test module or assessment is treated as available.

Update the traceability review recorder/evaluator and their tests as verification support. Independently review the exact contract and source candidate, then accept and pin that reviewed candidate before the coordinator uses the updated runner. Preserve WB-001's current approved inner-loop review, 25-case green run, prior failed integration evidence, and all future obligations. Rebind WB-001 to a fresh coordinator/base after pinning, as required by the accepted-contract loader.

Also add the user's delivery rule for UI tasks: after each WB-004–WB-009 integration, run the integrated UI, inspect it against the connected hierarchy and task outcome, and record a candidate-bound screenshot and findings before the next UI task starts.

## Why the change is needed

The current single review shape conflates two stages: a task integration check after one bounded task and final workstream acceptance after all tasks. Requiring all future source to exist before integrating the first task contradicts the accepted task sequence. Adding placeholder or guessed source files would invent reviewable behavior. A scope-bound review lets task integration assess only the behavior and source that exist at that candidate while preserving full review at the final workstream gate.

## Impacted artifacts

- `work/structured-agentic-environment/plan.md`: define task-scoped semantic review for task candidate integration and retain full review for final workstream verification.
- `work/structured-agentic-environment/inner-loop/tasks.yaml`: add bounded WB-001 verification-support ownership for the traceability review recorder/evaluator and focused tests.
- `.agents/ask/verification/traceability/evidence.py` and `completion.py`: represent, record, and validate the requested review scope.
- Traceability verification tests covering scoped review selection, source hashing, wrong scope, missing modules, and unchanged full-workstream requirements.
- Unique WB-004–WB-009 checkpoint notes and screenshots, each owned by its corresponding task.
- New independent review and accepted pin; new WB-001 coordinator attempt and candidate-bound result/review/integration evidence.

No product criteria or product behavior changes are proposed. No future test modules or assertions are added early.

## Impacted workstreams

Only `structured-agentic-environment`, beginning with WB-001 candidate integration. WB-002–WB-009 continue to add and review their own mapped sources when those tasks start. Final workstream verification still requires all accepted sources and cases.

## Migration / transition notes

Keep the previous accepted pin and the `0b14c15` candidate review, red/green evidence, and failed CheckPlan integration report as historical evidence. Once the amendment is independently reviewed and pinned, establish a fresh coordinator/base bound to that pin and rerun candidate integration. The existing WB-001 approval remains valid for the shell edit but does not approve traceability runner changes or a later composite candidate.

## Acceptance criteria for the change

1. A WB-001 task review resolves exactly the 25 accepted WB-001 test IDs and the criterion IDs they cover, without reading absent later-task source modules.
2. The review binds only present source files selected by those tests, the exact candidate and accepted contract, and cannot satisfy another task's review.
3. Task-level Verify accepts a complete matching task review and still rejects missing/failed task cases, stale source, wrong candidate, or invalid review.
4. Workstream-level review still requires every accepted test and criterion; absent future sources remain unavailable until their tasks add them.
5. The modified recorder/evaluator and tests receive independent review and are included in a new accepted pin before coordinator integration uses them.
6. Every UI task WB-004–WB-009 ends with a candidate-bound visual checkpoint; a mismatch is corrected before the next UI task begins.

## Decision

Approved by the human in chat on 2026-10-09: “do not wait run all task I will review the final result.” I interpret this as authorization to proceed with the necessary reviewed task-scoped verification amendment, while retaining full workstream review. The accepted plan is being amended and will require independent review and a new pin before implementation. No traceability implementation has been changed by this proposal.
