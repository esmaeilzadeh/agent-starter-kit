# Layout and Canonical Concepts

# 1. Objective

Build the smallest practical repository-level system that allows a developer to use AI agents as a delegated engineering workforce while preserving:

```text
human ownership of intent
human ownership of constraints and acceptance policy
explicit delegation boundaries
structured agent-to-agent handoffs
isolated Git workstreams
deterministic verification where possible
selective human escalation
specification state and drift visibility
engineering decision memory
result provenance
```

The kit must support a normal software repository and must not require the project to adopt a custom orchestration framework.

The kit should work with common agent environments such as:

```text
Codex
Claude Code
Cursor
other repository-aware coding agents
```

Do not build a bespoke multi-agent runtime in v1.

---

# 2. Core principles

## 2.1 Artifacts over conversations

Material engineering state must become repository artifacts or durable result records.

Chat is a temporary interaction surface. It is not the canonical engineering memory.

## 2.2 Human ownership must be visible

The repository must make the following explicit:

```text
What / Why
Constraints
Acceptance criteria
Delegation policy
Escalation rules
Human approval boundaries
```

## 2.3 LLMs are not the sole enforcement layer

Where a rule can be checked deterministically, prefer:

```text
script
Git hook
CI check
compiler
static analyzer
runtime test
security check
policy gate
```

over relying exclusively on an LLM instruction.

## 2.4 Capabilities do not imply authority

Tools may technically permit an agent to execute an action. Policy must determine whether the action is allowed.

## 2.5 Independent work must have isolated Git state

Do not silently continue from unrelated uncommitted changes.

## 2.6 Every material result must have provenance

At minimum:

```text
result → exact commit SHA
```

Where appropriate also:

```text
result → verification → spec → policy/skill references
```

## 2.7 Do not store raw agent traces by default

Do not turn Git into a transcript database. Full prompts, token streams, raw context, every tool call, and retry traces are optional operational/audit data, not required engineering state.

---

# 3. Repository layout

Create this structure:

```text
.
├── AGENTS.md
├── _ask/
│   ├── README.md
│   ├── guide/
│   │   └── README.md
│   ├── spec/
│   │   └── README.md
│   ├── agents/
│   │   ├── 00-explore.md
│   │   ├── 01-grill.md
│   │   ├── 02-spec.md
│   │   ├── 03-spec-challenge.md
│   │   ├── 04-spec-change.md
│   │   ├── 05-plan.md
│   │   ├── 06-implement.md
│   │   ├── 07-review.md
│   │   ├── 08-refactor.md
│   │   ├── 09-verify.md
│   │   └── 10-accept.md
│   ├── policies/
│   │   ├── delegation.md
│   │   ├── risk.md
│   │   ├── verification.md
│   │   ├── worktree.md
│   │   ├── workflow.md
│   │   └── git-flow.md
│   ├── decisions/
│   │   └── README.md
│   ├── skills/
│   │   ├── manifest.yaml
│   │   └── prepare-skills.sh
│   ├── scripts/
│   │   ├── check-clean-worktree.sh
│   │   ├── start-work.sh
│   │   ├── check-workstream.sh
│   │   ├── status.sh
│   │   ├── verify.sh
│   │   ├── record-result.sh
│   │   ├── record-run.sh
│   │   ├── sync-cursor-binding.sh
│   │   ├── install-kit.sh
│   │   ├── upgrade-kit.sh
│   │   └── setup.sh
│   ├── cursor-commands/
│   │   └── off-path.md
│   ├── tests/
│   ├── docs/
│   └── templates/
│       ├── explore-map.md
│       ├── intent.md
│       ├── spec.md
│       ├── spec-challenge.md
│       ├── spec-change.md
│       ├── plan.md
│       ├── review.md
│       ├── verification.json
│       ├── acceptance.md
│       ├── experiment-result.json
│       └── later-work.md
├── specs/
│   ├── current/
│   └── proposals/
├── work/
│   └── README.md
├── .later/
│   └── README.md
├── .ask.env.example
├── .ask/
│   └── README.md
├── ask
├── .agents/
│   └── ask/
│       ├── stages/
│       ├── bindings/
│       └── verification/
├── .cursor/
│   ├── hooks.json
│   ├── hooks/
│   ├── rules/
│   └── commands/
└── .gitignore
```

Do not create directories for hypothetical functionality beyond this baseline.

**Three layers (no generic-name collision):**

