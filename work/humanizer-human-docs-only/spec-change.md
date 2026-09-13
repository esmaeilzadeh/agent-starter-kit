# Specification Change Proposal

## Current specification

`specs/current/pin-humanizer.md`

Agents apply `humanizer` whenever they write or edit documentation or specifications. Spec-stage contracts `02` / `03` / `04` require that skill before finish. The stock Cursor rule is always-on for docs and specs.

## Proposed change

Split apply-scope by audience.

- Humanizer: only the human-facing set (root `README.md`, `_ask/guide/`, `_ask/docs/demo/`).
- `writing-for-agents`: all specs and machine-first `.md` files. Those files do not go through humanizer.
- Pin `writing-for-agents` from `mattpocock/skills` at `v1.2.3`.
- Supercede `pin-humanizer.md` with `specs/current/humanizer-human-docs-only.md`. Update ADR 0017.

## Why the change is needed

Humanizer optimizes for human voice. A spec or agent contract needs precise, machine-first language. Applying humanizer there is a defect, not a style pass.

## Impacted artifacts

- `specs/current/pin-humanizer.md`
- `specs/current/humanizer-human-docs-only.md`
- `_ask/docs/adr/0017-humanizer-docs-specs.md`
- `_ask/agents/02-spec.md`, `03-spec-challenge.md`, `04-spec-change.md`
- `.cursor/rules/humanizer-docs-specs.mdc` and a new writing-for-agents rule
- `_ask/skills/manifest.yaml`, `skills-lock.json`
- `_ask/tests/test-humanizer-docs-specs.sh`
- `_ask/spec/03-policies-skills-context.md`, `_ask/spec/06-phases-and-acceptance.md`, `_ask/MAPPING.md`, `_ask/skills/README.md`, `CONTEXT.md`

## Impacted workstreams

`pin-humanizer` (accepted; this change updates its CURRENT spec). No other live workstream is in scope.

## Migration / transition notes

Existing spec prose is left as-is. New and edited machine-first files use `writing-for-agents`. Consumers keep their own manifest on upgrade; they add the `writing-for-agents` pin if they want the required prepare.

## Acceptance criteria for the change

- CURRENT workstream spec lists the human-facing set and the machine-first rule.
- `02` / `03` / `04` require `writing-for-agents` and do not require humanizer.
- Humanizer rule no longer targets specifications.
- ADR 0017 records the split.

## Decision

Accepted 2026-09-13. Human: go till end (Q1-A, Q2-B, Q3-A, pin `writing-for-agents`).
