# Independent RWB-102 fresh review

**REJECTED. Ownership boundary APPROVED.**

Reviewer `/root/review_revising_plan`, selected Sol/high, independent Codex context. Candidate `f52e9ccc8f943dbe36dfb80dc83f2d61f0650ea0`. Admission base `c2635515f4f4643344b8483b86ea7d8e046d4bab`; accepted inventory base `5964fbfb56128e95676f0b991852ac58529cb8f8`. Full task review includes original `c3c148c4d483d9b8cc9ad50915c81e60ea07abb5` and pre-new-base WIP. Earlier rejection artifacts remain preserved. No source/commit/state/ref changes by reviewer.

## F9: schema compatibility and actual admission mix generations

New workflow_admission preflight validates a snapshot, reads its schema and clears selected_execution for v1. It then separately calls admit, which can capture a newer v2 model. In an exact-candidate temporary archive, I controlled a genuine external-save scheduling gap: valid v1 is returned by the real first validation; immediately afterward, the model is saved as fully valid v2 with docs/context.md absent. No guard or action implementation is mocked. The actual selected product/WB003 workflow enters its body on v2 without the required spec passage.

Compatibility and selected-task admission must use the **same captured/admitted Snapshot**. Preserve explicit selectors until schema dispatch on that actual snapshot (including nested admission), and keep invalid-document diagnostic precedence. A read-only preflight from another generation cannot authorize dropping a selected-task gate. This is an introduced high-severity violation of current-before-action and no-mixed-generation requirements.

## F3b: CLI mismatch refusal already publishes a generation

Traceability CLI main enters generic workstream workflow_context before execute reads the review body. Exact-candidate probe starts with valid v2 canonical input, absent selected spec context and no model-state generation; Git HEAD is valid. A review body names scope task/taskWB003, while CLI omits --scope (defaultworkstream). The command returns1 with CLI/body scope mismatch, but load_published changes fromNone to a generation.

Actual request/body scope must be resolved and checked before generic admission publication, with invalid-document error precedence preserved. Current mismatch test checks retained review-file bytes on an already-published fixture and misses this generation-pointer side effect. Required refusal must leave both publication and review state unchanged.

## Prior findings and coverage

F1 persisted-text hash binding, F2 qualified plan-owner refusal/positive, F3 omitted direct task-target guard, F4 v2 real start refusal, F5 safe missing committed unavailable/no fallback, F6 proper same-marker/sufficient-length/whitespace-only fence closer, F7 foreign case/mapping closure, and F8 ordinary valid-v1 route compatibility are substantively repaired. Added legacy tests exercise actual driver/spawn, integration admission, direct/CLI coordinator review and verification bridge; the prior v1 direct integration remains. F9 is introduced by the shared compatibility preflight used to fix F8. F3b is the remaining no-publication aspect of target-scope refusal.

Full source/caller assessment from earlier reports was rechecked against all candidate changes and complete original-base history. All worker sources fit amended ownership; coordinator plan/design/TaskGraph/pin and runtime archive/state history remain approved exclusions. No immutable runner/authority, instrumentation, CheckPlan, integrity, CAS or FF-only gate was weakened. The two actual admission defects still block completion.

Machine input contains all13 case decisions and every selected criterion/type. Selector and context-freshness cases are now approved; passage-actions remains rejected. Ten unchanged guard regressions pass fresh execution. Exactly-once semantic receipt and actual task-start publication lineage checks remain; new missing integration counterexamples are the concrete F9/F3b probes above, not a request for new product scope.

## TDD and current evidence

Latest test-only red `f98ffa6c93289a09c68930b9a5cb299ab7a584b1`, registered run `6e5d6e3a1bbd4335b074a90ec0703295`, has selector/action behavior assertion failures and11 passes. Final run `9f8a0021cdf344399a83a800383c5ffa` is registered to this candidate and passes all13. Canonical report-ledger digests, retained log hashes and case-source Git bindings were independently verified. Latest red/final test bytes are identical. Earlier genuine pre-fix ledger44d6d62/d386cfe history preserves the original/F1-F7 obligations and additive continuity; no assertion weakening or behavioral exemption is used.

TaskResult now cites the registered current red/green pair; prior unregistered supplemental citation is no longer used. Current evidence is genuine but cannot override F9/F3b. Machine parser errors are solely intended rejected semantic decisions, with exact candidate/spec/plan/source/inventory bindings intact.

Coordinator must preserve this rejection, add real failing probes for F9/F3b, repair within the existing amended scope, obtain fresh current evidence and independent review. No integration authorization forf52e9cc.
