# Independent review: WB-001 revised candidate

## Model

- model: gpt-6-astra
- runtime: codex
- parent_model: gpt-6-luna
- reviewer: /root/review_wb001
- Human model choice and same-family second confirmation remain applicable to this fresh review.

## Scope

- work_id: structured-agentic-environment
- task_id: WB-001
- base_sha: b1f8b49fe4c94c993deb1d65ea59a04303fc66df
- candidate_sha: 69cfc37ff6b0d8264f0200c6a17668f3efc3e288
- TaskResult: work/structured-agentic-environment/inner-loop/results/WB-001.json
- Accepted contract SHA: b755d83141b030d2d101e9fd9f37b51e28a8ef26
- spec_digest: f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb
- plan_digest: 572d2c3dda82e69a49d78b1320ec35835f4f153137e62c35f41af678ad106330

This fresh decision covers the exact revised candidate against the accepted WB-001 scope, specification revision 3, task graph, test scopes, plan and workbench-design relationship authority. The earlier rejected review at `work/structured-agentic-environment/inner-loop/evidence/WB-001-review.md` is preserved. WB-001 remains the current running writer according to `./ask inner-loop status structured-agentic-environment`.

## Steering boundary

boundary: ok

`git diff --name-only b1f8b49fe4c94c993deb1d65ea59a04303fc66df 69cfc37ff6b0d8264f0200c6a17668f3efc3e288` returns exactly:

- _ask/scripts/engineering_model/projection.py
- _ask/scripts/engineering_model/workbench.py
- _ask/tests/test_engineering_workbench.py

All match WB-001 owned paths. Candidate ancestry from the recorded base was verified with `git merge-base --is-ancestor`. No extras or glob_too_narrow issue. Relative to rejected candidate 7c75164647fec43ba1ac5908ae16038342932511, only workbench.py and its three mapped tests change; the remediations add canonical joins and preserve legacy relationships.

## Findings

No blocking findings remain for WB-001.

### R1 resolved — Canonical criterion membership is joined

At `_ask/scripts/engineering_model/workbench.py:59`, model scenarios are indexed by their current-work canonical spec path and criterion ID. Lines 74–80 union each accepted plan case's criterion membership with recorded model covers links. Task scenarios and secondary test/task links consume that union without changing executable ownership.

The revised fixture removes the redundant CASE-2 model test node and covers edge. `_ask/tests/test_engineering_workbench.py:124` now requires CASE-2 to map to s2 through its canonical C2 criterion and to retain task-b as its sole owner. The existing CASE-1 secondary task-b assertion remains. Independent disposable-fixture inspection confirmed CASE-2 scenario_ids=[s2], owner_task_id=task-b, and CASE-1 related_tasks includes task-b with via=scenario-coverage. The real repository pilot's MV-graph now maps to representative-model-is-accepted through EM-001 without a duplicate model test node.

### R2 resolved — Model-only recorded associations survive

At `_ask/scripts/engineering_model/workbench.py:149`, the model-only fallback retains explicit implementation/scenario links. `_ask/tests/test_engineering_workbench.py:147` requires legacy-task to expose s3 with via=recorded-implementation. Independent disposable-fixture inspection confirmed that association while status remains not-recorded, record_source remains engineering-model, runtime_status and result_path remain None, and model lifecycle/readiness remain separate fields. No completion or historical execution is fabricated from the association.

### Foreign-work isolation checked

Current-work test plan and graph identities are checked before joining. Canonical scenario lookup requires `specs/current/<snapshot.work_id>.json`, and recorded test coverage requires `work/<snapshot.work_id>/test-plan.json`.

The retained fixture reuses CASE-1 in another work. To make the isolation check discriminating, this reviewer also used a disposable fixture with a foreign-case covers edge to local s3, plus a foreign-scenario referencing `specs/current/other.json#C2`. Local CASE-1 retained only s1/s2, and local CASE-2 retained only s2. Neither the unique foreign edge nor the reused foreign criterion joined. These checks wrote only test-owned temporary files; committed source and pilot records were untouched.

## Assertion and criterion/type assessment

The changed test inventory remains exactly WB-relations, WB-task-history and WB-story-context in `_ask/tests/test_engineering_workbench.py`. Existing assertions were retained; removal of the CASE-2 model node makes canonical membership observable rather than masking it. The added model-only implementation pair makes R2 observable. No unrelated test source or accepted contract changed.

