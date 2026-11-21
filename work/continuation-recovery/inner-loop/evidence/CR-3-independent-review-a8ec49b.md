# CR-3 independent review: T11 stale approval history

- Reviewed candidate: `a8ec49b649474f22212552229750a84089b16a86`
- Comparison base: `ff6af28654b8495040adf459dcb98d55748b0c10`
- Scope: `_ask/tests/inner_loop_recovery.py`, CR-T11 correction only.
- Review axes: Standards and Spec, independently reviewed.

## Standards

No documented-standard violations were found. The test-specific combination
of `RecoveryTests` and `IntegrationTests` reuses their fixture behavior but
adds some setup complexity; this is a maintainability judgement call, not a
required correction.

## Spec

**APPROVED.** CR-T11 now runs genuine Red and Green traceability executions,
checkpoints both, records an approved review bound to the Green candidate, then
advances the task branch and verifies the old approval is rejected as stale.
It asserts that both the original run history and coordinator-recorded review
remain unchanged. This addresses the CR-3 decision's requirement to preserve
historical execution without reusing an inapplicable approval.

## Scope and limits

The review covers only the exact T11 diff. It does not establish CR-3
completion or resolve the separate recognized-Red evidence gap for CR-T12,
CR-T13, and CR-T21. The older semantic-review rejection remains immutable.

## Verification

- Focused T11, T12, and T13 recovery tests: passed.
- Full `_ask.tests.inner_loop_recovery` suite: 24 tests passed.
