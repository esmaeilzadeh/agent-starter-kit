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
├── part-engineering/
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
│   │   └── worktree.md
│   ├── decisions/
│   │   └── README.md
│   ├── skills/
│   │   ├── manifest.yaml
│   │   └── prepare-skills.sh
│   ├── scripts/
│   │   ├── check-clean-worktree.sh
│   │   ├── start-work.sh
│   │   ├── check-workstream.sh
│   │   ├── verify.sh
│   │   ├── record-result.sh
│   │   ├── sync-cursor-binding.sh
│   │   ├── install-kit.sh
│   │   └── upgrade-kit.sh
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
│       └── experiment-result.json
├── specs/
│   ├── current/
│   └── proposals/
├── work/
│   └── README.md
├── pek
├── .cursor/
│   ├── hooks.json
│   ├── hooks/
│   └── rules/
└── .gitignore
```

Do not create directories for hypothetical functionality beyond this baseline.

**Three layers (no generic-name collision):**

```text
part-engineering/     kit package (including kit scripts, kit tests, kit-author docs)
pek + AGENTS.md + .cursor/  thin adapter (`pek` dispatches kit scripts)
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
part-engineering/agents/00-explore.md — the stage contract for Explore.

Skill Preparation:
Agent runs `./pek prepare` (skills CLI) to install pinned revisions.

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

Preserve `01`–`10` names for Guide ↔ kit mapping stability. `00 Explore` is the first-class on-ramp for foggy / R&D work; it does not renumber the Engineering Pipeline.

## 5.1 Explore Phase (`00`)

Use Explore when the destination is not yet clear enough to own What/Why as Intent:

```text
foggy idea / large feature / R&D question
→ 00 Explore
   → decision map (wayfinder-shaped)
   → research tickets (facts)
   → prototypes when needed
→ destination clear
→ enter Engineering Pipeline at Intent / 01 Grill
```

Explore **must**:

```text
keep decisions as durable artifacts (map + resolved tickets / ADRs as appropriate)
distinguish decisions (human) from facts (research)
bind Community Skills via the Skill Manifest + Skill Preparation
hand off a clear destination into Grill / Spec — not silent chat residue
```

Explore **must not**:

```text
treat Implement as the place to discover the product destination
vendor Community Skill bodies into the repo by default
claim the destination is clear while material decisions remain open
```

Skip `00` when the human already has a destination sharp enough for Intent → Grill.

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
