# Specification Challenge

## Specification

`specs/current/grilling-skip-trivia.md`

## Ambiguities

“Short list” of skills is unbounded. Treat as ≤3 proposals unless they ask for more.

## Missing failure cases

Manifest edit on a dirty tree / during another workstream. Pinning is in-scope for this work-id’s branch (same as other kit edits).

## Over-constraint risks

Requiring a search on every tiny grill. Spec already skips when no domain skill would change What/Why.

## Under-constraint risks

No machine check that agents follow the filter. Contract + ADR only (v1).

## Recommended clarifications

Cap proposals at 3. Recorded as implementation preference, not a new What.

## Challenge verdict

PASS
