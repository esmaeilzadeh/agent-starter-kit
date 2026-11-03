# Task 2 test classification amendment

## Proposed change

Keep the specification, all nine Task 2 scenarios and assertions, source bindings,
runners, task ownership, and acceptance criteria unchanged. Reclassify cases
`2/1` through `2/9` in `test-plan.json` from `new` to `regression`.

## Evidence and reason

The task-scoped Red run `05de91f7c0144d358c609ec49988adfd` executed all three
Task 2 runners at the accepted pre-implementation baseline
`c8a5ea24821b0f984f4e9d7ddee38714d4409d16`. All nine mapped cases passed with
no source changes. The run is captured under
`work/shorter-hashes/traceability/runs/05de91f7c0144d358c609ec49988adfd/`.
The existing identity, immutable-store, and compact-codec behavior is already
present at this task's base, so these assertions must be treated as preserved
regressions; no failing behavior or implementation change should be fabricated.

## Invariants

- The canonical specification, What, Why, assumptions, and acceptance criteria remain unchanged.
- Every case retains its scenario, assertions, source bindings, runner, and task owner.
- Only `2/1` through `2/9` change classification; TaskGraph is unchanged.
- All nine cases require current final Green evidence as regressions.
- The amendment requires exact-revision independent review and renewed accepted-tests authority.

## Decision

This is a planning classification correction based on observed baseline evidence.
It does not change product behavior or the accepted intent. The user has already
authorized continuation through final acceptance; continue after independent
review and registration of this amendment.
