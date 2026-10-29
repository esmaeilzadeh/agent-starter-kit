# Task 4 independent review — round 3

Reviewer: independent Codex child reviewer; exact inherited model identifier was not exposed. Runtime: Codex. Parent reviewer: `/root`.
Candidate: `27dd8ac9194bead5dc927971cac58c6b6ee55fc6`.
Task base: `16b699cbcc253d0873cd58aee6e773ab373a6f28`.
Accepted contract: `02ad31b6e5ef5130986a920f943788cbbe970631` (revision 7).
Exact final Green run reported by coordinator: `3585e44f8f4849dea3e9778e05016ce1`; all seven mapped Task 4 cases passed and collection succeeded.

## Scope and boundary

Reviewed the complete Task 4 implementation and tests at the candidate against SH-15 through SH-18, mapped cases 4/1–4/7, the Task 4 plan, and round 1 and round 2 findings. Base-to-candidate changes are limited to `.agents/ask/workflow_refs/project.py`, `.agents/ask/workflow_refs/impact.py`, `_ask/tests/test_workflow_refs_project.py`, and `_ask/tests/test_workflow_refs_impact.py`. All match Task 4 owned-path globs. Boundary **ok**; no extras and no `glob_too_narrow` condition.

## Prior findings

- **R1 — resolved.** The project graph is loaded from captured, authority-registered catalogs and committed item sources. Candidate inputs are separately represented and traversed without rewriting old pins; unregistered candidate revisions make assessment incomplete. Missing source commits/files are translated to incomplete discovery results. The candidate includes a regression that points an authority snapshot at an unavailable commit and asserts incomplete status instead of an exception.
- **R2 — resolved.** Catalog refs for live and archived owners are associated with those owners; explicitly registered shared owners remain distinct.
- **R3 — resolved.** Capture fingerprints loose and packed owner refs plus the selected integration/archive refs, and checks movement logs and storage generations before and after scanning. The unlogged selected `develop` advance-and-return regression now returns incomplete.
- **R4 — resolved.** A valid retain decision stops only its named eligible consumer edge. The impact regression names X and confirms X is omitted while unrelated consumer Y remains affected; invalid, missing, stale, or unauthorized decisions continue propagation.
- **R5 — resolved.** Traversal retains distinct converging paths; the impact regression checks both paths through T and descendants X and Y.
- **R6 — resolved.** Explicit inactive lifecycle state is preserved and excluded from default impact, while history remains available. Deletion in an available candidate source is distinguished from an unavailable source/object; retirement is refused while active consumers remain and accepted retirement preserves historical graph bindings.

## Independent execution and probes

Ran both Task 4 modules on the exact candidate with `PYTHONPATH=.agents/ask`: 2 project tests and 5 impact tests passed. The first invocation without that import path failed during collection; the corrected invocation passed.

The exact candidate's assertions cover source-bound candidate-only dependency discovery and refusal of unregistered candidate revisions, unavailable pinned source objects, selected-ref unlogged ABA, per-consumer retain stops, converging paths, explicit inactive state, deletion versus unavailability, and retained history. These address the exact repros recorded in rounds 1 and 2. No source files were changed during review.

## Findings

No remaining existing-spec behavior defect or task-local structural suggestion found in the reviewed Task 4 outcome. No broader horizontal refactor, required redesign, or evidence-backed withdrawal identified. No parked refactor handoff.

## Residual risks

Capture scope is explicitly local and cooperative; unfetched remote refs are not claimed. The candidate returns that scope in capture data, matching the accepted bounded contract.

## Review verdict

**APPROVED** for exact candidate `27dd8ac9194bead5dc927971cac58c6b6ee55fc6`. Boundary **ok**. Prior round-1 and round-2 findings are resolved by candidate changes and assertions. The independent module run and coordinator's exact-candidate seven-case Green run passed.
