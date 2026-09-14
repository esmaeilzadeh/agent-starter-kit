# Specification: humanize kit Guide, docs, and README pages

## Status

CURRENT

## Goal

Existing kit Guide, `_ask/docs/`, and README pages read like a person wrote them. Claims, commands, paths, and protocol meaning stay the same.

## Non-goals

- `_ask/spec/` and the monolith Build Spec stub (machine-first).
- `_ask/agents/`, `_ask/policies/`, `_ask/templates/`.
- `CONTEXT.md`, `AGENTS.md`, `_ask/OWNED-PATHS.md`, `_ask/MAPPING.md`.
- Generated `.cursor/` projections.
- Historical `work/` and `specs/current/` records (except this spec).
- Scripts, tests, YAML, lockfiles.
- New features or policy changes.

## Behavior

- File-mode `humanizer` (`blader/humanizer` @ `v3.0.0`) on every in-scope file.
- In scope: `_ask/guide/**`, `_ask/docs/**` (ADRs, demo, research, kit-author notes), `README.md`, `_ask/README.md`.
- Keep every supported claim. Do not add a fact, name, number, date, quote, or citation.
- Leave code blocks, inline code, commands, paths, YAML metadata, data, and link targets unchanged.
- Do not change must/must-not meaning.

## Constraints

Technical/plain voice. No writing sample.

## Invariants

A reader who knew the old page still has the same facts and rules. Only the voice and the filler change.

## Failure cases

- A command, path, or stage name changes.
- A claim is dropped or invented.
- A spec module or agent contract is edited.

## Acceptance criteria

- `git diff` for this work touches only in-scope paths plus `work/humanize-ask-docs-and-specs/` and this spec.
- In-scope files have had a humanizer pass (short ADRs may change little).
- `./ask verify` passes.
- Spot-check: no rewritten command or path in the diff.

## Open questions

None.

## Source intent

`work/humanize-ask-docs-and-specs/intent.md`
