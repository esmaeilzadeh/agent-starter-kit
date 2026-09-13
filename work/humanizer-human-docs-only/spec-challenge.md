# Specification Challenge

## Model

model: grok-4.6
runtime: cursor
parent_model: grok-4.6

Human said go till end. Same-family warn waived by that confirm. Parent authored after the required spawn rule; no child transcript in this chat.

## Specification

`specs/current/humanizer-human-docs-only.md`

## Ambiguities

- `_ask/README.md`, `_ask/MAPPING.md`, `_ask/OWNED-PATHS.md`, and `_ask/skills/README.md` are not in the human-facing list. The default clause makes them machine-first. That is intended and now explicit in the spec.
- Root `README.md` is human-facing; `_ask/README.md` is not. Agents can mix them up if the rule glob is `**/README.md`. The humanizer glob must be the repo-root `README.md` only.

## Missing failure cases

- A `**/README.md` glob that humanizes `_ask/README.md` or `work/*/README.md`.
- `alwaysApply: true` left on the humanizer rule after the path limit is added.

Both are now in Failure cases / Behavior.

## Over-constraint risks

Requiring `writing-for-agents` on every `work/**/*.md` includes `acceptance.md` and `verification` notes that a human also reads. Cost is one skill read. Acceptable.

## Under-constraint risks

No script proves a given spec file was actually run through `writing-for-agents`. Same class of gap as the old humanizer contract (pointer + test of pointers). Out of scope to add a prose linter.

## Recommended clarifications

Baked into the CURRENT spec: explicit default, root-README-only humanizer glob, `alwaysApply` failure case.

## Challenge verdict

PASS
