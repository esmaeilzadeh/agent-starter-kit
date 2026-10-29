# Task 3 independent review — round 3

Reviewer: `/root/cont_review`, independent Codex Sol reviewer as assigned.
Runtime: Codex. Exact inherited model and parent model identifiers not supplied.
Base: `0d9089f95d29a0eb2d017477f634c5162ea1bb73`.
Candidate: `3517e96758f63dc1898a7a4dae3ad938c2eb282f`.
Accepted contract/inventory base: `02ad31b6e5ef5130986a920f943788cbbe970631`.

## Scope and boundary

Fresh independent review covered the full Task 3 comparison/profile implementation and test scenarios inspected across these rounds, exact correction diff, accepted Task 3 plan and cases 3/1–3/3, canonical SH-06/SH-07/SH-15 obligations, TaskResult and immutable Red/Green evidence.

Complete base-to-candidate paths are `.agents/ask/workflow_refs/compare.py`, `.agents/ask/workflow_refs/profiles.py`, and `_ask/tests/test_workflow_refs_compare.py`. All match declared task ownership. Earlier __init__.py exports were reverted. Boundary **ok**, no extras or glob_too_narrow condition. Prior evidence remains intact.

## Findings resolved

No unresolved findings.

High-precision numbers no longer collapse through float parsing: exact Decimal parsing and typed recursive canonicalization retain distinct numeric values. JSON object order/whitespace normalize, while all fields, unknown fields, array order, booleans, strings and absent/null/empty distinctions participate. Complete explicit dependency reference/revision/role lists are checked independently from equal payloads; missing lists produce incomplete.

The latest correction catches DecimalException at both direct comparison and pinned document parsing boundaries. Huge unsupported exponents now return incomplete instead of escaping. Genuine regression assertions exercise both paths. A direct independent comparison probe confirmed the incomplete result while preserving exact-decimal comparison.

Explicit empty/None or changed profile identities do not silently acquire default authority. Unknown profiles return incomplete. The registry fixes versioned extraction/presentation rules and returns copies, preventing caller mutation of profile authority. Prose defaults to exact bytes.

Git extraction checks exact full commit identity against repository format, canonical safe repository-relative paths and regular committed file objects. Directories and symlinks cannot supply synthetic/indirect document content. Real committed rename tests resolve explicit new path and preserve old snapshot/path; new-snapshot old-path absence is incomplete. Available absent items are distinguished from unavailable documents; duplicate stable IDs are incomplete. There is no HEAD/worktree fallback.

Prior reports were corrected, not withdrawn. No local structural suggestions, broader horizontal refactors, required redesigns, evidence-backed withdrawals or parked handoffs remain.

## Criteria and assertion adequacy

- Case 3/1 (SH-07, SH-15 unit): complete payload and actual external identity/revision/role comparison; unchanged payload/bindings retain equality, external rebinding changes despite identical payload, and unknown fields remain significant.
- Case 3/2 (SH-06, SH-07, SH-15 unit): JSON formatting equivalence, exact prose changes, timeout obligation change, unavailable/changed/empty profiles and missing inputs cannot establish equality; high-precision numeric differences remain changes and unsupported numeric ranges return incomplete.
- Case 3/3 (SH-07, SH-15 integration): real immutable commits retain independent item equality amid unrelated changes while changed items differ; exact prose, actual path rename, historical old path, unavailable/missing sources, unsafe paths, nonfile objects, ambiguous IDs, supported absence and invalid document number ranges are exercised.

Task 3 establishes comparison/extraction primitives and exact binding declarations. Later revision publication, coherent project discovery, impact decisions and consumer eligibility remain later tasks' obligations; no completion authority is inferred from an unchanged primitive result.

## TDD continuity and exact-candidate evidence

Initial Red `8118683e43804bef9de677450a7d2984` at a95b039 records all three cases failing behavior_assertion after successful collection. Correction Red `5b5c9b8ef6cd41f4a4de619c26e48211` at 7a5c4e33 records 3/2 and 3/3 behavior failures. Latest targeted Red `787d1c2e6c1c46b7bdd236364bca8f7f` at `eb72156bad66a8b1a47ddfb2679e18dedf4081b1` records 3/2 and 3/3 as behavior_assertion failures for escaping Decimal exceptions, with 3/1 passing. Tests catch the exception and explicitly self.fail, so Red is an assertion failure rather than an unhandled runner error.

Final Green `18c7a93869a64bfab39181124af20e2b` binds exactly to `3517e96758f63dc1898a7a4dae3ad938c2eb282f`: all three mapped cases pass, collection succeeds and runner exits 0. Inspected Red/Green logs match their recorded digests. Test assertions were strengthened without weakening original obligations; no TDD exemption is used. The refactor maintains cohesive separate frozen-profile and comparison boundaries without invented cosmetic edits.

No full test suite was independently rerun by reviewer. Exact source/assertion continuity, recorded execution/log integrity and direct behavior probes were checked. Coordinator integration CheckPlan remains separate.

## Verdict

**APPROVED** for exact candidate `3517e96758f63dc1898a7a4dae3ad938c2eb282f`.
Boundary **ok**. All Task 3 findings resolved; no blocking findings.