```text
_ask/     kit package (including kit scripts, kit tests, kit-author docs)
ask + AGENTS.md + .cursor/  thin adapter (`ask` dispatches kit scripts)
specs/ + work/        product engineering state (convention; created by start-work)
all other root names  product (docs/, scripts/, tests/, src/, …)
```

`install-kit` / `upgrade-kit` overlay the kit package and adapter only. They never write product `docs/`, `scripts/`, `tests/`, or `src/`.

The layout is intentionally repository-oriented rather than platform-oriented.

---

# 4. Canonical concepts

The kit uses these distinct concepts:

```text
Labor
Judgment
Capability
Authority
Accountability
Skill
Community Skill
Kit Protocol File
Skill Manifest
Skill Preparation
Explore Phase
Engineering Pipeline
Rule
Policy
Specification
Evidence
Provenance
```

Do not collapse them in documentation or implementation.

Examples:

```text
Community Skill:
How to perform grilling or wayfinding (pinned from skills.sh / source repo).

Kit Protocol File:
.agents/ask/stages/00-explore.md — the stage contract for Explore.
_ask/agents/00-explore.md is a pointer.

Skill Preparation:
Agent runs `./ask prepare` (skills CLI) to install pinned revisions.

Explore Phase:
Chart decisions until the destination is clear.

Engineering Pipeline:
01 Grill … 10 Accept after clarity.

Skill:
How to perform a code review.

Rule:
Do not cross architecture boundary X.

Policy:
Architecture changes require human approval.

Capability:
Agent can edit repository files.

Authority:
Agent is allowed to edit only the active workstream.

Accountability:
Project/team remains responsible for the outcome.
```

---

# 5. Canonical agent flow

The exact logical agent names are:

```text
00 Explore
01 Grill
02 Spec
03 Spec Challenge
04 Spec Change
05 Plan
06 Implement
07 Review
08 Refactor
09 Verify
10 Accept
```

Preserve `01`–`10` names for Guide ↔ kit mapping stability. `00 Explore` is the first-class stage for evidence gathering; it does not renumber the Engineering Pipeline.

When an inner-loop TaskGraph is active, `06 Implement` runs each task through
Red → Green → Refactor, independent Review, and local correction before
integration. `07 Review` and `08 Refactor` remain available as specialized task
roles; they are not unconditional outer-workstream phases. The outer pipeline
retains aggregate Verify and Accept. See the canonical
[`task-loop.md`](../../.agents/ask/task-loop.md) contract.

## 5.1 Explore Phase (`00`)

Use the request routes and entry rules in `_ask/policies/workflow.md`.

| Routing question | Stage | Completion |
| --- | --- | --- |
| Are knowledge gaps blocking the requested work? | 00 Explore | Evidence about the system, technologies, constraints, prior solutions, and documentation; remaining gaps and human decisions recorded. |
| Are goals, assumptions, or tradeoffs unresolved? | 01 Grill | Human decisions and complete intent for feature approval. |

Use either or both stages as needed. A clear goal can still need investigation;
an unclear goal alone does not make research mandatory. Explore separates facts
from human decisions and binds pinned Community Skills through Skill Preparation.

| Entry | Behavior |
| --- | --- |
| `/00-explore` or explicit “00-explore” | Apply request routing, then investigate the authorized question. For feature exploration, create `work/<id>/explore-map.md`. |
| Free on-path new task | State its route and whether facts, goals, or both need work; enter the corresponding stage within the request's authority. |
| `/01-grill` with unresolved goals | Clarify or challenge decisions; use Explore if factual gaps also block the work. |
| Real skip | Omit Explore and its map when evidence is sufficient; record `Explore skipped: evidence sufficient for intent.` in feature intent. Preserve earlier approved skip records. |

If Explore runs for a feature, its non-empty `Handoff to Intent` names evidence,
remaining gaps, and human decisions before Grill. Open preference questions do
not block that handoff. Standalone investigation ends with its report, without
entering the feature pipeline. `./ask start-work` must not seed an Explore Map.

Feature stages retain their required artifacts and authority gates. Other routes
use the bounded deliverables in the workflow policy rather than feature paperwork.

## 5.2 Engineering Pipeline (`01`–`10`)

The default pipeline after clarity:

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

The following workflow can interrupt the pipeline:

```text
Any stage
→ Specification change required
→ Spec Change Agent
→ Challenge
→ Human decision
→ revised accepted spec
→ affected work resumes
```

If fog returns at a scale that invalidates the destination itself, return to `00 Explore` rather than forcing Spec Change to do wayfinding.

---
