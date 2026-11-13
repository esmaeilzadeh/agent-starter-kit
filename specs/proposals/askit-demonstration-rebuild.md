# Specification: AskIt demonstration notes rebuild

## Status

PROPOSED

## Goal

Make the English and Persian AskIt demonstration notes usable as a coherent
90-minute technical presentation and facilitator guide. A presenter should be
able to explain the AskIt model, walk through a simple lifecycle, distinguish
authority from evidence, and run the session without implying that unexecuted
work was executed.

## Non-goals

- Changing AskIt behavior, scripts, policies, or protocol contracts.
- Rebuilding the PowerPoint files.
- Preserving the existing 40-slide structure.
- Making the shorter-hashes retrospective the primary teaching path.
- Running historical benchmarks or producing new product artifacts.

## Behavior

The notes are two parallel Markdown documents. Each document presents the same
teaching sequence:

1. audience, outcomes, and session map;
2. AskIt's core model: human intent, delegated labor, durable evidence, and
   acceptance;
3. repository orientation and request routing;
4. a simple end-to-end walkthrough from request through acceptance;
5. evidence, recovery, and failure boundaries;
6. a bounded adoption exercise and closing reconstruction check.

Each section separates:

- a concise cue card suitable for a slide or presenter glance;
- presenter notes describing what to say, show, and ask;
- timing and expected audience outcome; and
- source/evidence references where a claim depends on repository material.

Demonstration material is explicitly labeled as live, saved evidence, or
optional. Historical examples and prepared commands are never described as
executed unless the repository contains corresponding evidence.

## Interfaces

- English guide: `docs/AskIt-demonstration-notes.md`
- Persian guide: `docs/AskIt-demonstration-notes-fa.md`
- Canonical workflow sources: `README.md`, `AGENTS.md`, `_ask/policies/`,
  `_ask/docs/demo/`, `.agents/ask/`

## Constraints

- English and Persian must have matching section IDs and order.
- Timing must be internally consistent and sum to the stated session length.
- Claims about commands, stages, authority, and evidence must point to current
  repository sources.
- The guide must be scannable during a live session; avoid a 40-slide
  transcript or near-verbatim speech.
- Persian prose should be natural and technically precise, not a mechanical
  line-by-line translation.
- Keep changes limited to the two requested notes plus required workstream
  contracts and verification artifacts.

## Invariants

- No note claims a benchmark, experiment, or live command was run without
  inspectable evidence.
- The two language versions describe the same audience outcomes, lifecycle,
  evidence policy, and boundaries.
- Human ownership of intent and acceptance remains distinct from delegated
  implementation and review work.
- The simple walkthrough remains the primary demonstration; any historical case
  is explicitly secondary or optional.

## Failure cases

- A presenter cannot tell what to say, show, or ask from the guide.
- English and Persian sections drift in numbering, order, timing, or meaning.
- A saved or optional example is presented as live execution.
- A source reference points to a missing path or no longer supports the claim.
- Timing or section boundaries make the stated session length impossible.

## Acceptance criteria

- `DOC-001`: Both requested Markdown files exist and contain the same ordered
  section IDs and session outcomes.
- `DOC-002`: The guide has a clear opening, core model, lifecycle walkthrough,
  evidence/recovery section, adoption exercise, and close.
- `DOC-003`: Every section has a concise cue card, presenter guidance, timing,
  and an observable audience outcome.
- `DOC-004`: Demonstration claims are labeled live, saved evidence, or optional,
  and no unverified execution is presented as fact.
- `DOC-005`: Important workflow claims cite repository paths that exist and
  remain relevant to the claim.
- `DOC-006`: English and Persian are semantically aligned while allowing
  natural language differences.
- `DOC-007`: The notes are substantially shorter and more scannable than the
  current 40-slide script, without losing the core AskIt model or safety
  boundaries.

## Open questions

- The exact number of sections and minute allocation may be adjusted during
  implementation if the resulting total remains explicit and coherent.
- A shorter-hashes evidence clinic may remain as a clearly optional appendix.

## Source intent

`work/askit-demonstration-rebuild/intent.md`

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: The deliverable is static Markdown guidance. Its
verification is structural and editorial rather than a runtime user journey.
