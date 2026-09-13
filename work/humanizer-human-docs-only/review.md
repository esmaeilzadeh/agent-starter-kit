# Review

## Model

model: grok-4.6
runtime: cursor
parent_model: grok-4.6

Human said go till end. Same-family warn waived by that confirm.

## Scope

`specs/current/humanizer-human-docs-only.md` vs manifest, lock, stock rules, Spec-stage contracts, ADR 0017, superseded `pin-humanizer.md`, contract test.

## Findings

- Manifest pins `writing-for-agents` from `mattpocock/skills` @ `v1.2.3`, role `agent-docs`, `required: true`. `humanizer` @ `v3.0.0` stays.
- `skills-lock.json` records `writing-for-agents` at `v1.2.3` with hash `ccfa1e94d8f6ab5c6a1edd55293ca477faf93c39207771331efdb1e798ed21d6`.
- Humanizer rule is glob-limited (`README.md`, `_ask/guide/**/*.md`, `_ask/docs/demo/**/*.md`) and `alwaysApply: false`.
- Writing-for-agents rule exists and names embedded mode for machine-first files.
- `02` / `03` / `04` require `writing-for-agents` and do not apply `humanizer/SKILL.md`.
- `pin-humanizer.md` is SUPERSEDED and points at this spec.
- `_ask/tests/test-humanizer-docs-specs.sh` passed after `./ask sync`.

No blocking mismatch with the spec.

## Suggested fixes

None required for acceptance.

## Residual risks

- No prose linter proves a given spec file was actually run through `writing-for-agents` (same pointer-only gap as the old humanizer contract; out of scope).
- Upgrade does not add the `writing-for-agents` pin to an existing consumer manifest.

## Review verdict

PASS
