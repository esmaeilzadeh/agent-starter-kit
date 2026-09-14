# Humanizer on human-facing docs; writing-for-agents on machine-first files

The Community Skill [humanizer](https://www.skills.sh/blader/humanizer/humanizer) removes default-model writing tells. Applied to a spec or stage contract, that rewrite costs `must` / `must not` precision. Machine-first files need [writing-for-agents](https://www.skills.sh/) (`mattpocock/skills`).

## Decision

- Pin `humanizer` from `blader/humanizer` at `v3.0.0` (`role: docs-voice`, `required: true`). Never `revision: latest`.
- Pin `writing-for-agents` from `mattpocock/skills` at `v1.2.3` (`role: agent-docs`, `required: true`).
- Humanizer apply-scope is fail-closed: root `README.md`, `_ask/guide/`, `_ask/docs/demo/` only. Stock rule: `.cursor/rules/humanizer-docs-specs.mdc` (glob-limited, not `alwaysApply`).
- Specs and other machine-first Markdown use `writing-for-agents` in embedded mode. Stock rule: `.cursor/rules/writing-for-agents-machine-docs.mdc`. Spec-stage contracts: `_ask/agents/02-spec.md`, `03-spec-challenge.md`, `04-spec-change.md`. Those contracts do not apply humanizer.
- Kit files stay thin pointers. Skill bodies stay in the prepared trees.
- Keep claims. Do not invent facts. Leave code, commands, paths, YAML metadata, and link targets unchanged.
- Rewriting existing kit prose is a later job.

## Consequences

- `./ask prepare` fails closed if either required pin cannot be installed.
- Upgrade does not add pins to an existing consumer manifest.
- A spec that goes through humanizer is a contract failure.

## Supersedes

The 2026-09-13 pin that applied humanizer to all documentation and specifications (`specs/current/pin-humanizer.md`, now SUPERSEDED).
