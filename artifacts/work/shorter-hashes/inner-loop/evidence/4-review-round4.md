# Task 4 independent review — round 4

Reviewer: independent Codex Sol reviewer; runtime: Codex. Exact parent/model identifiers are not exposed in this child context.
Candidate: `4c6f32f3f4437d042681be0a93fff76a3341d0f3`.
Previously approved ancestor: `27dd8ac9194bead5dc927971cac58c6b6ee55fc6`.
Task base: `16b699cbcc253d0873cd58aee6e773ab373a6f28`.
Accepted contract: `02ad31b6e5ef5130986a920f943788cbbe970631` (revision 7).
Exact final Green traceability run reported by coordinator: `74ed1bdc47984e10bac920b3f72f4fe8`; all seven mapped Task 4 cases passed.

## Scope and boundary

Reviewed the exact candidate tree, its delta from the prior approved candidate, the full Task 4 implementation and tests, cases 4/1–4/7, and the round 1–3 findings. The base-to-candidate paths remain `.agents/ask/workflow_refs/project.py`, `.agents/ask/workflow_refs/impact.py`, `_ask/tests/test_workflow_refs_project.py`, and `_ask/tests/test_workflow_refs_impact.py`; all are within Task 4 owned-path globs. The direct delta from `27dd8ac` changes only assertions in `_ask/tests/test_workflow_refs_project.py`. Boundary **ok**; no extras and no `glob_too_narrow` condition.

The changed assertions still fail if candidate input discovery or the unregistered-candidate list is absent or wrong. The unavailable-source test converts an unexpected exception into a result with status `error`, which fails the asserted `incomplete` status; it also asserts the scoped `discovery_incomplete` reason.

## Prior findings R1–R6

- **R1 — resolved.** Source-bound catalog graph loading validates committed sources and dependencies. Candidate-only inputs are separately represented and traversed while old pins remain unchanged; unregistered candidate revisions refuse complete assessment. A missing pinned object is reported as incomplete discovery, with an exact regression.
- **R2 — resolved.** Ordinary live/archive catalogs remain attached to their owner; true shared registrations remain explicit.
- **R3 — resolved.** Loose and packed owner ref state, selected integration/archive refs, and movement logs participate in coherent capture. The selected-ref unlogged advance-and-return fixture reports incomplete.
- **R4 — resolved.** Stop decisions are bound to capture/path/authority checks and suppress only the named eligible consumer. The test confirms X is stopped while unrelated Y remains in impact.
- **R5 — resolved.** Distinct converging paths remain in the impact result through consumers and descendants.
- **R6 — resolved.** Explicit inactive lifecycle state remains inactive in default views. Available-source deletion is distinguished from unavailable source/object; retirement and history behavior match the accepted cases.

## Independent execution

On exact candidate `4c6f32f`, ran both Task 4 modules with `PYTHONPATH=.agents/ask`: both project tests and all five impact tests passed. This supplements the coordinator's exact-candidate Green traceability run covering all seven mapped cases. No source files were changed during review.

## Findings and verdict

No remaining existing-spec behavior defect or task-local structural suggestion found. No broader horizontal refactor, required redesign, evidence-backed withdrawal, or parked handoff.

**APPROVED** for exact candidate `4c6f32f3f4437d042681be0a93fff76a3341d0f3`. Boundary **ok**. Applicable R1–R6 reproductions remain addressed by the exact candidate implementation and assertions.
