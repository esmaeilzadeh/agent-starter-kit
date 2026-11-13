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

The notes are two parallel Markdown documents. Each document presents these
eight stable sections, in this order:

1. `ORIENT` — audience, outcomes, and session map;
2. `MODEL` — human intent, delegated labor, durable evidence, and acceptance;
3. `ROUTE` — repository orientation and request routing;
4. `WALKTHROUGH` — a simple end-to-end path from request through acceptance;
5. `EVIDENCE` — claims, sources, provenance, and review boundaries;
6. `RECOVERY` — refusal, stale evidence, and changed-destination cases;
7. `ADOPT` — a bounded first-use exercise;
8. `CLOSE` — reconstruction check and next action.

Each section separates:

- a concise cue card suitable for a slide or presenter glance;
- presenter notes describing what to say, show, and ask;
- internal facilitator timing and expected audience outcome; and
- source/evidence references where a claim depends on repository material.

Demonstration material is explicitly labeled as `LIVE`, `SAVED`, or
`OPTIONAL`. Every command, result, historical example, and optional activity
has one unique inventory key and one label in the evidence inventory. `SAVED`
rows name the artifact path and the commit that produced or last changed that
artifact; `LIVE` rows are instructions to execute rather than claims that
execution already happened. The session target is approximately 90 minutes;
the eight internal numeric timings sum exactly to 90 minutes, and cue cards do
not need to display duration.

## Interfaces

- English guide: `docs/AskIt-demonstration-notes.md`
- Persian guide: `docs/AskIt-demonstration-notes-fa.md`
- Canonical workflow sources: `README.md`, `AGENTS.md`, `_ask/policies/`,
  `_ask/docs/demo/`, `.agents/ask/`

## Constraints

- English and Persian must have matching section IDs and order.
- Internal timing must be consistent and sum to 90 minutes; the audience
  cue-card layer does not need to show duration.
- Claims about commands, stages, authority, and evidence must point to current
  repository sources.
- The guide must be at least 35% shorter by line count than the current
  English/Persian notes respectively and remain scannable during a live
  session; avoid a 40-slide transcript or near-verbatim speech.
- Persian prose should be natural and technically precise, not a mechanical
  line-by-line translation.
- The eight section IDs and their order are identical in both languages.
- A parity review covers section IDs/order, outcomes, timing, lifecycle,
  evidence labels, ownership boundaries, and primary/optional status.
- A citation review records the source path, relevant heading or excerpt, and
  `SUPPORTED`/`UNSUPPORTED` decision for every cited claim.
- A parity review records one `MATCH`/`MISMATCH` decision for each required
  parity dimension and one row per uniquely keyed inventory item.
- Baselines are the two current note files at commit
  `2e5ea92989c48c10e4829bc22c325643443a38b3`; reduction uses physical
  `wc -l` counts including blank lines.
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
- Only the two requested Markdown files are production deliverables. PPTX
  files, indexes, links, and unrelated documentation remain unchanged unless
  a separately approved scope change identifies a broken reference.

## Failure cases

- A presenter cannot tell what to say, show, or ask from the guide.
- English and Persian sections drift in numbering, order, timing, or meaning.
- A saved or optional example is presented as live execution.
- A source reference points to a missing path or no longer supports the claim.
- Timing or section boundaries make the stated session length impossible.

## Acceptance criteria

- `DOC-001`: Both requested Markdown files exist and contain the eight ordered
  section IDs (`ORIENT`, `MODEL`, `ROUTE`, `WALKTHROUGH`, `EVIDENCE`,
  `RECOVERY`, `ADOPT`, `CLOSE`) and the same session outcomes.
- `DOC-002`: The guide has a clear opening, core model, lifecycle walkthrough,
  evidence/recovery section, adoption exercise, and close.
- `DOC-003`: Every fixed section has a concise cue card, presenter guidance,
  internal timing, and an observable audience outcome; the eight timings sum
  to 90 minutes.
- `DOC-004`: The evidence inventory assigns every command, result, historical
  example, and optional activity exactly one label: `LIVE`, `SAVED`, or
  `OPTIONAL`; saved rows identify their path and relevant SHA, and no
  unverified execution is presented as fact.
- `DOC-005`: Every cited workflow claim has an existing repository path, a
  relevant heading or excerpt, and an explicit support decision.
- `DOC-006`: English and Persian match on section IDs/order, outcomes, timing,
  lifecycle, evidence labels, ownership boundaries, and primary/optional
  status while allowing natural language differences.
- `DOC-007`: Each rebuilt note is at least 35% shorter by physical `wc -l` count than its
  pinned current-language baseline, and a safety checklist confirms preservation of
  the core model, ownership, evidence, recovery, and failure boundaries.

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
