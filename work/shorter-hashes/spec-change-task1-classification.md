# Task 1 test classification amendment

## Proposed change

Keep the specification, scenario, assertions, source bindings, runner, and task
scope unchanged. Reclassify test case `1/2` in `test-plan.json` from `new` to
`regression`.

## Evidence and reason

Case `1/2` passes at the pre-implementation Task 1 Red revision
`f6d6791cbdfe985c89df38226808ebb86968bc3b`, run `186cc05d0e7c433e8fc63e2bb619994d`.
The captured result classifies `1/2` as passed while `1/1` fails on its new
behavior assertion. Case `1/2`'s mapped baseline projection and lookup-accounting
behavior was already present at Task 1's base, so it does not need a fabricated
Red. Case `1/1` remains `new` and retains its behavior Red plus current Green.

## Invariants

- The canonical specification and all acceptance criteria remain unchanged.
- Case `1/2` keeps its scenario, assertions, sources, runner, and task owner.
- TaskGraph and all other case classifications remain unchanged.
- Case `1/2` still requires current Green evidence as a regression.
- Case `1/1` still requires recognized behavior Red and current Green.
- The plan amendment needs an independent exact-revision review and renewed
  coordinator accepted-tests authority before task execution resumes.

## Decision

Authorized under the user's direction to continue the workstream through final
acceptance. Record the classification correction as a plan amendment; no product
What, Why, assumptions, or acceptance criteria change.
