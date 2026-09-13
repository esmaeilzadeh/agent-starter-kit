# Specification Challenge

## Specification

`specs/current/humanize-ask-docs-and-specs.md`

## Ambiguities

“README pages” means root `README.md`, `_ask/README.md`, and READMEs already inside `_ask/guide/` and `_ask/docs/`.

## Missing failure cases

A rewrite that keeps every claim but reorders a numbered Guide section so a cross-reference in `_ask/spec/` (out of scope) points at the wrong heading. Mitigation: keep heading text and section numbers.

## Over-constraint risks

Requiring every short ADR to change would force fake edits. Acceptance already allows little change on short files.

## Under-constraint risks

No automated “AI-tell” scorer. Review is a human/agent read of the diff.

## Recommended clarifications

Keep Guide/ADR titles and section numbers. Recorded here; no spec change.

## Challenge verdict

PASS
