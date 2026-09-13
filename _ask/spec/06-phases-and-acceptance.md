# Phases, Acceptance, and Mapping

# 35. What not to build in v1

Do not build:

```text
custom multi-agent runtime
full agent transcript database
universal formal verification system
autonomous production deployment platform
automatic rewriting of accepted specs
complex centralized state database replacing Git
```

The starter kit is:

```text
repository protocol
+
agent instruction files
+
small deterministic scripts
+
artifacts/templates
+
policy files
```

---

# 36. Implementation phases

## Phase 1 — Repository protocol

Build:

```text
layout
AGENTS.md
templates (including explore-map)
policies
agent instruction files (00 Explore + 01–10)
spec lifecycle conventions
skills manifest + prepare-skills instruction/script
```

## Phase 2 — Safety and traceability

Build:

```text
clean-tree check
start-work
workstream check
verification script
result recording
Skill Preparation wired for Cursor (skills CLI / documented commands)
```

## Phase 3 — Workflow quality

Build:

```text
structured review findings
spec-change workflow
escalation markers
failure-convergence detection
risk classification
```

## Phase 4 — Optional integrations

Only after the repository protocol works reliably:

```text
CI integration
richer skill-update tooling beyond prepare-skills
experiment store
additional runtime adapters beyond Cursor-first
richer dashboards
```

**v1 destination for this kit effort:** Phases **1–2** including Explore protocol (not Phase 3 completeness).

---

# 37. Acceptance criteria for the starter kit itself

The kit is complete when a developer can copy it into an ordinary software repository and:

1. Run **Explore (`00`)** on a foggy idea until handoff is clear (or skip when already clear), preparing pinned Community Skills by instruction.
2. Execute a small task through:

```text
Intent
→ Grill
→ Spec
→ Spec Challenge
→ Plan
→ Implement
→ Review
→ Refactor
→ Verify
→ Accept
```

without relying on the previous chat conversation as canonical state.

The resulting repository/process must be able to answer:

```text
Was Explore required? What destination did it hand off?
What were we trying to do?
Why?
Which spec was accepted?
Which policy/skill pins applied?
Which branch did the work use?
Which commit implemented it?
What review findings existed?
What changed after review?
What verification ran?
Which exact commit produced the reported result?
Was human approval required?
Who/what had the authority to accept it?
```

The negative-path test is mandatory:

```text
Start with intentionally dirty working tree
→ ./ask start-work
→ must refuse to proceed
```

The spec-change negative path is also mandatory:

```text
Agent attempts to change accepted semantic requirement
→ must not silently modify canonical spec
→ must produce escalation/spec-change artifact
```

---

# 38. Guide ↔ starter-kit mapping

The implementation must preserve this mapping:

| Guide concept | Starter-kit implementation |
|---|---|
| Explore / wayfinding / R&D on-ramp | `_ask/agents/00-explore.md`, `explore-map` template, Explore skills in manifest |
| What / Why | `work/<work-id>/intent.md` |
| Intent Grilling | `_ask/agents/01-grill.md` |
| OpenSpec / Specification | `_ask/agents/02-spec.md`, `specs/` |
| Specification Challenge | `_ask/agents/03-spec-challenge.md` |
| Specification Change | `_ask/agents/04-spec-change.md` |
| Planning | `_ask/agents/05-plan.md` |
| Delegated implementation | `_ask/agents/06-implement.md` |
| Structured review | `_ask/agents/07-review.md` |
| Delegated refactor | `_ask/agents/08-refactor.md` |
| Verification | `_ask/agents/09-verify.md`, `./ask verify` |
| Acceptance | `_ask/agents/10-accept.md`, `acceptance.md` |
| Guide (modular) | `_ask/guide/` |
| Build Spec (modular) | `_ask/spec/` |
| Delegation policy | `_ask/policies/delegation.md` |
| Risk policy | `_ask/policies/risk.md` |
| Verification policy | `_ask/policies/verification.md` |
| Skill provenance + preparation | `_ask/skills/manifest.yaml`, `./ask prepare` |
| Humanizer on docs and specs | `_ask/skills/manifest.yaml` (`humanizer`), `.cursor/rules/humanizer-docs-specs.mdc`, ADR 0017 |
| Load-bearing grilling + skill-before-grill | `_ask/agents/01-grill.md`, ADR 0016 |
| Human-only tracker/MCP setup | `./ask setup`, `.ask.env.example` |
| Decision memory | `_ask/decisions/` |
| Spec state | `specs/current/`, `specs/proposals/`, status field |
| Worktree / branch / commit discipline | `_ask/policies/worktree.md`, `./ask check-clean`, `./ask start-work` |
| Workflow guidance (not a lock) | `_ask/policies/workflow.md`, `./ask status` warnings |
| Session-only off-path | `_ask/cursor-commands/off-path.md`, `./ask sync` |
| Later inbox | `.later/`, `_ask/templates/later-work.md` |
| Git hygiene | `./ask check-clean`, `./ask start-work`, `./ask check-workstream`, `./ask status` |
| Cursor Binding sync | `./ask sync`, `.cursor/` |
| Install overlay | `./ask install` |
| Result provenance | `./ask record-result`, result schema |
| Experiment run provenance | `./ask record-run`, `results/<run-id>/` |
| Escalation | policy + workflow gates |
| Acceptance debt | evidence/acceptance state records |
| Engineering-system evolution | review/verification outputs → rule/skill/check improvements |

Do not rename these relationships without also updating the companion guide.

---

# 39. Final implementation principle

The starter kit is not intended to prove that AI agents are always reliable.

It is intended to make reliability **observable, bounded, and improvable**.

The core implementation strategy is:

```text
Human intent
→ [Explore when foggy → clear destination]
→ explicit artifacts
→ bounded agent labor
→ structured handoffs
→ deterministic verification where possible
→ explicit escalation
→ versioned engineering state
→ commit-anchored results
→ human authority where required
```

The kit succeeds when a developer can delegate substantial engineering labor without losing the ability to answer:

> **What did we intend, what did the agents do, under which rules, what evidence do we have, and exactly which engineering state produced the result?**
