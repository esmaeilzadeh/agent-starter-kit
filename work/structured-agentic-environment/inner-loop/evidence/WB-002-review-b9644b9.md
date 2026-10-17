# Independent review: remediated WB-002

## Attribution and exact identities

- model: gpt-6-astra
- runtime: codex
- parent_model: gpt-6-luna
- reviewer: /root/review_wb001
- work_id / task_id: structured-agentic-environment / WB-002
- task base_sha: adf259305d38074e509fc0a5f05d6c967e45dd8c
- candidate_sha: b9644b94da99dc6752a5f5a01cdd59e3e19d74a6
- accepted contract / semantic inventory base_sha: 55c11fad3e0391f8a47236166c8d5941d824ef73
- TaskResult: work/structured-agentic-environment/inner-loop/results/WB-002.json
- TaskResult SHA-256: 9120beecd8d0e4b5f0c9c6f9ca790991d6a72197e652f74076ff27253851a3e7
- spec_digest: f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb
- plan_digest: 4845c9f46fb7ecfe4f368e006c1a8d89b2f7c3ea5beefe1478b08ea184eb09e8

## Steering boundary

boundary: ok

The candidate's implementation remains bounded to workbench_sources.py and test_engineering_workbench_sources.py, the two assigned WB-002 paths. Relative to rejected candidate 43d5138, only these files change: a pre-enumeration guard and one discriminating test extension. Prior archived task results, reviews and execution reports remain runtime evidence exceptions. Candidate ancestry from the recorded task base was verified.

Semantic inventory from the accepted contract contains exactly those two inspected Python sources, changed_cases=[WB-inventory, WB-snapshot, WB-source-errors], no unmapped cases and no exclusions. All three planned cases retain classification new and receive no exemptions.

## R1 resolved: no external read through symlinked .later root

At `_ask/scripts/engineering_model/workbench_sources.py:83`, `_later_cards` now returns an empty inventory when the .later directory itself is a symlink, before iterdir or content reads. The per-card direct-symlink guard remains intact. This removes the original ancestor-symlink path to external Markdown titles.

At `_ask/tests/test_engineering_workbench_sources.py:72`, the existing inventory case now replaces its normal parked-card directory with a symlink to a separate temporary directory containing a private Markdown heading. The result must have an empty later collection. The original inventory assertions remain unchanged.

Independent instrumented reproduction created the same outside directory and symlink and wrapped Path.iterdir and Path.read_text to reject unsafe directory enumeration or content access. discover_work returned later=[], neither wrapper observed any unsafe operation, and Git HEAD/refs were unchanged. This confirms the fix prevents the external reads, rather than merely hiding their returned title. Only disposable test-owned files were used.

No blocking findings remain in this bounded review. Raw committed SourceSnapshot data remains distinct from validated Engineering Model admission; downstream integration must use the existing document layer and revision-matched reference closure. The snapshot fixture could optionally capture HEAD/refs/files before its first read rather than afterward; direct implementation inspection and independent checks show no mutations, so this test strengthening is not blocking.

## Assertion and criterion/type review

- WB-inventory / EM-009 integration: retains correct current/task/live/archive/missing-model/parked/detached/gitless assertions and now discriminates the previously rejected external directory symlink. Approved.
- WB-snapshot / EM-009 integration: unchanged full-SHA, coherent model/graph/plan/requested-source, explicit refresh and immutable captured-byte assertions remain valid. Source implementation uses read-only Git commands and exposes no admission/edit operation. Approved.
- WB-source-errors / EM-009 unit: unchanged missing-blob/model, traversal and committed symlink assertions remain valid; the inventory regression now covers the complementary ancestor-directory path. Approved.

These decisions cover the assigned EM-009 source/inventory slice, without claiming later UI navigation or full workstream completion. The optional shell/static checks and other tasks' assertions are outside these three mapped cases.

## Genuine evidence and TDD continuity

The original valid feature-red run 5aaefa45ffdc4d50a057bb88c8ae150d at fb3bb24cc0a893c8af47e8014055da09d9beee55 failed all three task cases by behavior_assertion with valid collection. Its log and source identities were independently checked in WB-002-review-43d5138.md. That original record is retained; the earlier runtime-error attempt 29bba382314d4f2a920fe6322605669d remains excluded.

Repair-red run: b8eabe0b113c4923a40aa8a7e8d364a0.

- source_sha: 019dad0322154e4eeb028c8b1935b02f9b593ac4
- phase red; collection_status ok; exit_code 1
- WB-inventory fails by behavior_assertion on the external card returned through .later; WB-snapshot and WB-source-errors pass.
- Log: work/structured-agentic-environment/traceability/runs/b8eabe0b113c4923a40aa8a7e8d364a0/635af7b88ef74e27a6892352cdbaa64d.log
- Verified log SHA-256: e953f509dab0e660e310d2a9daebd6f12ce096dca067aef8945f5cbf85542b8d

Exact candidate green: 16738323cd53448d9dc1c0659a589956.

- candidate/source_sha: b9644b94da99dc6752a5f5a01cdd59e3e19d74a6
- phase final_green; collection_status ok; exit_code 0
- All three assigned cases pass; log concludes 3 tests in 0.356s / OK.
- Log: work/structured-agentic-environment/traceability/runs/16738323cd53448d9dc1c0659a589956/aa9c929d4d14495bacccd38385f3670c.log
- Verified log SHA-256: a9ba6f3ef36ea858ed9a0bf69ba8def6ccc49c9153472a783a4d11ff122436f8

Both repair reports bind the current accepted spec/plan digests and task WB-002. Every reported source digest matches the appropriate committed source; retained log bytes match their recorded digest. The test file is byte-identical between repair-red and current green, SHA-256 4ac7243bb39e4e15bdd377adc101a1ff89496cfef65ee56748907622d15dec3e. Snapshot and source-error methods/assertions are unchanged when the inventory regression is appended. The TaskResult accurately describes the repaired seam and evidence. No outcome or red history was fabricated.

## Semantic artifact and verdict

Artifact: `work/structured-agentic-environment/traceability/review-input-WB-002-b9644b9.json`.

It supplies task-scoped ask-test-review/v2 with exactly the three accepted WB-002 tests, EM-009, accepted inventory base, source digest, TaskResult digest and substantive criterion/type and per-case assertion/counterexample/continuity assessments. The read-only review_errors validator returns []. This reviewer did not record the coordinator decision or integrate the task.

verdict: APPROVED

boundary: ok

R1 is resolved with discriminating behavior-red and exact-candidate green evidence plus an independent no-external-read check. No source edits, coordinator-state changes or commits were made. Coordinator recording/integration and later workstream gates remain separate.
