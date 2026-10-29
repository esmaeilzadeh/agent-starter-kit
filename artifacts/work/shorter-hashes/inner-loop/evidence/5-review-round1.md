# Review

## Model

Sol reviewer; runtime: Codex; parent_model: not exposed in this review context.

## Scope

Independent review of Task 5 candidate `e5e140b05a657e958a8c179d2a13f532d4eef319`, based on Task 5 base `d5b8b002796830e33115dac394ad071d08165e9e` and the accepted Task 5 contract. The coordinator supplied Red run `a26ee5f99c99454383a7a35ae3a9f2a2` (5/3 behavior assertion) and Green run `e6d8cdaea78049b4b960da32c9352f9d` (all three mapped cases passed). Changed paths are within Task 5 ownership: `.agents/ask/verification/traceability/adapters.py` and `_ask/tests/test_workflow_refs_traceability.py`.

Independent local checks: `test_workflow_refs_traceability.py` passed all 3 tests; `test_traceability_evidence.py` passed all 13 tests. These checks do not establish the missing 5/3 contract scenario identified below.

## Findings

### F1 — The 5/3 “newer item binding” is not registered or resolved

Classification: **local structural suggestion** (mapped integration coverage does not exercise the accepted scenario).

At `_ask/tests/test_workflow_refs_traceability.py:144-148`, the test writes a JSON file containing `{"reference":{"id":1,"revision":1}}` and commits it. At lines 158-161 it adds an arbitrary `reference_bindings` member to `test-plan.json`. A repository search finds no production consumer for `reference_bindings`; the test itself is its only occurrence. The scenario therefore never registers a qualified numeric item revision in the workflow reference integrity catalog, resolves that revision, or exercises the accepted contract's source/binding relationship.

This does not establish the planned 5/3 case in `work/shorter-hashes/test-plan.json:1296-1336`: “a newer item binding” followed by registration of new run evidence and a contract amendment, while preserving exact source and accepted-contract bindings. The fixture currently checks a fabricated JSON convention rather than the workflow refs binding path.

Actionable location: `_ask/tests/test_workflow_refs_traceability.py:144-161`. Build the scenario through the workflow refs catalog/API: register the qualified numeric item revision, resolve it against its source snapshot, then demonstrate the coordinator-approved amendment and fresh evidence bind to that registered revision. Keep the old accepted entry immutable and assert it retains the original bindings.

### F2 — The historical-Green assertion is confounded by stale review evidence

Classification: **local structural suggestion** (the mapped assertion does not isolate the contract guarantee).

At `_ask/tests/test_workflow_refs_traceability.py:151-154`, the stale completion attempt passes `consumer.record`, which is the review record for `old_candidate`, along with the old Red and Green runs, while claiming `newer_binding` as candidate. Failure can therefore be caused by the stale review/candidate binding before the assertion demonstrates that a historical final Green cannot be reused under otherwise-current review evidence.

Actionable location: `_ask/tests/test_workflow_refs_traceability.py:151-154`. Create a review record valid for the new candidate/accepted contract while retaining the historical Green, and assert completion still fails because there is no current exact-bound Green. Then retain the existing fresh Red/review/Green success path for the amended contract.

## Suggested fixes

Complete F1 and F2 in the Task 5 owned test path, capture a Red run that fails by behavior assertion for the strengthened 5/3 scenario, then Green and request a fresh exact-candidate review. No implementation behavior defect is established by this review.

## Parked refactor handoffs

None.

## Residual risks

The adapter environment-path change is covered by a fixture with a competing host package and candidate private package; the mapped test passed and asserted candidate `source_sha`. The requested mapped local suites passed. This review did not run the entire repository suite.

## Review verdict

**REJECTED** — F1 and F2 are valid Task 5-local coverage gaps in the required 5/3 mapped integration scenario. The supplied Green run does not close them.
