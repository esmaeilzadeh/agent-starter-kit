# Specification: pin humanizer for docs and specs

## Status

CURRENT

## Goal

The kit prepares `humanizer` from `blader/humanizer#v3.0.0` and agents apply it whenever they write or edit documentation or specifications.

## Non-goals

Rewriting existing kit prose. Vendoring the skill tree. `revision: latest`. Changing code or machine-facing fields.

## Behavior

- Manifest entry `humanizer`: source `blader/humanizer`, revision `v3.0.0`, skill `humanizer`, role `docs-voice`, `required: true`.
- `./ask prepare` installs it and updates `skills-lock.json`.
- Stock Cursor rule (kit-owned, not `.cursor/rules/local/`): when writing or editing docs or specs, read the prepared skill and follow it in embedded mode. Point; do not copy the pattern list into the rule.
- Spec-stage contracts (`02`, `03` when the challenge writes prose, `04`) tell the agent to apply the same skill before finishing those artifacts.
- File-mode / embedded-mode limits from the skill stay in force: keep claims; do not invent facts; leave code, commands, paths, YAML metadata, and link targets unchanged.

## Interfaces

- `_ask/skills/manifest.yaml`
- `skills-lock.json`
- `.cursor/rules/` stock rule
- `_ask/agents/02-spec.md`, `03-spec-challenge.md`, `04-spec-change.md`
- ADR 0017

## Constraints

Never `revision: latest`. Do not vendor `.agents/skills/humanizer`.

## Invariants

The pattern list lives only in the prepared skill body. Kit files stay thin pointers.

## Failure cases

- Prepare with `required: true` fails if the pin cannot be installed.
- A rule that restates the 25 patterns becomes a second SoT.

## Acceptance criteria

- Manifest and lock pin `humanizer` at `v3.0.0`.
- `./ask prepare` exits 0 and reports ok for `humanizer`.
- Stock rule exists and names the prepared skill + embedded mode.
- `02` / `03` / `04` contracts mention humanizer.
- Contract test covers the pin, rule, and contracts.
- `./ask verify` passes.

## Open questions

None.

## Source intent

`work/pin-humanizer/intent.md`
