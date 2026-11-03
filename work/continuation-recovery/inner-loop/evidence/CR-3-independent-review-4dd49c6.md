# CR-3 independent review — REJECTED

Candidate: `4dd49c689509247c6b4372d221cdcbe5a47202f6`.
Fixed base: `2c508ff4248f16a3e3121d33a0fae7297c9b378e`.
Verified source: `c2262d11216f3142a75a994cd88a14801c9a86a6`.

## Model and independence

Runtime: Codex. Coordinator: `/root`.
Standards reviewer: `/root/cr3_standards_review`, a fresh review context.
Spec reviewer: `/root/review_continuation_recovery_plan`, a separate review context
that did not author this implementation. Both independently returned REJECTED.
The exact inherited model and parent-model identifiers are not exposed by the
runtime tool interface. The user assigned the review role; no new model or
approval selection was requested.

## Scope and boundary

Review CR-3 only. The five production/assertion paths changed since the task base
all match CR-3 owned globs; other changes are operational evidence/result archives.
Boundary: **ok**. The later evidence commit changes no production/assertion source.
The canonical 38/38 checks and 8/8 mapped cases ran at the verified source SHA,
not at the evidence-only candidate. Small review probes ran on disposable fixtures.

## Standards

**REJECTED — three findings.**

- **CR3-R01 / P1 — valid isolated candidates cannot integrate.**
  `evidence.py:167` requires candidate ancestry in the pre-FF coordinator HEAD.
  `driver.py:126` invokes finalization before its fast-forward. A real Green
  candidate preserved on a task branch is rejected after returning the disposable
  coordinator to its base. Error: `traceability candidate is outside the active task ancestry`.
  Validate the selected task lineage rather than requiring prior integration.
- **CR3-R02 / P2 — multiple accepted runners are rejected.**
  `evidence.py:193` hardcodes exactly one execution. An independently constructed
  accepted two-runner fixture produced two successful executions and two passing
  mapped cases; public `checkpoint_run` rejected the report shape. Validate every
  accepted execution and bind cases to their corresponding execution.
- **CR3-R04 / P2 — inconsistent pending evidence becomes a Green milestone.**
  `evidence.py:200` and `:211` omit execution runner/argv and case phase bindings.
  Both primary and independent reviewer reproduced public checkpoint publication
  after changing the execution to an unplanned runner/argv and one case to phase
  `red` while the execution retained phase `final_green`. Removing the ledger row
  modeled interrupted insertion; the finalizer repaired and checkpointed it.
  Ordinary completion rejects these bindings (`completion.py:92,105,109`).
  This finding concerns durable milestone eligibility, not a demonstrated bypass
  of the separate integration completion gate.

All three are existing-spec behavior defects in CR-3 owned paths. No optional
smell, broader refactor, scope expansion or contract change is needed.

## Spec

**REJECTED — three findings.**

- **CR3-R01 / P1 — isolated candidate integration contradicts CR-T19.**
  The Spec reviewer separately reproduced the ancestry refusal described above.
  Accepted exact FF support requires finalizing the selected forward candidate.
- **CR3-R03 / P1 — no durable verification-complete milestone before FF.**
  `checkpoint-design.md:87–92` requires publication before FF and completion of
  only missing transitions on recovery. `driver.py:116–138` keeps verified runs
  in memory and publishes only through the final transaction exit. A separate
  disposable probe interrupted precisely at the FF call: the retained checkpoint
  had no run milestones or verification evidence, although local run reports
  existed. Add the missing durable transition and interruption/recovery assertions.
- **CR3-R05 / P2 — accepted interruption and compatibility scenarios are unproven.**
  `inner_loop_recovery.py:480–494` snapshots placeholder old-runner bytes without
  executing the old verifier, consuming its receipt, or testing schema diagnostics
  promised by CR-T21. CR-T20 (`:446–478`) deletes a ledger row and replays it; it
  does not inject process death at its three accepted publication boundaries.
  Preserve existing history and exercise the specified scenarios. Previously
  documented CR-T13/14 generic-CAS/clone diagnostic coverage gaps also remain open.

These are local implementation/assertion defects, not redesign requests.

## Probe observations

- Valid isolated candidate: ancestry proved HEAD → candidate; finalizer refused.
- Two accepted runners: execution exit codes `[0, 0]`, case outcomes both passed;
  public finalizer refused execution shape.
- Inconsistent pending report: execution runner `unplanned-runner`, unplanned argv,
  case phase `red`, execution phase `final_green`; public finalizer recorded Green.
- Stop immediately before FF: retained task `running`, retained run milestones
  `[]`, retained verification absent, three local run reports present.

## Required correction and residual state

Add genuine failing regressions for the newly reproduced defects; correct them
within CR-3; complete applicable Refactor and missing accepted test scenarios;
then obtain fresh independent review and candidate-bound completion evidence.
Working inherited behavior does not need manufactured Red.

No production source, real task state, accepted authority or integration was changed
by this review. No approved review was registered: TaskResult is not present and
this verdict is rejection. The detailed machine-readable sibling contains stable
finding IDs, priorities, locations and required fixes. No human decision is needed.

Standards: 3 findings, worst P1 isolated-writer regression.
Spec: 3 findings, worst P1 pre-FF verification durability and isolated-writer support.
