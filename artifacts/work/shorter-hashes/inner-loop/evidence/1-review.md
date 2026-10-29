# Task 1 independent review — round 2

Reviewer: `/root/cont_review`, independent Codex Sol reviewer as assigned by coordinator.
Runtime: Codex. Exact inherited model identifier and parent model not supplied to reviewer.
Base: `813b971e387547248037ee972bbafd26e2110188`.
Candidate: `0e4c484641938c79ee2e7e2f08b609db2c654e14`.

## Scope and boundary

Re-read canonical 07-review instructions and reviewed accepted plan/spec obligations, cases 1/1 and 1/2, task graph/TaskResult, full candidate implementation/tests, frozen corpus and recorded Red/Green results. Inner-loop status confirms task 1 as current writer.

The complete base-to-candidate changed path list contains only `.agents/ask/workflow_refs/benchmark.py` and `_ask/tests/test_workflow_refs_baseline.py`; both match task 1 owned_paths. Boundary: **ok**. No extras or glob_too_narrow condition.

Round-1 rejection is preserved as `1-review-round-1.md`.

## Previous R1 correction

R1 is resolved in production. The baseline now projects the first task's complete selected test records, relevant obligations and runners, corresponding specification criteria, first task YAML context and plan row plus selected specification/authority context. Unrelated WB-002 through WB-009 material is removed from the review context. Complete frozen source bytes remain independently verified before projection. Historical plan decision/accepted pins, completion/run report and selected log bytes remain represented, without relabeling historical outcomes. No production regression found in this correction.

## R2 — Local structural suggestion: assert complete selected evidence against frozen source

Location: `_ask/tests/test_workflow_refs_baseline.py`, `test_equivalent_questions_and_lookup_accounting`, especially the assertions after parsing task_plan.

The test derives selected_ids from the projected scope, then compares projected tests against those IDs. It derives selected_criteria and runner IDs from the projected tests, then compares projected obligations/runners against those derived sets. This verifies internal consistency and removal of known unrelated material, but not preservation of the actual frozen scope or complete evidence records.

Concrete counterexample: deleting `expected_assertions`, `scenario`, or `source_paths` from each projected selected test leaves all these assertions passing. Likewise, removing an assigned test consistently from projected scope/tests can evade this check. That violates the case's required check that all mapped tests/obligations and recorded evidence survive projection. Current production retains the records on inspection, but this important contract lacks an independent assertion.

Required local correction: derive the expected first scope and full selected tests/obligations/runners from `git_blob(BASELINE_SOURCE, original_path)` or another independently frozen source, then compare complete projected records with those originals, including full test fields and relevant authority/context. Cover resume as well as review; the current selective assertions only inspect review. Keep the unrelated-task exclusions and tokenizer/accounting checks. No change to What/Why or task ownership is needed. Request fresh candidate-bound review after the test correction. This is a task-local test assertion improvement, not a claim that current production drops evidence.

## Integrity, tokenizer and accounting

Whole corpus bytes and sizes are checked against pinned SHA-256 values from the sealed manifest before use. Sources come from the exact frozen Git revision with no checkout fallback. Manifest/requirements/source/workload identities remain pinned. Tokenizer version, encoding and encode_ordinary operation are checked. Question/source labels and projected context feed per-journey token counts; the total is explicitly asserted as the sum. Unique metadata JSON paths remain deduplicated separately from transcript selection. Direct corrupt/missing source regressions now exercise source refusal with the unchanged manifest.

Task 1 establishes measurement inputs and unique metadata totals; candidate savings and generated-output accounting remain task 10 obligations.

## TDD evidence and assertion continuity

Reviewed Red run `997aae92aba3461a95d9bf085bea0025`, exact source `c97d9973d42754cdc77f86889ee7cbe9419052a6`: case 1/1 passed, case 1/2 failed as behavior_assertion for unrelated whole-file projection. Collection succeeded, exit code 1. This directly targets original R1.

Reviewed final Green run `b371c2a2487441318973c7bf26ef0525`, exact current candidate: both mapped cases passed, collection succeeded, exit code 0. TaskResult matches these records. From this Red revision to Green, test changes add direct corrupt/missing blob refusal assertions; projection assertions were preserved without weakening. The initial Red/Green cycle for basic baseline capture remains historical evidence from round 1.

No executable tests were independently run by this reviewer. Recorded case reports and test sources were inspected.

## Other finding classes

No new existing-spec production behavior defect, broader horizontal refactor, required redesign, or evidence-backed withdrawal. R1 was corrected, not withdrawn. No parked handoffs. Refactor outcome is structurally reasonable, subject to completing R2.

## Verdict

**REJECTED** for exact candidate `0e4c484641938c79ee2e7e2f08b609db2c654e14`.
Boundary: **ok**. Required task-local suggestion: **R2**. Production correction of R1 is confirmed.
