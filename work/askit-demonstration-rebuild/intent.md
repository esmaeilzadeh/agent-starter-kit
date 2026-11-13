# Intent: Rebuild the AskIt demonstration notes

## What

Replace `docs/AskIt-demonstration-notes.md` and
`docs/AskIt-demonstration-notes-fa.md` with a matched English/Persian
facilitator guide that presents AskIt as a practical, reconstructable
engineering workflow.

The guide will:

- use a smaller, clearer structure than the current 40-slide script;
- start with the audience problem and AskIt's core model;
- walk through a simple end-to-end lifecycle rather than making the
  `shorter-hashes` retrospective the main path;
- separate slide/section cue cards from presenter notes;
- identify what to say, show, and ask without writing an artificial
  word-for-word transcript;
- label live demonstration, saved repository evidence, and optional material;
- cite canonical repository paths for important claims; and
- keep the English and Persian versions structurally and semantically aligned.

## Why

The current notes are long and technically rich, but they make the presenter
reconstruct the teaching arc from repeated slide blocks. A clearer guide should
make the AskIt model understandable to a new technical audience, make the
demonstration runnable without invented results, and make translation parity
reviewable.

## Non-goals

- Rebuilding or redesigning either PowerPoint file.
- Changing AskIt scripts, policies, protocol contracts, or runtime behavior.
- Running historical benchmarks or claiming that optional experiments ran.
- Rewriting unrelated documentation or translating the whole repository.
- Preserving a one-to-one mapping with all existing 40 slides.

## Known assumptions

- The two named Markdown files are the deliverables; the existing PPTX files
  may remain as historical/reference assets.
- The audience is developers and technical decision-makers who need a concrete
  mental model and a safe first adoption path.
- The guide targets approximately 90 minutes. Its facilitator timing is
  internally explicit, but audience-facing cue cards do not need to display
  the duration.
- Repository paths and current canonical contracts are the authority over
  claims inherited from the old notes.
- “Separate presenter notes + concise cue cards” means each section will make
  the concise audience-facing cue distinct from presenter guidance, rather
  than blending both into one paragraph.

## Open questions

- Exact section count and final minute allocation.
- Which simple lifecycle example can be demonstrated entirely from stable
  repository commands and artifacts without requiring a benchmark run.
- Whether a short appendix should retain the shorter-hashes evidence clinic.

## Human decisions

- Use a reduced, clearer structure instead of retaining 40 slide slots.
- Use a simple end-to-end AskIt walkthrough as the main demonstration.
- Keep presenter guidance separate from concise cue cards; do not write a
  full word-for-word script.
- Use eight stable guide sections and require at least a 35% reduction from
  the current notes while preserving the safety-boundary checklist.
- Maintain explicit evidence/citation inventories and review parity across
  section order, outcomes, timing, lifecycle, evidence labels, ownership, and
  primary/optional status.

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: This work changes static Markdown facilitation
notes only. It has no product runtime journey; verification is structural,
content, parity, source-reference, and Markdown-quality checking.
