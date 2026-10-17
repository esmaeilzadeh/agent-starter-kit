# RWB-107 independent candidate review

- Reviewer: `/root/review_rwb107` (independent delegated Kit 07 context).
- Runtime: Codex. Model: GPT-6 family as declared by the runtime; the exact selectable model identifier is not exposed to this reviewer. Repository selection requests `gpt-6.1-sol`, reasoning `high`; that selection is recorded here as configuration, not independently verified runtime identity. Parent model: GPT-6 family; exact identifier unavailable.
- Candidate: `f5adb9e8f075a2aed8fceac6eca9529115154a5f`.
- Recorded task base: `bf197e62a7cfcb7046901535e1e16ea1c4c6cebf`.
- TaskResult: `work/revising-workbench/inner-loop/results/RWB-107.json`.
- TaskResult byte SHA256: `be32804eeafcc4464c26f356b11ff63ed82ef71d78f3690a7e8e2038eed58231`.
- TaskResult canonical JSON SHA256: `f4a3cad95c1e969ba4a10e219eb3eea6a40ab16f76708419c7d2011f02fa1074`.
- Accepted contract: `54ef012b0517758ee548a2a4ee79b28e698990ff`; canonical spec digest `626fab82df682bdc7b382e4188bc822e488a8bf4ca9682a209be535fcea119bd`, plan digest `36fe0b54e4431123d52649a3fd5f6ce738ebfdf2cd503428fcf3a5f55a157769`, graph digest `bc59ece2074e22e98499237a7f9fa9521a28924212eafe63c72c552306ee41ba`.
- Verdict: **REJECTED**.
- Steering boundary: **ok**. Extras: none requiring reversion. `glob_too_narrow`: none established by this review.

## Findings

### P1: Required flow-specific negative assertion is absent

Location: `_ask/tests/test_revising_detail.py:40`, assigned case `RWB-APP-EVIDENCE`; accepted EM-011 assertion: “unrelated criterion Test is not proof.”

The case checks a selected Test's setup/helper/assertion rendering and canonical plan scenario text, historical candidate inspection, invalid evidence rendering, distinct expander identities and lazy result inspection. Its delegated existing AppTest journeys also contain no competing criterion-linked Test or unselected Scenario flow. The three direct flow assertions at lines 110–112 compare one fixture's expected narrative. Consequently a regression which presents another Test sharing the criterion as proof of the selected flow can still satisfy all inspected assertions. The case's name includes “flow_specificity”, but that behavior is not asserted.

Minimal remediation is an assertion in the owned `_ask/tests/test_revising_detail.py` AppTest case: admit two distinct concrete flows/Tests sharing a criterion, select one Scenario, and assert the exact selected Test/source/assertion/result association while the unrelated Test is absent from proving that flow (or explicitly labeled criterion-related without flow coverage). Exercise the real Scenario-to-Test UI route and admission/projection caller. A positive assertion that the selected Test appears must be paired with the negative competing-Test assertion. No ownership change is needed to add that case. If it exposes a source defect outside the owned seams, stop for a narrow ownership amendment instead of editing an unowned renderer.

### P1: Referenced red and green execution artifacts are unavailable

The TaskResult cites behavior-red run `6e185916ba1f44e9881b1498a448db1b` for candidate `911a6ab9434c2c512688cf3160927ac1ca2fecb7` and final-green run `cdd859c407a8446e819c29126dcadde7` for the exact final candidate. Neither cited `work/revising-workbench/traceability/runs/<run-id>/results.json` exists in this checkout; the traceability run subtree is absent. The coordinator independently confirmed the absence during this review.

TaskResult prose and exit codes cannot establish collected identities, real assertion failures, per-case outcomes, output hashes or current execution. Under `_ask/docs/spec-test-traceability.md`, completion requires retained actual execution and semantic continuity. Restore or rerun exact immutable red/final candidates through the supported instrumented runner, retain result/log evidence, and bind a fresh review to those bytes. Changed coverage assertions require corresponding valid red continuity, not only another green run.

### P2: Full result-state coverage is not explicit in the assigned case

