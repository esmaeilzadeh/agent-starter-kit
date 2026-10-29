# Task 1 independent review — round 4

Reviewer identity: `/root/cont_review`, independent Codex Sol reviewer as assigned by coordinator.
Runtime: Codex. Exact inherited model identifier and parent model not supplied to reviewer.
Base: `813b971e387547248037ee972bbafd26e2110188`.
Candidate: `eb39360ebe9d6609991a11b92981c62df3f8d62e`.

## Scope and boundary

Reviewed current candidate against canonical 07-review protocol, accepted Task 1 plan, SH-11/SH-12 obligations for cases 1/1 and 1/2, task graph, TaskResult, full implementation and tests with successive corrections, frozen source contract, and exact-candidate execution evidence. Inner-loop status identifies task 1 as the current writer.

Complete base-to-candidate changed paths:

- `.agents/ask/workflow_refs/benchmark.py`
- `_ask/tests/test_workflow_refs_baseline.py`

Both match task 1 owned_paths. Boundary: **ok**. No extras or glob_too_narrow condition. Earlier rejection evidence remains unchanged in its existing files.

## Findings and corrections

No unresolved findings.

R1 is resolved by implementation: verified whole-file corpus inputs remain available to tools, while resume/review agent transcripts receive the declared selective first-task projections. Required tests, obligations, assertions, runners, selected criteria, plan/task context and authority remain available. Unrelated WB-002 material and resume's approval-checkpoint task are excluded. Historical completion results and selected log remain historical and retain full evidence; no status is relabeled.

R2 is resolved by the strengthened independent assertions. Review projection objects are compared in full against selected immutable Git records for WB-001 scope/tests/obligations/runners and relevant spec criteria. Resume now also compares complete scope/tests/obligations/runners to immutable source records, excludes approval-checkpoint from transcript/plan text, and compares approval and accepted identities with frozen originals. Deleting mapped test records, expected_assertions, scenarios or source paths will fail these equalities. Complete historical run content is compared with its frozen original.

Both findings were corrected rather than withdrawn. No new local structural suggestions, existing-spec behavior defects, broader horizontal refactors, required redesigns or evidence-backed withdrawals. No parked handoffs.

## Task criteria, source integrity and accounting

Case 1/1 verifies repeated deterministic capture of all three frozen journeys, source/tokenizer identity and unique metadata totals; changed contract/workload/tokenizer inputs refuse. Direct corrupt/missing source reads exercise integrity refusal without merely changing the manifest.

Case 1/2 independently checks frozen source byte sizes/hashes, projected question/context/source labels, complete selected evidence preservation and unrelated-task exclusion, exact historical run content, selected log inclusion and token totals. Complete selected records preserve assertion and source lineage fields. Approval and accepted authority are retained, not recreated.

Production pins manifest and requirements SHA-256, source revision and workload. Every corpus file is read from the exact Git revision and byte/hash/UTF-8 checked before projection. It does not fall back to checkout files. Tokenizer package version, encoding and encode_ordinary operation remain fixed. Per-journey transcripts include question/source labels; aggregate token count is asserted as their sum. Metadata totals deduplicate original JSON metadata paths independently from prose/YAML/log inputs and projected agent context. Task 10 retains candidate-output generation and strict aggregate savings obligations; Task 1 does not claim savings.

## TDD and exact-candidate evidence

Original baseline-capture Red behavior failures and initial Green remain documented in earlier rounds. R1 correction Red `c97d9973d42754cdc77f86889ee7cbe9419052a6`, run `997aae92aba3461a95d9bf085bea0025`, records case 1/2 failing as behavior_assertion for unrelated whole-file projection and case 1/1 passing, with successful collection and exit 1.

Final Green run `349aa070578a47b986ac49746557c627` is bound exactly to reviewed candidate `eb39360ebe9d6609991a11b92981c62df3f8d62e`. Both mapped cases passed, collection succeeded, exit 0; the recorded log digest matches its bytes. Test changes strengthen complete-evidence preservation and source refusal without weakening Red assertions. R2 adds assertions for already-correct behavior, so no manufactured additional behavior Red is required.

No tests were independently executed by reviewer; immutable case reports, log integrity and source/assertion continuity were inspected. The no-further-cleanup refactor result is reasonable for this cohesive reader/test task.

## Residual limits and verdict

This review approves Task 1 measurement foundations, not later identity/catalog implementation or final aggregate savings. Coordinator CheckPlan integration and outer verification remain separate.

**APPROVED** for exact candidate `eb39360ebe9d6609991a11b92981c62df3f8d62e`.
Boundary: **ok**. R1 and R2 resolved; no blocking findings.
