# Task 1 independent review — round 3

Reviewer: `/root/cont_review`, independent Codex Sol reviewer as assigned.
Runtime: Codex; exact inherited model and parent model identifiers not supplied.
Base: `813b971e387547248037ee972bbafd26e2110188`.
Candidate: `8d6b3d9729b772c31557ebebae61a0b237704f3d`.

## Scope and boundary

Reviewed the complete candidate against accepted Task 1 outcomes and cases 1/1 and 1/2 (SH-11/SH-12), with full production implementation and incremental test changes since round 2. Rechecked task status, TaskResult, frozen source expectations and exact-candidate Green results. Changed paths remain only benchmark.py and test_workflow_refs_baseline.py in their declared locations, both within Task 1 owned_paths. Boundary: **ok**.

## Findings

R1 remains resolved: production uses selective projections, retains complete selected records and authority, excludes unrelated review tasks, verifies whole sources independently and separates transcript selection from unique metadata totals.

The main R2 counterexample is now resolved for the review journey. Expected complete WB-001 scope, selected tests, obligations, runners and criteria are derived from frozen Git originals and compared as complete objects. Dropping expected_assertions, scenarios, source paths or mapped records will now fail. Complete historical run contents are likewise compared with the original.

### R2 remainder — local structural test suggestion

The earlier round also requested equivalent assertions for resume. The current tests still inspect complete projection objects only for review; resume checks question/labels/source paths and token counts without comparing its selected first scope, complete test records, obligations/runners and relevant authority with frozen originals or proving exclusion of its unrelated task row/tests. Since the frozen three-question contract covers resume as well, complete that local assertion correction and request a fresh exact-candidate review. Production shares the projection helper and appears correct on inspection; this is a test coverage gap, not a newly discovered production regression or redesign request.

## TDD and checks

Red revision `c97d9973d42754cdc77f86889ee7cbe9419052a6`, run `997aae92aba3461a95d9bf085bea0025`, genuinely fails case 1/2 with behavior_assertion for unrelated task projection, while case 1/1 passes. Current final Green run `20cdea6e38f4408c8abddd37d609f870` binds exactly to `8d6b3d9729b772c31557ebebae61a0b237704f3d`; both mapped cases pass. New assertions strengthen preservation rather than weaken earlier Red assertions. No independent executable run was performed by reviewer.

Source/hash/tokenizer guards, corrupt/missing source refusal, per-transcript counts, aggregate token assertion and deduplicated metadata accounting remain sound on inspection. Task 10 retains aggregate savings/output accounting obligations.

No broader refactor, required redesign or withdrawn finding. Prior evidence files remain unchanged. No parked handoffs.

## Verdict

**REJECTED** for exact candidate `8d6b3d9729b772c31557ebebae61a0b237704f3d`.
Boundary: **ok**. Remaining required local suggestion: **R2 resume assertions**.
