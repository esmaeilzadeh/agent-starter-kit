# Agent Starter Kit

A practical guide and copy-ready starter kit for teams that want to run AI agents as a **delegated engineering workforce**—with clear scope, quality gates, and measurable outcomes.

## Who this is for

This repository is for developers and tech leads who want agents to execute real engineering work (triage, implementation, verification, and review) while humans stay responsible for prioritization, architecture, and final decisions.

## What you get

- A clear operating model for delegated engineering
- Prompt and task templates that reduce ambiguity
- A PR readiness checklist focused on quality and safety
- A simple rollout path from pilot tasks to team-wide adoption

## 1) Operating model: Human-led, agent-executed

Use this split of responsibilities:

- **Human responsibilities**
  - Define business outcomes and priorities
  - Set constraints (security, architecture, compatibility)
  - Approve risky design decisions
  - Review and merge
- **Agent responsibilities**
  - Explore code and propose a plan
  - Implement scoped changes
  - Write/update tests where appropriate
  - Run validation (build/lint/tests/security checks)
  - Report progress in small increments

Treat agent outputs as implementation drafts with evidence, not truth.

## 2) Delegation loop (repeat per task)

1. Create a precise work item using `starter-kit/templates/agent-task.md`
2. Ask the agent to restate requirements and constraints
3. Require a minimal-change implementation plan
4. Require targeted validation before full-suite validation
5. Require explicit reporting of:
   - changed files
   - test/build/security results
   - open risks or follow-ups
6. Human reviews diff quality, then merges or requests revisions

## 3) Rollout plan

- **Week 1 (pilot):** 3–5 low-risk bug fixes/docs updates
- **Week 2 (expand):** medium-scope refactors behind tests
- **Week 3+:** include CI triage and repetitive maintenance tasks

Track:

- lead time to merge
- escaped defects
- review iterations per PR
- human time saved per task

## 4) Guardrails that prevent “opaque code generation”

Require every task to include:

- scope boundaries (what not to change)
- explicit validation commands
- security and secrets checks
- progress updates with checklist status
- final summary with unresolved risks

Use the template files in `starter-kit/` as defaults for new tasks.

## Repository contents

- `starter-kit/prompts/delegated-engineer.system.md`
  - System prompt baseline for delegated engineering behavior
- `starter-kit/templates/agent-task.md`
  - Task brief template for scoped, auditable work
- `starter-kit/checklists/pr-ready.md`
  - Final PR checklist for quality/safety gates

## Quick start

1. Copy `starter-kit/templates/agent-task.md` into your issue or task tracker
2. Start the agent with `starter-kit/prompts/delegated-engineer.system.md`
3. Require completion of `starter-kit/checklists/pr-ready.md` before merge
4. Tune templates based on your codebase and CI pipeline

---

If you adopt this kit, start small, enforce evidence-based validation, and scale only what consistently improves quality and delivery speed.
