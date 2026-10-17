# WB-001 traceability semantic-review gate diagnostic

- Reviewer: /root/review_wb001
- Model: gpt-6-astra; runtime: codex; parent_model: gpt-6-luna
- Candidate: 0b14c15317d90c94435b045924d77adb304795ea
- Task base: 822c24338765f00cc66b189d863e247a2b688d38
- Accepted contract/inventory base: 897cb40a8362aed3d5858a4e105b9a374480fcc5
- Existing candidate review remains **APPROVED / boundary ok** in WB-001-review-0b14c15.md.

The candidate-bound behavioral run 6ac33e168a104cf89ee5ff989aa33346 passes the 25 WB-001 cases. This does not supply assertion/source review for the later tasks' unimplemented cases.

## Missing committed sources

Checking every unique accepted-plan source with `git cat-file -e <candidate>:<path>` identifies nine absent files supporting 20 later-task cases:

- _ask/tests/test_engineering_workbench_attention.py
- _ask/tests/test_engineering_workbench_browser.py
- _ask/tests/test_engineering_workbench_evidence.py
- _ask/tests/test_engineering_workbench_navigation.py
- _ask/tests/test_engineering_workbench_overview.py
- _ask/tests/test_engineering_workbench_performance.py
- _ask/tests/test_engineering_workbench_sources.py
- _ask/tests/test_engineering_workbench_tasks.py
- _ask/tests/test_engineering_workbench_tests.py

These are planned WB-002–WB-009 obligations. Their absence does not contradict WB-001's accepted ownership boundary.

## Gate references and reproduced failure

- `.agents/ask/verification/traceability/evidence.py:102`: `source_digests(root, sha, plan)` reads every source path from every planned test, without task filtering.
- `evidence.py:17`: `read_at` raises `Invalid` if the committed source is absent.
- `evidence.py:145`: `review_errors` requires that full-plan source-digest map.
- `evidence.py:160`: semantic review requires exactly all 12 criterion IDs and all 57 test IDs.
- `evidence.py:162` and line 170: every criterion/type and test must be APPROVED with substantive assessments.
- `.agents/ask/verification/traceability/completion.py:41`: completion also computes full-plan source digests after selecting scoped execution tests.
- `completion.py:54`: task completion invokes the same unscoped `review_errors`.

Read-only invocation of the actual source-digest helper against the exact candidate raises:

```text
Invalid migration_required: missing _ask/tests/test_engineering_workbench_sources.py at 0b14c15317d90c94435b045924d77adb304795ea
```

The actual `inventory(root, accepted_contract_sha, candidate_sha, plan)` result is:

```json
{"inspected_sources": [], "changed_cases": [], "unmapped_cases": [], "behavior_changes": []}
```

That empty Python inventory is correct: the resumed candidate changes only the authorized shell static check. The shell check is separate from the 57 mapped Python cases and was independently verified in WB-001-review-0b14c15.md.

## Conclusion

The current unscoped semantic gate cannot record a valid full review for this WB-001 candidate. Missing sources have no honest source digests or implemented assertions to approve. Adding approval prose, invented digests or empty future test stubs would not establish the accepted future behaviors.

Integration requires a reviewed contract/runner change that applies the appropriate task scope while preserving full workstream gates, or actual implementation of every future source and its substantive assertions before the unscoped review can be satisfied. This diagnostic changes no approval, contract, runner, source or integration state. No fabricated full semantic review was written.
