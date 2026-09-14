# Plan

## Specification

`specs/current/humanizer-human-docs-only.md` (includes accepted spec-change)

## Approach

Keep both Community Skill pins. Narrow the humanizer Cursor rule to the human-facing globs. Add a writing-for-agents Cursor rule for machine-first files. Point Spec-stage contracts at writing-for-agents. Supercede `pin-humanizer.md`. Update ADR 0017 and the thin Build Spec / mapping / CONTEXT pointers. Extend the existing contract test. Do not rewrite existing prose.

## Work breakdown

1. Pin `writing-for-agents` in `_ask/skills/manifest.yaml`. Run `./ask prepare`. Commit lock.
2. Mark `specs/current/pin-humanizer.md` SUPERSEDED. Keep `humanizer-human-docs-only.md` CURRENT.
3. Replace humanizer apply text in `02` / `03` / `04` with writing-for-agents. `./ask sync`.
4. Change `.cursor/rules/humanizer-docs-specs.mdc` to globs `README.md`, `_ask/guide/**/*.md`, `_ask/docs/demo/**/*.md`; `alwaysApply: false`. Add `.cursor/rules/writing-for-agents-machine-docs.mdc`.
5. Update ADR 0017, `_ask/spec/03-policies-skills-context.md`, `_ask/spec/06-phases-and-acceptance.md`, `_ask/MAPPING.md`, `_ask/skills/README.md`, `CONTEXT.md`.
6. Update `_ask/tests/test-humanizer-docs-specs.sh` for both pins, both rules, and “no humanizer apply” on `02` / `03` / `04`.
7. `./ask verify`.

## Risks

- `mattpocock/skills@v1.2.3` missing `writing-for-agents` (then pin fails; stop and escalate).
- Sync overwrites generated stage skills; source contracts must be correct first.
- A broad README glob humanizes `_ask/README.md` (test must reject `alwaysApply: true` on the humanizer rule and require the listed globs).

## Verification approach

`./ask verify` plus the updated contract test.

## Out of scope for this plan

Rewriting existing Guide / spec / ADR / README prose. A prose linter. Changing stage-model spawn behavior.
