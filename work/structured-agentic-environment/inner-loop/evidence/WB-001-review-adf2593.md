# Independent review: WB-001 with explicit baseline acknowledgments

## Attribution and exact identities

- model: gpt-6-astra
- runtime: codex
- parent_model: gpt-6-luna
- reviewer: /root/review_wb001
- work_id / task_id: structured-agentic-environment / WB-001
- task base and candidate_sha: adf259305d38074e509fc0a5f05d6c967e45dd8c
- accepted contract / semantic inventory base_sha: 55c11fad3e0391f8a47236166c8d5941d824ef73
- TaskResult: work/structured-agentic-environment/inner-loop/results/WB-001.json
- TaskResult SHA-256: 2a1512b14efdaa5a4ad5b92945a4b4db7d718511c5b963d2f5ed7e0e01b85fb0
- spec_digest: f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb
- plan_digest: 4845c9f46fb7ecfe4f368e006c1a8d89b2f7c3ea5beefe1478b08ea184eb09e8
- graph_digest: eea31a815b6b3857f1cbbe2bddd7b820cd0e4c62c89a73d822c96af502aac606

## Scope and boundary

boundary: ok

The current writer's task base equals the candidate, so its source diff is empty. The implementation was committed and independently reviewed in the preserved ancestry. The fresh accepted pin and candidate supply authority for this attempt; no prior TaskResult or review is silently rebound.

Actual Python inventory from accepted contract to candidate is inspected_sources=[], changed_cases=[], unmapped_cases=[], behavior_changes=[]. Task ownership and accepted contract definitions were checked. No extra source path or required out-of-boundary fix was identified.

The projection implementation and workbench cases are byte-identical to previously independently approved candidates 69cfc37/0b14c15. The shell static test is likewise unchanged. All six selected mapped test/fixture source digests match the earlier independently assessed source and the new exact-candidate execution. Prior detailed case assessments therefore remain applicable after fresh source verification.

## Source and behavior findings

No blocking source findings remain for WB-001.

The canonical criterion join preserves CASE-2 scenario membership without a redundant model test node. Graph task scopes remain executable ownership authority; shared test memberships produce separately labeled scenario-coverage links and deduplicated canonical test records. Current-work specification/test-plan paths prevent foreign reused identities from joining. Explicit implementation associations survive in model-only task rows without fabricating runtime status or completion. Recorded story membership and missing story membership remain separate.

Missing task runtime records are planned or explicitly not-recorded. Declared model lifecycle/readiness, graph ownership and actual integration status remain distinct from proof of workstream completion. The independently checked ASK_WORK_ID reset applies only to the two synthetic shell invocations; its original assertions and production precedence remain intact. That shell support test is not represented as one of the 57 mapped Python cases.

The accepted verification amendment independently reviewed at 55c11fa allows only explicit task-scoped baseline-regression acknowledgments. Current semantic validation enforces whitelist membership, classification new, source existence/equality for every referenced path, reviewer acknowledgment, rationale and approval. Full-workstream review rejects this exemption. The completion evaluator rejects combining a recognized red with an exemption for the same case, and preserves nested task/workstream scope binding.

## Exact 22-case exemption decision

This reviewer independently approves `kind: baseline-regression`, `reviewer_ack: true`, with a substantive per-case rationale, for exactly these accepted WB-001 IDs:

MV-valid, MV-graph, MV-fields, MV-refs, ME-decision, ME-revise, ME-reject, ME-race, EV-real, EV-missing, MP-shared, MC-journey, DG-pre, DG-post, DG-refs, DG-events, DG-parity, DG-publish, DG-bootstrap, ME-batch, DG-success, DG-entrypoints.

For each of the 22 cases, this review checked:

- It is explicitly listed in `test-plan.json.task_scoped_baseline_regression_exemptions.WB-001` and assigned to WB-001.
- Its accepted change_kind remains new; no regression reclassification was used to conceal missing historical red.
- Every referenced source exists in accepted contract 55c11fa and candidate adf2593, with byte-for-byte equality, including the shared engineering_fixture.py path.
- The exact-candidate final-green run passes its qualified selector with matching source digests.
- It has no recognized behavior-red in the current-plan replay reports; the acknowledgment does not claim red history.

The five foundation test modules/fixture sources are engineering_fixture.py, test_engineering_model.py, test_engineering_cli.py, test_engineering_evidence.py and test_engineering_guard.py. Their exact digests are bound in the semantic JSON. The three workbench cases are excluded from the exemption list and have no exemption field.

