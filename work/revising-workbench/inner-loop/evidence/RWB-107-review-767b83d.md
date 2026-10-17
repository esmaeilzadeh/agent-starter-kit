# RWB-107 independent candidate review

- Reviewer: `/root/review_rwb107`, independent delegated Kit 07 context.
- Runtime: Codex. Model: GPT-6 family as declared by this runtime; exact selectable model identifier unavailable. Configured review selection: `gpt-6.1-sol`, high reasoning. Parent model: GPT-6 family, exact identifier unavailable. Configuration is not independently verified runtime identity.
- Candidate: `767b83dd56b32ba155020a7996510cfea0233ec0`.
- Recorded base: `bf197e62a7cfcb7046901535e1e16ea1c4c6cebf`.
- TaskResult: `work/revising-workbench/inner-loop/results/RWB-107.json`.
- TaskResult byte SHA256: `2d8706f19d54ef7c74eceda4679cdf480524f159ac1f3344aeadd727b20c653c`.
- TaskResult canonical JSON SHA256: `45556608a8e81796f4b63e0a923e7ad2425b87c3cb38eed2644562689c400a81`.
- Accepted contract: `54ef012b0517758ee548a2a4ee79b28e698990ff`.
- Canonical spec digest: `626fab82df682bdc7b382e4188bc822e488a8bf4ca9682a209be535fcea119bd`.
- Canonical plan digest: `36fe0b54e4431123d52649a3fd5f6ce738ebfdf2cd503428fcf3a5f55a157769`.
- Accepted TaskGraph digest: `bc59ece2074e22e98499237a7f9fa9521a28924212eafe63c72c552306ee41ba`.
- Verdict: **APPROVED**.
- Boundary: **ok**. Extras: none requiring reversion. `glob_too_narrow`: none.

## Review scope and findings

Reviewed the complete original-base-to-candidate diff, accepted spec and test plan, amended ownership, current TaskResult, exact retained reports/logs and test-source continuity. No remaining blocking findings. This decision supersedes the rejected source/evidence review of `f5adb9e` for this exact candidate and bound TaskResult only.

All changed product/test paths are owned by RWB-107: `_ask/ui/workbench_loading.py`, `_ask/ui/workbench_tasks.py`, `_ask/ui/workbench_tests.py`, `_ask/tests/test_revising_detail.py`. The additional complete-diff paths are RWB-106 runtime review/result/integration history, RWB-107 runtime result/state, the independently approved TaskGraph ownership amendment, its matching plan row, and accepted pin. Runtime files are explicit policy exceptions; the reviewed amendment authorizes the Task renderer needed by the unchanged blocker-context obligation. No worker source expansion or change to What/Why, criterion, required type or executable selector is hidden in that history. The dependency chain serializes shared ownership.

The complete product source diff is unchanged from the earlier review. It restores captured canonical test-plan fields and model-declared source context, verifies committed and working test/helper dependencies by content, invalidates same-mtime helper edits, loads qualified source from the selected revision, displays helper roles/explanations under initially collapsed expanders, and exposes retained output only after report/log authority and a fresh SHA256 check. Output reads retain a bounded tail. Task blocker presentation resolves the reasoned decision context without modifying lifecycle or action authority. No semantic source defect was established in these seams.

## Prior findings closed

1. **Criterion-only sibling flow:** the new private helper creates an admitted v2 model with two concrete Scenario/Test selections sharing `EM-007`. Each Test has a distinct canonical plan case and flow. Both selectors pin the updated plan digest. Projection assertions require exactly `WB-publish -> scenario` and `WB-stale -> scenario-stale`; broad criterion inference would fail these assertions. Real AppTest then opens the selected Test and requires its valid-model flow while excluding the sibling refusal narrative and sibling source assertion. This combines an actual admission/projection counterexample with selected UI rendering; the previously absent unrelated-criterion negative assertion is now present. Inspection of the unchanged Scenario renderer confirms it consumes these explicit `scenario_ids` and explicit canonical test mappings, without adding criterion inference.
2. **Missing execution evidence:** exact retained red and green reports, ledger bindings, case identities, source digests and output logs are now present and match. See the evidence section.
3. **Skipped/runtime-error/not-run display:** the new AppTest helper exercises the real Result route with controlled loader-boundary fixtures for each state. It asserts Skipped, Error plus runtime-error detail, and no-recorded-execution respectively; each excludes Passed, and not-run excludes any recorded outcome. The controlled rows establish rendering semantics rather than claiming genuine external execution of those fixture outcomes. Existing real retained-evidence/log-integrity journeys remain intact, and the separately existing `test_revising_evidence.EvidenceIdentityTests.test_all_observation_states_and_helper_changes_preserve_applicability` supplies evaluator-level state coverage.

## Criterion, type and assertion decisions

All three accepted required types are **integration**. Their exact public test methods remain the assigned collected case identities; no additional public method or unsupported dynamic subtest was introduced. Private helpers are directly called by those methods. No exemption is requested or needed.

