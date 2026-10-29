# Task 4 independent review — round 5

Reviewer: independent Codex reviewer; runtime: Codex. Exact model and parent identifiers are not exposed in this child context.
Candidate: `d5b8b002796830e33115dac394ad071d08165e9e`.
Prior approved candidate: `4c6f32f3f4437d042681be0a93fff76a3341d0f3`.
Task base: `16b699cbcc253d0873cd58aee6e773ab373a6f28`.
Accepted contract: `02ad31b6e5ef5130986a920f943788cbbe970631` (revision 7).
Coordinator-reported Red run: `0b30a4495a4145dfbc8e47bf4e6973a8` (mapped behavior assertions failed, including 4/7).
Coordinator-reported Green run: `a60d388bf4784f4ca22a885cfe933133` (all seven mapped cases passed).

## Scope and boundary

Reviewed the exact candidate and its direct delta from the prior approved candidate, the Task 4 implementation and tests, mapped cases 4/1–4/7, and prior rounds' findings R1–R6. Base-to-candidate changes are limited to `.agents/ask/workflow_refs/project.py`, `.agents/ask/workflow_refs/impact.py`, `_ask/tests/test_workflow_refs_project.py`, and `_ask/tests/test_workflow_refs_impact.py`, all owned by Task 4. The direct delta from `4c6f32f` is the new 4/7 assertion in the impact test module. Boundary **ok**; no extras and no `glob_too_narrow` condition.

## Added 4/7 regression

The test changes an authority catalog snapshot to a nonexistent full commit ID, then requires `load_project_graph` to return `incomplete` with an `unresolved` entry whose reason is `discovery_incomplete`. It catches unexpected exceptions into a result with status `error`, which fails the status assertion. The candidate implementation catches Git lookup/read failures in `_regular_file_at`; `load_project_graph` converts that `ProjectError` into the scoped unresolved result. This distinguishes a missing pinned Git object from an ordinary available-source deletion.

## Prior findings R1–R6

- **R1 — resolved.** Catalog-authoritative source discovery binds the graph to captured refs. Candidate-only dependencies are represented and traversed without changing historical pins; unregistered candidate revisions refuse complete clearance. Missing pinned objects produce incomplete discovery.
- **R2 — resolved.** Live/archive catalogs are attached to their owner, while shared owners require explicit registration.
- **R3 — resolved.** Loose and packed owner refs, selected integration/archive refs, and movement logs are included in capture consistency checks. The unlogged selected-ref advance-and-return case reports incomplete.
- **R4 — resolved.** Retain decisions are checked against captured context, required paths, authority, and exact scope; only named eligible consumer edges are stopped. The regression shows unrelated Y remains affected when X is named.
- **R5 — resolved.** Traversal preserves distinct converging input paths through the affected descendants.
- **R6 — resolved.** Explicit inactive state remains inactive; available deletion and unavailable source/object are distinct; retirement preserves history and is blocked by remaining active consumers.

## Independent execution

On exact candidate `d5b8b00`, ran both Task 4 modules with `PYTHONPATH=.agents/ask`: both project tests and all five impact tests passed. This independently exercises the new 4/7 assertion and applicable R1–R6 regressions. The coordinator-reported exact-candidate Green run covers all seven mapped cases. No source files were changed during review.

## Findings and verdict

No remaining existing-spec behavior defect or task-local structural suggestion found. No broader horizontal refactor, required redesign, evidence-backed withdrawal, or parked handoff.

**APPROVED** for exact candidate `d5b8b002796830e33115dac394ad071d08165e9e`. Boundary **ok**. The new missing-object regression is behavior-based and passes; applicable R1–R6 repros remain addressed.
