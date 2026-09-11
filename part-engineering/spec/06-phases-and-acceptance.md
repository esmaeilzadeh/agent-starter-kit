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
→ start-work.sh
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
| Explore / wayfinding / R&D on-ramp | `part-engineering/agents/00-explore.md`, `explore-map` template, Explore skills in manifest |
| What / Why | `work/<work-id>/intent.md` |
| Intent Grilling | `part-engineering/agents/01-grill.md` |
| OpenSpec / Specification | `part-engineering/agents/02-spec.md`, `specs/` |
| Specification Challenge | `part-engineering/agents/03-spec-challenge.md` |
| Specification Change | `part-engineering/agents/04-spec-change.md` |
| Planning | `part-engineering/agents/05-plan.md` |
| Delegated implementation | `part-engineering/agents/06-implement.md` |
| Structured review | `part-engineering/agents/07-review.md` |
| Delegated refactor | `part-engineering/agents/08-refactor.md` |
| Verification | `part-engineering/agents/09-verify.md`, `part-engineering/scripts/verify.sh` |
| Acceptance | `part-engineering/agents/10-accept.md`, `acceptance.md` |
| Guide (modular) | `part-engineering/guide/` |
| Build Spec (modular) | `part-engineering/spec/` |
| Delegation policy | `part-engineering/policies/delegation.md` |
| Risk policy | `part-engineering/policies/risk.md` |
| Verification policy | `part-engineering/policies/verification.md` |
| Skill provenance + preparation | `part-engineering/skills/manifest.yaml`, `prepare-skills.sh` |
| Decision memory | `part-engineering/decisions/` |
| Spec state | `specs/current/`, `specs/proposals/`, status field |
| Worktree / branch / commit discipline | `part-engineering/policies/worktree.md`, `part-engineering/scripts/check-clean-worktree.sh`, `part-engineering/scripts/start-work.sh` |
| Git hygiene | `check-clean-worktree.sh`, `start-work.sh`, `check-workstream.sh` |
| Cursor Binding sync | `part-engineering/scripts/sync-cursor-binding.sh`, `.cursor/` |
| Install overlay | `part-engineering/scripts/install-kit.sh` |
| Result provenance | `record-result.sh`, result schema |
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
