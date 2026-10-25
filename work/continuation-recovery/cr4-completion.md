# CR-4 completed under the scoped human exception

Implementation candidate: `622e89c879c1b09d4982b84b3327bcfcaa216059`.
Coordinator state: revision 59; CR-1, CR-2, CR-3 and CR-4 integrated.
Retained checkpoint: `f457ee3af085e36db8378c9e8218b77c99a77bb4` at
`refs/ask/inner-loop/continuation-recovery`. The cached state exactly matches the
Git-retained checkpoint state. Original task bases and attempt histories remain.

## Result

CR-4 implements the read-only legacy audit/proposal CLI, provenance inventory,
exact preimage and review validation, and disposable regression coverage.
Review found a checkout evidence path escape; the fix rejects traversal and
absolute paths and contains symlink resolution within the checkout. The original
failure is reproduced against immutable pre-fix candidate `a2b7522`.

The independent reviewer `/root/final_review` approved the exact implementation,
TaskResult and proposal payload. The recorded semantic CR-4 review passed its
validator. Proposal payload SHA-256:
`b643b7c4530deb2621262e1e2bf1e0b0e2dc846288b05ea70a318a38889d7535`.

## Verification and integration

- Pinned task run `828faea9006a42c1b618d49f4906a79d`: CR-T15 and CR-T16 passed with complete collection.
- Broader mapped suites: 32 recovery, 29 reliability and 7 entrypoint tests passed.
- All 38 CheckPlan checks passed, including the prescribed wrapper executions.
- Normal coordinator review recording advanced state to revision 57.
- Normal report-consumption integration advanced state to revision 59 without
  rerunning the task tests. The receipt binds the same candidate, report and
  resulting SHA: `work/continuation-recovery/inner-loop/evidence/verify-828faea9-o9xjtaon/integration.json`.
- The integration wrapper reached its 300-second bound during its subsequent
  redundant status/recovery scan. Integration had already published revision 59.
  Its successful state transition, receipt digest and exact cached/retained state
  equality were checked directly; the wrapper was not retried.

`./ask verify` returned nonzero at the outer completion gate after all 38 checks
passed. Its recorded errors are a task-scoped semantic review at a workstream
boundary and stale CR-T10 historical continuity source identities after shared
recovery code changed. The focused CR-4 completion report separately requests
registered per-case historical Reds for CR-T15/16. The human explicitly waived
those requirements and allowed kit exceptions for CR-3 and CR-4 only; see
`cr4-authorization.md`. No canonical failed gate is relabeled as passed, no
historical Red is fabricated, and global kit rules are unchanged. The result is
recorded as `completed-under-scoped-exception`, not formal workstream acceptance.
These broader gate interactions remain parked in
`../../.later/self-hosted-kit-change-boundary.md`.

## Legacy audit outcome and endpoint

The audited product ref remains `agent/shorter-hashes` at
`d04b3a4e515105df8cdf703f2fa0a28895f1524d`.
The reviewed proposal honestly reports missing/unverified Task 1 milestones,
checkout-only Tasks 2–5 evidence, missing structured Refactor/integration proof,
and task-state/accepted-authority conflicts. Validation correctly refuses
adoption on those conflicts. Product state, authority and task schedule were
not changed. Tasks 6–10 remain pending.

CR-4 ends at the reviewed audit/proposal. Product adoption and product-branch
integration require separate direction. The repair queue has no active writer
or resumable candidate. Stop and stand by at this endpoint.

## Retained evidence

Runtime evidence is retained in the checkpoint, including
`inner-loop/evidence/CR-4-full-verification.json`,
`inner-loop/evidence/CR-4-task-completion.json`,
`inner-loop/evidence/review-CR-4-622e89c.md`,
`inner-loop/evidence/CR-4-path-containment-repro.py`, and the TaskResult/report.
Recovery from another checkout requires fetching the workstream's `refs/ask/`
checkpoint and accepted-tests refs as well as the normal branch.
