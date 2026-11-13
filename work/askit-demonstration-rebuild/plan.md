# Plan

## Specification

`specs/current/askit-demonstration-rebuild.md` and its canonical JSON criteria,
revision 1, digest
`f4126d944d1308a4844ffde6aa91b097768271687b292e2d20e4cf674a20eb15`.

## Approach

1. Replace both requested Markdown notes with one shorter, section-based
   facilitator guide and keep the English/Persian structure aligned.
2. Use the repository's current workflow docs as the source for commands,
   stages, authority, and evidence boundaries.
3. Keep the primary walkthrough simple and mark saved evidence, live actions,
   and optional material explicitly.
4. Review the two language versions against the same section checklist and
   validate source paths, timing, headings, and prohibited claims.

## Work breakdown

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| DOC-REBUILD | Rewrite the English and Persian AskIt demonstration notes as a matched, concise facilitator guide | — | `docs/AskIt-demonstration-notes.md`; `docs/AskIt-demonstration-notes-fa.md` | — | Both notes satisfy DOC-001 through DOC-007 under independent review; structural and source-reference checks pass |

This is one cohesive documentation deliverable. Splitting English and Persian
would create a false boundary because parity, timing, and section order must be
reviewed together. There are no executable product behavior tests; direct
editorial review plus deterministic structure/source checks provide evidence.

Create `work/askit-demonstration-rebuild/inner-loop/tasks.yaml` with the same
single task and `work/askit-demonstration-rebuild/test-plan.json` with the
review-only criteria mapping.

## Risks

- The guide could become shorter by omitting important safety boundaries.
- Translation could drift in meaning even when headings match.
- Repository references could become stale or point to files that do not
  support the surrounding claim.
- Existing PPTX assets may no longer correspond slide-for-slide; the notes
  must state that the Markdown guide is the rebuilt source for the new flow.

## Verification approach

- Parse both Markdown files and compare section IDs, order, outcomes, and
  timing totals.
- Check every cited repository path exists.
- Search for unsupported execution language and inspect each demonstration
  label.
- Compare the new line counts and section count with the old notes.
- Perform an independent semantic review against every DOC criterion.
- Run `./ask verify` and the workstream acceptance checks.

## Out of scope for this plan

PowerPoint redesign, AskIt runtime changes, benchmark execution, historical
artifact mutation, and unrelated documentation cleanup.

## E2E

`not_applicable`: this work changes static facilitation notes and has no
product runtime journey.
