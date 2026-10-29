# Task 3 independent review — round 2

Reviewer: `/root/cont_review`, independent Codex Sol reviewer as assigned.
Runtime: Codex; exact inherited model and parent identifiers not supplied.
Base: `0d9089f95d29a0eb2d017477f634c5162ea1bb73`.
Candidate: `a24922f8ee0f15d04bac87e562f8a3eef5652237`.
Accepted inventory base: `02ad31b6e5ef5130986a920f943788cbbe970631`.

## Scope and boundary

Reviewed full compare.py, profiles.py and test_workflow_refs_compare.py against accepted Task 3 plan and cases 3/1–3/3, SH-06/SH-07/SH-15, current TaskResult and recorded assertion continuity. The exact implementation-base diff contains only these three owned paths. Earlier __init__.py edits were reverted. Boundary: **ok**. Task 3 is current writer.

## Prior findings resolved

Previously reported high-precision numeric collapse is fixed by exact Decimal parsing and typed recursive canonicalization. Unknown fields, booleans versus numbers, arrays and absent/null/empty distinctions are preserved; JSON object order/whitespace alone normalize. External input identity/revision/role changes remain significant despite equal payloads. Missing input lists return incomplete rather than silently assuming no dependencies.

Explicit empty/None or changed profile identities no longer silently default. Unknown versioned profiles are incomplete; the frozen profile registry exposes copies, not mutable profile authority. Prose compares exact bytes.

Git extraction checks full commit identity against repository object format, canonical relative paths, exact committed object and regular file mode. Directories/symlinks cannot be mistaken for file payloads. Committed path-rename tests preserve old snapshot/path and extract new path explicitly, while missing old path in the new snapshot refuses. Available absent items are distinct from source unavailability; duplicate stable IDs are incomplete. No worktree fallback exists.

## R1 — Existing-spec behavior defect: unsupported Decimal numbers escape incomplete-state boundary

Location: `.agents/ask/workflow_refs/compare.py`, compare_items exception boundary and extract_git_item document parsing boundary (both use json.loads with Decimal).

Direct independent probe:

`compare_items('{"v":1e99999999999999999999999999999999999999}', '{"v":1}', 'structured-item/1', before_inputs=[], after_inputs=[])`

raises `decimal.InvalidOperation` instead of returning an incomplete comparison. Decimal's implementation has finite exponent limits, and its DecimalException hierarchy is not caught by the existing ValueError/TypeError handlers. The same numeric token in a pinned structured document escapes extraction's exception boundary.

Task 3 requires unsupported/unavailable comparison and extraction inputs to return incomplete, never crash or establish equivalence (SH-07, SH-15; cases 3/2 and 3/3). Catch DecimalException or convert unsupported Decimal parse/canonicalization errors to the existing invalid-input/incomplete outcome at both public boundaries. Add genuine assertion regressions for direct comparison and a pinned document with an unsupported exponent, execute Red → Green → Refactor and request exact-candidate review. Keep exact-decimal precision; do not revert to float rounding.

This is a remaining failure-path defect in the current precision correction, within task ownership. No Spec Change or broader redesign required.

## Assertion and TDD review

Initial Red `8118683e43804bef9de677450a7d2984`, source a95b039, records all three cases failing behavior_assertion after successful collection. Correction Red `5b5c9b8ef6cd41f4a4de619c26e48211`, source 7a5c4e33, records 3/2 and 3/3 failing behavior_assertion and 3/1 passing. Exact final Green `9b0f9718bc884334a1a35791bf0b80d6` binds to a24922f; all three cases pass. Runner collection statuses, exits and output log digests match recorded evidence.

Tests are strengthened for explicit inputs, real ambiguous identities, exact prose extraction, high-precision changes, explicit profile failure and real path moves. No previous Red assertion was weakened. They do not exercise unsupported Decimal exponent parsing, so passing Green does not clear R1. No tests were rerun by reviewer; direct comparison and Git path/type probes were executed without modifying source.

## Other classifications and verdict

No local structural suggestion, broader refactor, required redesign or withdrawn finding. No parked handoffs. Earlier observations were corrected, not withdrawn.

**REJECTED** for `a24922f8ee0f15d04bac87e562f8a3eef5652237`.
Boundary **ok**. Only blocking finding: **R1 unsupported Decimal exception**.
