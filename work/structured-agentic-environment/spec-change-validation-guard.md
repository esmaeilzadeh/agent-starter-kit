# Specification Change: validated state around every action

## Current specification

The initial, not-yet-accepted model/UI contract is retained at `f60dafb`. It described model-file validation and UI handling of malformed documents, and assumed a Python-standard-library core. No accepted-tests ref or implemented validator exists for this workstream.

## Human-directed change

The human clarified that the UI relies on clean requirements; document validity and links belong to the document-state validator. Validation must run after every specification change and also before any state-changing action, because its starting state must be stable. Fast existing tools or a lower-level implementation are expressly allowed. Latest stopping condition: deliver a plan, not an implementation.

## Required behavior

The shared action path validates the current complete definition/reference snapshot, stages a candidate, validates the result, checks input freshness and publishes only a validated state. Validation covers referenced specification changes even when the engineering-model file did not change. Invalid pre-state prevents action invocation; invalid post-state cannot replace the last stable state. A multi-file action is one explicit change, with no intermediate state published. External saves also trigger validation; startup and action/read entry checks cover missed events. Invalid external edits require explicit repair/import outside ordinary action execution; the UI does not repair them.

## Impact

Revise Intent, spec Markdown/JSON, Plan and test obligations. Replace the UI broken-document case with document-layer admission/guard tests. Add pre/post ordering, referenced-input invalidation, atomic snapshot, external-edit and cache-parity cases. Keep evidence provenance and runtime feedback separate from document validity. Preserve original source history and independent re-challenge the new contract before implementation.

## Alternatives

UI-specific validation duplicates domain rules. Validating only the changed model misses edited referenced criteria. Validating only after writing exposes broken state; validating only before writing admits broken changes. Git hooks alone miss uncommitted/editor changes. A fixed Python or native implementation without workload measurements adds an unsupported performance assumption. These alternatives do not satisfy the clarified requirement.

## Decision

HUMAN-DIRECTED — explicit statements in this conversation authorize these changes. Implementation language/tool selection remains an engineering decision informed by reproducible benchmarks. No speed claim, latency guarantee, implementation approval or completed feature is inferred from this plan.
