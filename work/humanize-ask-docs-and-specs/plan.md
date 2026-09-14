# Plan

## Specification

`specs/current/humanize-ask-docs-and-specs.md`

## Approach

File-mode humanizer in slices: Guide, README pages, then `_ask/docs/`. Keep headings and section numbers. Commit after each slice.

## Work breakdown

1. Guide modules (`_ask/guide/`).
2. `README.md`, `_ask/README.md`.
3. `_ask/docs/` ADRs, demo, agents notes, research.
4. Review the diff for dropped/invented claims and path/command edits.
5. `./ask verify`.

## Risks

Meaning drift on Guide workflow text. Mitigation: keep lists of must/must-not and command lines verbatim where they are normative.

Research notes are long and citation-heavy. Mitigation: light pass; do not drop sources.

## Verification approach

Path filter on `git diff --name-only`. `./ask verify`. Diff spot-check for commands and paths.

## Out of scope for this plan

Build Spec, agents, policies, merge to `main` until Accept.
