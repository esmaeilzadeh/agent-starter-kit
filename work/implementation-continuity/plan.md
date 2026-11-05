# Plan: Close the duplicate continuity card

## Specification

Close the card only if the merged recovery guidance directly covers its failure and proposed fix.

## Approach

Inspect the merged canonical and generated instructions, record the evidence, remove the duplicate card, and merge this documentation-only workstream.

## Work breakdown

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| DUP-001 | Evidence-backed duplicate closure | — | `.later/implementation-continuity.md`, `work/implementation-continuity/` | Not applicable | Cross-reference to `continuation-context-loss` and merged commit `4b392e0` |

## Risks

If the card contains requirements absent from the merged fix, preserve it. Its named failure and proposed recovery are covered by checking active state and retaining approvals.

## Verification approach

Inspect all source/projection copies and run `git diff --check`.

## Out of scope for this plan

Any source change.

## E2E

`not_applicable`: documentation-only duplicate closure.
