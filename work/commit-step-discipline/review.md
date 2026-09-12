# Review

## Scope

`specs/current/commit-step-discipline.md` vs the tree on `main` (`61ff5d8` and later).

## Findings

None blocking. The policy is already current:

- `_ask/policies/worktree.md` “Commit at each meaningful step (hard)” plus work-branch safety rationale.
- `AGENTS.md` item 7; Plan/Implement contracts; delegation “never silently wait to be asked.”
- `.cursor/rules/commit-step-discipline.mdc` and bootstrap rule point at policy.
- ADR-0010 matches.
- `.cursor/hooks` only wrap check scripts; no auto-commit.

## Suggested fixes

None.

## Residual risks

A global Cursor “only commit when asked” user rule can still distract a model. Kit text overrides it; enforcement is still agent-followed, not mechanical.

## Review verdict

Pass. No refactor.
