# Explore Map: AskIt demonstration notes rebuild

## Destination

Create one coherent 90-minute AskIt presentation and facilitator guide in
English and Persian. The notes must help a presenter explain the kit's core
model, run the session without inventing evidence, and point every important
claim to the repository source that supports it.

## Notes

- The requested deliverables are the two Markdown note files:
  `docs/AskIt-demonstration-notes.md` and
  `docs/AskIt-demonstration-notes-fa.md`.
- The existing PowerPoint files are presentation assets, not the primary
  editing target for this work.
- The repository is the source of truth; the notes must not imply that an
  optional experiment or benchmark was executed when it was only prepared.
- English and Persian should have the same structure, slide numbering, timing,
  learning outcomes, evidence boundaries, and facilitator actions.

## Tracker map (optional)

- No external tracker context was supplied.

## Decisions so far

- Route: feature/documentation rebuild, not a bug fix.
- Audience: developers and technical decision-makers who need to understand
  how AskIt turns delegated work into reconstructable, reviewable evidence.
- Format: a practical facilitator guide, not a protocol specification and not
  a transcript of an agent chat.
- Teaching arc: orient the audience, explain the operating model, walk the
  workflow, inspect one real case, practice recovery/evidence decisions, and
  close with adoption guidance.
- Evidence policy: label each activity as live, saved evidence, or optional;
  keep claims tied to concrete repository paths and revisions where relevant.

## Not yet specified

- Whether the final 90-minute pacing should retain exactly 40 slides or use a
  smaller set of clearer sections.
- Whether the existing shorter-hashes case remains the central case study or
  should be replaced by a simpler AskIt lifecycle walkthrough.
- The final degree of presenter scripting versus concise cue cards.

## Out of scope

- Rebuilding or redesigning the PowerPoint files.
- Changing AskIt behavior, protocol contracts, scripts, or policies.
- Running historical benchmarks or fabricating live outputs for the guide.
- Re-translating unrelated repository documentation.

## Handoff to Intent

The destination is clear enough to own: rebuild the two named Markdown notes
into a matched English/Persian facilitator guide for a 90-minute AskIt
demonstration. The guide will use a simpler narrative and explicit evidence
labels, retain only claims supported by canonical repository sources, and
separate presenter cues from audience-facing explanation. The implementation
will decide the final slide/section count while preserving a usable timed
session and parity between languages.
