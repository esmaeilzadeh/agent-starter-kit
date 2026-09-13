# Humanizer on documentation and specifications

The Community Skill [humanizer](https://www.skills.sh/blader/humanizer/humanizer) already has a method for removing default-model writing tells. The kit had no pin or rule that required it on docs and specs.

## Decision

- Pin `humanizer` from `blader/humanizer` at `v3.0.0` in `_ask/skills/manifest.yaml` (`role: docs-voice`, `required: true`). Never `revision: latest`.
- When writing or editing documentation or specifications, agents read the prepared skill and follow it in embedded mode. Stock Cursor rule: `.cursor/rules/humanizer-docs-specs.mdc`. Spec-stage contracts: `_ask/agents/02-spec.md`, `03-spec-challenge.md`, `04-spec-change.md`.
- Kit files stay thin pointers. The pattern list lives only in the prepared skill body.
- Keep claims. Do not invent facts. Leave code, commands, paths, YAML metadata, and link targets unchanged.
- Rewriting existing kit Guide and Build Spec prose is a later job, not this pin.

## Consequences

- `./ask prepare` fails closed if this required pin cannot be installed.
- Upgrade does not add the pin to an existing consumer manifest. Consumers who want the required install add the pin themselves; the stock rule still names the skill.
