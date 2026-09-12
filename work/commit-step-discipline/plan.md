# Plan

## Specification

`specs/current/commit-step-discipline.md`

## Approach

The policy already landed on `main` at `61ff5d8`. This workstream records that and closes artifacts. No second policy rewrite.

## Work breakdown

1. ~~Policy + AGENTS + stage contracts + Cursor rule + ADR-0010~~ — done (`61ff5d8`).
2. Confirm no auto-commit hooks; push/merge still human-gated.
3. Verify + Accept.

## Risks

Global Cursor user rules still say “only commit when asked.” Agents must follow kit policy on `agent/<work-id>` anyway. Residual: a model that ignores both.

## Verification approach

- Grep policy surfaces for “without waiting” / override of “only commit when asked.”
- No hook in `.cursor/hooks` or `.git/hooks` that auto-commits.
- `./ask verify`

## Out of scope for this plan

Auto-commit hooks. Changing `start-work`. Merging other live branches.