| Case | Assessment |
| --- | --- |
| WB-relations, EM-008/unit | Shared membership, deduplication, exact executable ownership and labeled secondary coverage remain asserted; canonical-only CASE-2 now has a discriminating assertion. Foreign isolation additionally checked independently as described above. |
| WB-task-history, EM-008 and EM-010/integration | Attributable graph metadata, explicit associations, missing-runtime planned state, model-only labeling, actual integrated/blocked states and legacy explicit scenario links are asserted. The legacy link does not promote missing history to completion. |
| WB-story-context, EM-008/unit | Recorded story s1/s2 membership and explicitly unassigned s3 remain asserted, without fabricated story containment. |

The prior review's case-by-case assessment of all 22 unchanged foundation tests remains applicable; their source digests are unchanged and each passed again at this exact candidate. Specifically: MV-valid/MV-graph/MV-fields/MV-refs exercise EM-001 valid/invalid definitions; ME-decision/ME-revise/ME-reject/ME-race exercise EM-002 mutation, history, blockers, stale rejection and races; EV-real/EV-missing exercise EM-003 real, tampered, missing and historical read-only evidence; MP-shared/MC-journey exercise EM-004 projection parity and CLI persistence; DG-pre/DG-post/DG-refs/DG-events/DG-parity/DG-publish/DG-bootstrap/ME-batch/DG-success/DG-entrypoints exercise EM-007 pre/post validation, referenced-input identity, complete publication and public entrypoint admission. Their assertions, counterexamples and retained regression classification were inspected in the earlier review and rechecked against the unchanged source inventory and fresh case evidence.

WB-001 establishes the assigned unit/integration projection slice of EM-008 and integration metadata slice of EM-010. UI/e2e obligations and the remaining criterion/type combinations belong to later tasks. This approval does not claim all workstream criteria or final completion. No historical behavior-red evidence for unchanged foundation tests is invented.

## Execution evidence and TDD continuity

Second red report: `work/structured-agentic-environment/traceability/runs/f9babe1fd98f46d4b027cde9fc00008c/results.json`.

- source_sha: 912e0599bcb079307512f3dbdcc7de13e31417bb
- phase: red; collection_status: ok; exit_code: 1
- 25 cases: 23 passed, WB-relations and WB-task-history failed as behavior_assertion; WB-story-context passed.
- Exact log: `work/structured-agentic-environment/traceability/runs/f9babe1fd98f46d4b027cde9fc00008c/86551565cc574acab8e9ad90f13b14d0.log`
- Log SHA-256 verified: 2f0b66b6c2860ab06665b0b2bbc1fbf52c7e61955b4561d223e9ae81f7c61974
- The actual failures are CASE-2 scenario_ids=[] versus [s2], and legacy-task related_scenarios=[] versus its recorded s3 association. They are the exact prior review counterexamples, not collection/import errors.

Candidate final-green report: `work/structured-agentic-environment/traceability/runs/81f34719cd664d9591746be954af8169/results.json`.

- source_sha: 69cfc37ff6b0d8264f0200c6a17668f3efc3e288
- phase: final_green; collection_status: ok; exit_code: 0
- All 25 assigned cases passed; exact log records 25 tests in 21.833s / OK.
- Exact log: `work/structured-agentic-environment/traceability/runs/81f34719cd664d9591746be954af8169/32d2e1131c9a4319929535b1775b6c74.log`
- Log SHA-256 verified: 3cdf4a37ea5574a9482ee59f8db8dda04b226df682a915d7f67e8858da6b69c4

Both reports bind task WB-001 and the accepted spec/plan digests listed above. Every case's reported source digest was compared with `git show` at its recorded source commit, without mismatch. The updated new-test bytes are identical between second red and candidate final green, SHA-256 196941a78bc0cf6560740ad735db1dcb5417998ede463f1e46072212ce012643. The original valid red run ec50d7d6193f4b72b79a3d8f975666d4 and first green bc215f3cafbc4b2c9bb5c517a1df1804 remain retained history; the fresh TaskResult accurately cites the second red and exact revised candidate green. No exemption is requested or required.

## Suggested fixes

None required before WB-001 integration. Optional test strengthening: retain a distinct foreign-only association in the permanent fixture and assert a nonempty dependency list. Current foreign isolation behavior was independently checked and these suggestions are not blocking findings.

## Residual risks

Approval is limited to this task's graph/relationship projection. Branch/revision selection and matching runtime/evidence context remain WB-002/WB-003 obligations; UI presentation, lazy evidence/source loading, end-to-end journeys, performance and full Verify remain later gates. Integrated runtime status remains attributed to task-state and does not assert global verification. The model's declared lifecycle and missing history remain separate. This artifact supplies an independent decision; the coordinator must bind it to the exact TaskResult/candidate before integration.

## Review verdict

verdict: APPROVED

boundary: ok

Both prior blocking findings are resolved with discriminating behavior-red and exact-candidate green evidence. No implementation edits or commits were made by this reviewer.