EM-011 also names passed, failed, not run, skipped, runtime error, stale, historical and unavailable states. The assigned case positively exercises historical/passed/invalid states and loader-side retained failed output, but its inspected assertions do not enumerate skipped/runtime-error/not-run UI states. Include representative assertions or identify an independently reviewed, explicit coverage mapping for those meanings. This is an assertion-coverage observation; source inspection found no demonstrated state-classification defect.

## Changed-path and boundary assessment

The complete base-to-candidate diff was inspected, rather than only the final commit. Product/test changes are limited to `_ask/ui/workbench_loading.py`, `_ask/ui/workbench_tasks.py`, `_ask/ui/workbench_tests.py`, and `_ask/tests/test_revising_detail.py`. All four are inside the accepted RWB-107 ownership set. Unchanged owned renderers (`workbench_debug.py`, `workbench_attention.py`) were read through their test-facing behavior where relevant.

Additional diff paths are predecessor RWB-106 review/result/integration evidence, the inner-loop state file, the RWB-107 TaskGraph ownership amendment, the matching plan row, and the accepted traceability pin. Runtime paths are explicit policy exceptions. The independently approved contract amendment adds only `workbench_tasks.py`, preserves What/Why and all canonical test/spec obligations, and serializes predecessor/successor ownership through the task chain. Those coordinator changes are accounted-for administrative/contract history, not worker scope extras. The transient later card is deleted before the final candidate and does not survive the base-to-candidate diff.

## Semantic and assertion assessment

- `RWB-APP-EVIDENCE` (integration; EM-003/EM-005/EM-011): **partial**. Positive setup/helper/current revision assertions use a genuinely admitted v2 model, namespaced selector, model-declared external helper and selected canonical plan text. Same-mtime helper edits change identity and refuse stale helper bytes. UI checks show source assertion, collapsed helper context and actual source commit. Retained output exposure uses report/log authority followed by an independent streamed SHA256 check and a bounded tail. Negative flow-association coverage is missing as above. Passed/historical/invalid provenance assertions are useful; full named-state coverage remains incomplete.
- `RWB-APP-DECISIONS` (integration; EM-002/EM-006/EM-007/EM-010): **source/assertion assessment acceptable**, execution unverified. Existing AppTest journeys assert actor/rationale persistence across a new session, dependent readiness, missing actor/rationale no-write and referenced-spec stale-form no-write until explicit refresh. The added committed-revision journey asserts disabled submission and byte preservation. Task context now resolves blocker IDs to decision title/options/latest attribution/rationale without mutating decision authority; assertions exercise the actual Task UI. These are behavior assertions rather than implementation mirrors.
- `RWB-LAZY-CACHE` (integration; EM-012): **source/assertion assessment acceptable**, execution unverified. Spies wrap actual selected-source loading and history evaluation, assert zero initial loads, one selected load and unchanged revisit reuse, then same-mtime source/log mutation plus explicit refresh causes reevaluation and invalid output display. The additional admitted-helper case supplies the previously missing external-helper dependency counterexample. Cache content identity includes the curated paths. No broad eager source/evidence read was introduced by the candidate in the Overview caller.

Every new test method in the changed test module maps to one of the three accepted case IDs. Private helpers support those methods; reused existing public-AppTest tests stay unchanged. No changed-test exemption is claimed or applicable.

## TDD continuity and limits

Compared immutable red candidate `911a6ab` with final candidate `f5adb9e`. The only test-source change is the provenance assertion text changing from `Inspected source revision: <sha>` to `Source commit: <sha>`. Both assert the same inspected immutable source commit; this is consistent semantic assertion continuity, not weakening the test or replacing a failed condition with unrelated success. Helper-freshness, admitted-model, blocker-context and lazy-tamper assertions already exist in the cited red candidate. Their actual red outcomes cannot be verified without the missing execution artifacts. The missing competing-flow assertion has no TDD history and must be added and reviewed in the remediation candidate.

No tests were run and no source, pins, state or TaskResult were modified by this reviewer. This artifact records read-only exact-candidate review plus the allowed runtime evidence write. The candidate remains **REJECTED / boundary ok** until the blocking coverage and execution-evidence findings are resolved and independently rebound.
