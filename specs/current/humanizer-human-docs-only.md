# Specification: humanizer on human-facing docs only

## Status

CURRENT

## Goal

Agents apply `humanizer` only to an explicit human-facing Markdown set. Agents apply `writing-for-agents` to every spec and every other machine-first Markdown file. Machine-first files do not go through `humanizer`.

## Non-goals

Rewriting existing kit prose. Vendoring skill trees. `revision: latest`. Dropping the `humanizer` pin. Changing code, commands, paths, YAML metadata, or link targets for voice.

## Behavior

### Pins

- `humanizer`: source `blader/humanizer`, revision `v3.0.0`, skill `humanizer`, role `docs-voice`, `required: true`.
- `writing-for-agents`: source `mattpocock/skills`, revision `v1.2.3`, skill `writing-for-agents`, role `agent-docs`, `required: true`.

`./ask prepare` installs both and updates `skills-lock.json`.

### Human-facing set (humanizer)

Only these paths:

- root `README.md`
- `_ask/guide/**`
- `_ask/docs/demo/**`

When writing or editing a file in this set, read `.agents/skills/humanizer/SKILL.md` and follow it in embedded mode (`./ask prepare` if missing).

### Machine-first set (writing-for-agents)

Default: every other `.md` the kit or a workstream treats as a contract, pointer, or agent-consumed artifact. This includes at least:

- `specs/`
- `_ask/spec/`
- `_ask/agents/`
- `_ask/policies/`
- `_ask/templates/`
- `AGENTS.md`
- `CONTEXT.md`
- `work/**/*.md`
- `_ask/docs/adr/`
- generated `.cursor/skills/` and `.cursor/commands/` (follow `_ask/agents/` source)

When writing or editing a file in this set, read `.agents/skills/writing-for-agents/SKILL.md` and follow it in embedded mode (`./ask prepare` if missing). Do not apply `humanizer` to that file.

A `.md` path that is in neither list is machine-first.

### Rules and contracts

- Stock Cursor rule for humanizer: glob-limited to the human-facing set. It does not name specifications as an apply target. Thin pointer; do not copy the humanizer pattern list.
- Stock Cursor rule for writing-for-agents: always-on pointer for machine-first files. Thin pointer; do not copy the skill body.
- Spec-stage contracts `02`, `03` (when the challenge writes prose), and `04` require `writing-for-agents` before finish. They do not require `humanizer`.

File-mode / embedded-mode limits from each skill stay in force: keep claims; do not invent facts; leave code, commands, paths, YAML metadata, and link targets unchanged.

## Interfaces

- `_ask/skills/manifest.yaml`
- `skills-lock.json`
- `.cursor/rules/` stock rules
- `_ask/agents/02-spec.md`, `03-spec-challenge.md`, `04-spec-change.md`
- ADR 0017
- `specs/current/pin-humanizer.md` (SUPERSEDED)

## Constraints

Never `revision: latest`. Do not vendor `.agents/skills/humanizer` or `.agents/skills/writing-for-agents`.

## Invariants

- The humanizer pattern list lives only in the prepared humanizer skill body.
- Specs and machine-first files name `writing-for-agents`, not humanizer, as the finish skill.
- Kit files stay thin pointers.

## Failure cases

- Prepare with `required: true` fails if either pin cannot be installed.
- A rule that restates the humanizer pattern list or the writing-for-agents body becomes a second SoT.
- `02` / `03` / `04` still require humanizer on the specification or challenge artifact.
- Humanizer rule still applies to specifications or is `alwaysApply: true` with no path limit.
- A spec or machine-first file is passed through humanizer.

## Acceptance criteria

- Manifest and lock pin `humanizer` at `v3.0.0` and `writing-for-agents` at `v1.2.3`.
- `./ask prepare` exits 0 and reports ok for both skills.
- Humanizer stock rule exists, is limited to the human-facing set, and does not target specifications.
- Writing-for-agents stock rule exists and names the prepared skill + embedded mode for machine-first files.
- `02` / `03` / `04` mention `writing-for-agents` and do not instruct the agent to apply humanizer.
- Contract test covers both pins, both rules, and the Spec-stage contracts.
- `pin-humanizer.md` is SUPERSEDED with a pointer to this file.
- ADR 0017 records the split.
- `./ask verify` passes.

## Open questions

None.

## Source intent

`work/humanizer-human-docs-only/intent.md`

## Spec change

`work/humanizer-human-docs-only/spec-change.md` (accepted, 2026-09-13)
