# Specification: stepwise commits on work branches

## Status

CURRENT

## Goal

On `agent/<work-id>`, agents commit after each meaningful step without waiting to be asked. The dedicated branch is the safety boundary so those commits do not land on `main`.

## Non-goals

Changing `start-work` branching defaults. Auto-committing via hooks. Changing how `main` is merged.

## Behavior

- While executing a plan on `agent/<work-id>`, waiting for “please commit” is a policy violation.
- Kit policy overrides global “only commit when asked” habits on that branch.
- Push, force-push, amend of pushed commits, and merges to `main`/`master` still need explicit human direction.
- One plan → one `agent/<work-id>` branch.

## Interfaces

- `_ask/policies/worktree.md`
- `_ask/policies/delegation.md` (never silently wait to be asked)
- `AGENTS.md` checklist item 7
- `.cursor/rules/commit-step-discipline.mdc`
- `_ask/agents/05-plan.md` and `06-implement.md`
- ADR-0010

## Acceptance criteria

- `worktree.md` states commit-after-each-step as hard, with the work-branch safety rationale.
- `AGENTS.md` and Implement/Plan contracts tell agents not to wait to be asked.
- A Cursor rule points at that policy.
- No git hook auto-commits.
- `./ask verify` passes.

## Source intent

`work/commit-step-discipline/intent.md`