The substantive assertion/counterexample assessments from the previous independent review are retained after source equality checks: foundation cases exercise typed graph and reference errors, semantic history/blockers, stale/concurrent edits, real/tampered/missing/historical evidence, shared projections, CLI persistence, and pre/post validation with coherent publication. Their unchanged assertions provide regression protection for the task. These acknowledgments do not resolve their missing historical red for final workstream verification.

## Replayed red and fresh green evidence

All three reports use the current accepted spec and plan digests, scope=task and task_id=WB-001. All retained log digests and every reported case source digest were independently compared to the log bytes and historical/current committed source. No mismatches were found.

### Original behavior replay

- Run: 687db2a7e2c245f4acd492f40e8f256b
- source_sha: c8d97cb89270da80bb8e34756745da7e9ac3e6b0
- phase red; collection_status ok; exit_code 1
- 25 cases: 22 passed and all three WB cases failed with failure_kind behavior_assertion.
- Log: work/structured-agentic-environment/traceability/runs/687db2a7e2c245f4acd492f40e8f256b/e033bdd5301d4beea9e4b0bf91152cc6.log
- Verified log SHA-256: e45e02a1c01d60eec70a2bf30d8b779147cb36991d02236357ee6de0a0eabc75

This executes the actual committed historical failing assertions through the current accepted runner. Original retained reports remain history; no outcome or digest was edited to simulate replay.

### Discriminating repair replay

- Run: aeb93ef0906243a0a534b89395117e21
- source_sha: 912e0599bcb079307512f3dbdcc7de13e31417bb
- phase red; collection_status ok; exit_code 1
- 25 cases: 23 passed; WB-relations and WB-task-history failed with failure_kind behavior_assertion; WB-story-context passed.
- Log: work/structured-agentic-environment/traceability/runs/aeb93ef0906243a0a534b89395117e21/c6a4379df18f4f5991b011fa6971ff50.log
- Verified log SHA-256: b573c8ce302c831adc5f34654552b515b42a880593cc8da89dede03c998320e2

The retained repair assertions discriminate canonical-only CASE-2/s2 membership and model-only legacy s3 relationships. Repair-red mapped test bytes match current source; the later implementation fixes both gaps. WB-story-context retains its original behavior-red continuity rather than receiving an exemption.

### Exact candidate green

- Run: f9a238a1b5db4473b0c7af44dd6d1b32
- candidate/source_sha: adf259305d38074e509fc0a5f05d6c967e45dd8c
- phase final_green; collection_status ok; exit_code 0
- All 25 assigned cases passed.
- Log: work/structured-agentic-environment/traceability/runs/f9a238a1b5db4473b0c7af44dd6d1b32/6fc9647653984e8ba76b6801839440f8.log
- Verified log SHA-256: 3fb8aac5bfd3316264f6279712536037033700d85d1c735110c409b9cdc43110

The TaskResult's red/green narrative agrees with these replay and current-candidate reports. Source ancestry is preserved; no missing import, collection error or missing selector is treated as a behavior-red.

## Semantic review artifact and checks

Artifact: `work/structured-agentic-environment/traceability/review-input-WB-001-adf2593.json`.

It is ask-test-review/v2, task-scoped to WB-001, with exactly 25 selected test IDs, seven criterion IDs (EM-001, EM-002, EM-003, EM-004, EM-007, EM-008, EM-010), matching selected source digests, exact accepted inventory base, per-criterion/type adequacy, per-case assertion assessment/counterexample/continuity and exactly 22 explicit exemptions.

The actual read-only `review_errors` validator returns []. In-memory counterexamples removing reviewer acknowledgment, emptying rationale, rejecting the exemption decision, or adding an exemption to a nonwhitelisted WB case all reject. No coordinator record-review/integration operation was performed.

## Verdict and remaining limits

verdict: APPROVED

boundary: ok

The bounded WB-001 source, assertions, genuine WB red/green continuity and exact task-only baseline acknowledgments are approved for this candidate and TaskResult. No blocker remains in this independent task review. The coordinator must still record the exact artifacts and execute its integration gates.

The 22-case historical TDD gap remains a final workstream limitation. Full-workstream review and completion cannot use these task-only acknowledgments. Later tasks, full Verify and Accept are outstanding. This reviewer changed only review artifacts and made no source edits, commits or coordinator decisions.