| Assigned case | Criteria | Coverage and type decision | Assertion/counterexample assessment |
| --- | --- | --- | --- |
| RWB-APP-EVIDENCE | EM-003, EM-005, EM-011 | APPROVED integration | Actual admitted v2 snapshot and canonical plan drive namespaced selected source, setup/helpers and flow narrative. External helper content tampering at unchanged mtime invalidates the detail and refuses stale committed context. Selected/sibling flows cannot acquire coverage from shared criteria. Genuine retained history supplies passed/failed output and provenance; invalid/tampered/historical evidence stays distinguished. Controlled UI fixtures add skipped/error/not-run semantics. Explanatory technical/helper context is initially collapsed; narrative remains distinct from source assertions and recorded observations. |
| RWB-APP-DECISIONS | EM-002, EM-006, EM-007, EM-010 | APPROVED integration | Public AppTest journeys verify persisted actor/rationale across a new session and resulting readiness. Missing actor/rationale and linked-spec stale forms preserve published identity and remain open until explicit refresh. Committed inspection disables submission and preserves model bytes. Task detail asserts blocker title/cause/options/latest actor/rationale. These assertions detect meaningful missing or incorrectly attributed context and write guards rather than merely mirroring renderer internals. |
| RWB-LAZY-CACHE | EM-012 | APPROVED integration | Wrapped real loaders/evaluators assert zero initial source/history scans, one selected load, unchanged revisit reuse and reevaluation after same-mtime source/log edits plus refresh. Tampered output renders invalid. Cache keys now additionally include curated helper content, covered by the admitted-helper counterexample in the evidence case. |

## Retained execution and TDD binding

Inspected reports and ledger canonical SHA256 bindings:

- Historical behavior-red: run `7155d3d198064d1286779dc1f7c62630`, immutable source `65eae3047c830de732ce4f56b529d0d3f688139a`, canonical report SHA256 `3a308718af13ca9c855a628e4e2a324c81b5905f945dbf2d8c18a56b67ccf1c0`. All three assigned cases collected successfully and failed as `behavior_assertion`; all three executions exit 1. Logs show real failed expectations: absent readable context, absent reasoned blocker title, and absent captured execution output. No import/setup failure supplies this red.
- Additional helper-freshness/blocker behavior-red: run `734d987c1be2407e98eb900af1a34ee0`, source `911a6ab9434c2c512688cf3160927ac1ca2fecb7`, canonical report SHA256 `fa5bfc484006fbd19eb03ceb94e7ad863a56037aeabf33786170fb2b04f4ba21`. Evidence and decision cases fail as behavior assertions; lazy cache passes here and does not supply its red. The helper failure is specifically unchanged cache identity after same-mtime curated-helper mutation.
- Exact final green: run `f23cdc83a2904dd68f9315b56e36ea6b`, source `767b83dd56b32ba155020a7996510cfea0233ec0`, canonical report SHA256 `3810691b4334d619b37d19d8e485955e0704b2493d411d763386ca5b61c9b992`. All three assigned cases pass with successful collection and exit 0. Final test-source SHA256 `024058a56d299d3ada986c8a2641d6d27873891d8f7f670e51fb3a4ae1f9e407` matches the candidate blob.

For all nine inspected red/additional-red/green case records, source digests match their immutable Git blobs and log SHA256 values match retained output bytes. Report digests match the execution ledger. Case/runner/execution IDs and candidate/spec/plan/scope/task bindings agree. The two earlier system-Python collection-error attempts have no cases and supply no TDD evidence.

The lazy-cache test AST is identical at historical red `65eae30`, additional red `911a6ab`, and final `767b83d` (AST SHA256 `63a632f7c99af33372fc38da7dc67fa3fed23a050a84c880e9a9952e963d9d54`). It preserves the exact missing-output assertion through red and green. Evidence/decision cases retain their original failed semantic conditions while strengthening fixtures and adding the sibling-flow/state assertions. The provenance assertion wording changes from “Inspected source revision” to “Source commit” while requiring the same full source SHA; no semantic expectation is weakened. The added counterexamples strengthen coverage of the already accepted behavior and do not substitute an unrelated passing assertion for red. TDD continuity is **APPROVED** for each assigned case.

## Limits

This is independent semantic and retained-evidence review, not outer workstream acceptance. The coordinator must still bind this artifact and TaskResult through the normal review authority and execute the integration gate; outer Verify and Accept remain required. TaskResult notes retain historical earlier run/candidate references, but its current structured red/green fields and candidate binding are unambiguous and are the evidence approved here.

No tests were run by this reviewer. No source, TaskResult, state or accepted pin was edited; only this permitted runtime review artifact was written. Final decision: **APPROVED / boundary ok** for candidate `767b83dd56b32ba155020a7996510cfea0233ec0` and the TaskResult digest above.
