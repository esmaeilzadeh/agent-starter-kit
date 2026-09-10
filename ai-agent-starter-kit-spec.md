# AI Engineering Starter Kit — Build Specification

> Implementation contract for a repository-level starter kit that operationalizes [`ai-agent-engineering-guide.md`](./ai-agent-engineering-guide.md).
>
> The goal is not to build a new agent platform. The goal is to provide a portable engineering protocol that can be used by Codex, Claude Code, Cursor, or another agent runtime that can read repository instructions and use Git/shell/tooling.
>
> The starter kit and guide are a matched pair. Keep the names, artifacts, lifecycle states, and workflow relationships in this document stable so that a developer can move directly between the article and the repository implementation.

---

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
├── engineering/
│   ├── README.md
│   ├── agents/
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
│   │   └── verification.md
│   ├── decisions/
│   │   └── README.md
│   ├── skills/
│   │   └── manifest.yaml
│   └── templates/
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
├── scripts/
│   ├── check-clean-worktree.sh
│   ├── start-work.sh
│   ├── verify.sh
│   ├── record-result.sh
│   └── check-workstream.sh
└── .gitignore
```

Do not create directories for hypothetical functionality beyond this baseline.

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
Rule
Policy
Specification
Evidence
Provenance
```

Do not collapse them in documentation or implementation.

Examples:

```text
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

These names should be preserved because the guide references them.

The default flow is:

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

The following workflow can interrupt the main flow:

```text
Any stage
→ Specification change required
→ Spec Change Agent
→ Challenge
→ Human decision
→ revised accepted spec
→ affected work resumes
```

---

# 6. Artifact model

Every material phase should have an artifact.

## 6.1 Intent

Path:

```text
work/<work-id>/intent.md
```

Template:

```markdown
# Intent: <title>

## What

## Why

## Non-goals

## Known assumptions

## Open questions

## Human decisions
```

The artifact represents clarified human intent, not merely a copy of the original request.

---

## 6.2 Specification

Initial path:

```text
specs/proposals/<work-id>.md
```

Template:

```markdown
# Specification: <title>

## Status
PROPOSED

## Goal

## Non-goals

## Behavior

## Interfaces

## Constraints

## Invariants

## Failure cases

## Acceptance criteria

## Open questions

## Source intent
<work-id>
```

The specification must preserve a stable relationship to its source intent.

After acceptance, it may be promoted or copied to the project's canonical current location according to policy.

---

# 7. Specification lifecycle

Supported semantic states:

```text
OBSERVED
PROPOSED
ACCEPTED
IMPLEMENTED
VERIFIED
CURRENT
```

Recommended lifecycle:

```text
PROPOSED
   ↓
ACCEPTED
   ↓
IMPLEMENTED
   ↓
VERIFIED
   ↓
CURRENT
```

`OBSERVED` is used when the repository documents behavior that exists without necessarily asserting that it is the desired semantic contract.

Important invariants:

```text
Never silently rewrite an accepted spec during implementation.
Never infer that observed code behavior is the desired spec merely because it exists.
Never promote a proposed change to CURRENT without the required decision and verification.
```

---

# 8. Specification Challenge artifact

Path:

```text
work/<work-id>/spec-challenge.md
```

Minimum fields:

```markdown
# Specification Challenge

## Specification

## Ambiguities

## Hidden assumptions

## Counterexamples

## Conflicting requirements

## Acceptance-criteria gaps

## Recommended changes

## Outcome
PASS | ESCALATE
```

The challenge agent must not silently rewrite the accepted human intent.

---

# 9. Specification Change artifact

Path:

```text
work/<work-id>/spec-change.md
```

Template:

```markdown
# Specification Change Proposal

## Trigger

## Current specification

## Observed behavior / new analysis

## Problem with current specification

## Proposed semantic change

## Why the change is needed

## Impact

## Alternatives considered

## Required human decision

## Decision
PENDING | ACCEPTED | REJECTED
```

Use this workflow when:

```text
implementation reveals a requirement problem
analytics produces new understanding
review identifies a semantic mismatch
acceptance criteria need to change
business/domain invariant needs to change
```

The Spec Change Agent does not silently modify `specs/current/`.

---

# 10. Planning artifact

Path:

```text
work/<work-id>/plan.md
```

The plan must reference exactly one accepted specification revision.

Minimum structure:

```markdown
# Plan

## Accepted specification

## Scope

## Implementation tasks

## Verification tasks

## Dependencies

## Risks

## Escalation points

## Potential specification changes
```

The plan may decompose implementation but may not redefine requirements.

---

# 11. Review artifact

Path:

```text
work/<work-id>/review.md
```

Review finding format:

```markdown
## Finding RV-001
Severity: LOW | MEDIUM | HIGH | CRITICAL
Status: OPEN | FIXED | ACCEPTED | ESCALATED

### Claim

### Location

### Evidence

### Suggested correction
```

Review findings must be structured for machine consumption by the Refactor Agent.

Review should cover, as applicable:

```text
requirements
constraints
invariants
error paths
security
maintainability
tests
unintended scope
architecture
performance claims when relevant
```

Prefer concrete evidence to vague statements such as "this feels wrong."

---

# 12. Verification artifact

Path:

```text
work/<work-id>/verification.json
```

Minimum schema:

```json
{
  "verification_id": "",
  "work_id": "",
  "commit": "",
  "spec": "",
  "checks": [
    {
      "name": "",
      "status": "PASS",
      "evidence": ""
    }
  ],
  "created_at": ""
}
```

The `commit` field is mandatory.

The verifier must not report a check as passed unless the check actually ran or the repository has an explicitly documented equivalent evidence source.

---

# 13. Acceptance artifact

Path:

```text
work/<work-id>/acceptance.md
```

Minimum fields:

```markdown
# Acceptance

## Specification

## Code commit

## Verification

## Review summary

## Unresolved findings

## Risk class

## Acceptance decision
AUTO_ACCEPT_ELIGIBLE | HUMAN_APPROVAL_REQUIRED | REJECT

## Human decision

## Authority used
```

Acceptance must be policy-driven.

The Accept Agent assembles evidence and determines eligibility. It is not automatically the final human authority.

---

# 14. Result provenance

Path may be inside Git or an external result store depending on project needs.

Minimum schema:

```json
{
  "result_id": "",
  "work_id": "",
  "commit": "",
  "spec": "",
  "verification": "",
  "result": {},
  "created_at": ""
}
```

The result is invalid without an exact commit SHA.

For example:

```json
{
  "result_id": "order-cancel-perf-01",
  "work_id": "cancel-order",
  "commit": "8f31c42",
  "spec": "specs/current/cancel-order.md",
  "verification": "verify-17",
  "result": {
    "p95_ms": 83
  },
  "created_at": "2026-09-10T12:00:00Z"
}
```

The essential lineage is:

```text
which code
→ which commit
→ which spec
→ which verification
→ which result
```

Do not store full agent transcripts merely to satisfy provenance.

---

# 15. Pre-built agent contracts

## 15.1 01 Grill Agent

Purpose:

```text
Turn ambiguous human intent into an explicit Intent Artifact.
```

Must:

```text
ask questions
expose assumptions
distinguish What from Why
identify non-goals
identify unresolved decisions
stop when human judgment is required
```

Must not:

```text
invent business decisions
jump into implementation prematurely
pretend unresolved ambiguity is resolved
```

Output:

```text
work/<work-id>/intent.md
```

---

## 15.2 02 Spec Agent

Purpose:

```text
Turn clarified intent into an explicit engineering specification.
```

Must:

```text
preserve What and Why
make constraints explicit
define observable acceptance criteria
separate requirements from implementation preferences
mark uncertainty explicitly
```

Output:

```text
specs/proposals/<work-id>.md
```

---

## 15.3 03 Spec Challenge Agent

Purpose:

```text
Challenge the specification before implementation.
```

Must:

```text
look for ambiguity
look for conflicting constraints
construct concrete counterexamples
challenge acceptance criteria
look for unsupported assumptions
check alignment with Why
```

Output:

```text
work/<work-id>/spec-challenge.md
```

Gate:

```text
PASS → eligible for acceptance
ESCALATE → human decision required
```

---

## 15.4 04 Spec Change Agent

Purpose:

```text
Turn discovered semantic problems into explicit specification-change proposals.
```

Triggers:

```text
analytics reveals new intended behavior
implementation exposes a requirement conflict
review reveals semantic mismatch
acceptance criteria are discovered to be wrong
```

Must:

```text
preserve the current accepted spec
show why a change is proposed
identify impact
identify alternatives
request the required decision
```

Must not:

```text
rewrite current specs silently
change acceptance criteria merely to make tests pass
change business semantics without the required authority
```

---

## 15.5 05 Plan Agent

Purpose:

```text
Derive the implementation plan from an accepted specification.
```

Must:

```text
reference exactly one accepted spec
identify affected components
identify dependencies
identify verification steps
identify escalation points
identify possible spec-change triggers
```

Must not redefine the requirement.

---

## 15.6 06 Implement Agent

Purpose:

```text
Perform delegated implementation labor.
```

Hard preconditions:

```text
clean working tree
dedicated branch
accepted spec
active plan
no unrelated uncommitted changes
```

Default branch convention:

```text
agent/<work-id>
```

Must not:

```text
modify unrelated work
rewrite acceptance criteria to make tests pass
bypass policy
perform forbidden high-risk actions
continue through a mandatory escalation gate
```

At meaningful milestones, create commits so that important engineering states are recoverable and attributable.

---

## 15.7 07 Review Agent

Purpose:

```text
Independently inspect implementation against the accepted specification and project policy.
```

Must produce structured findings.

It should prefer evidence and concrete locations over generic criticism.

A review agent is not the sole acceptance mechanism.

---

## 15.8 08 Refactor Agent

Purpose:

```text
Resolve actionable review findings without silently changing requirements.
```

Input:

```text
accepted spec
review.md
current code
project rules
```

For each finding:

```text
FIX
ACCEPT WITH RATIONALE
ESCALATE
```

A finding may not be marked FIXED without the relevant verification being rerun.

If the finding implies a spec change, call the Spec Change workflow.

---

## 15.9 09 Verify Agent

Purpose:

```text
Produce evidence appropriate to the changed system and risk class.
```

At minimum, discover and run the repository's existing checks as applicable:

```text
type checks
lint
unit tests
integration/e2e tests
build
security checks
configured project checks
```

Do not hard-code a universal Node/Nest command set.

The verifier should inspect repository configuration and use project-specific commands.

It must record the exact commit SHA.

---

## 15.10 10 Accept Agent

Purpose:

```text
Assemble evidence and decide whether the work is eligible for acceptance under policy.
```

Possible outcomes:

```text
AUTO_ACCEPT_ELIGIBLE
HUMAN_APPROVAL_REQUIRED
REJECT
```

The agent must explain the outcome and cite evidence.

Human approval remains mandatory where delegation policy requires it.

---

# 16. Delegation policy

File:

```text
engineering/policies/delegation.md
```

The policy must define five things for each relevant task category:

```text
Allowed actions
Forbidden actions
Required evidence
Escalation conditions
Human approval conditions
```

Conservative default:

### Autonomous by default

```text
file creation/modification within assigned scope
routine refactoring
generated tests
routine review-finding fixes
local verification
documentation directly implied by an accepted change
```

### Escalate

```text
ambiguity in What/Why
acceptance-criteria changes
domain-invariant changes
public API changes not in approved spec
architecture-boundary changes
security-policy changes
destructive database/data operations
production-impacting actions
repeated non-converging fixes
contradictory evidence
insufficient evidence
```

### Never silently do

```text
broaden scope
weaken acceptance criteria
delete constraints because they are inconvenient
overwrite another workstream's uncommitted changes
claim verification without running it
promote observed behavior to canonical specification
rewrite accepted specification to unblock implementation
```

---

# 17. Risk policy

File:

```text
engineering/policies/risk.md
```

Risk classification must consider:

```text
reversibility
blast radius
external impact
data loss
security consequences
business consequences
```

Default:

```text
LOW
  autonomous + normal checks

MEDIUM
  autonomous + stronger verification

HIGH
  proposal + human approval

CRITICAL / IRREVERSIBLE
  human authority mandatory
```

Projects should customize this according to their domain.

Line count is not an adequate risk metric.

---

# 18. Verification policy

File:

```text
engineering/policies/verification.md
```

The policy should map classes of claims to appropriate evidence.

Example:

```text
Type correctness
→ compiler/type checker

API behavior
→ integration/contract tests

Security invariant
→ security check + targeted tests

Performance claim
→ reproducible benchmark

Architecture boundary
→ static/architectural check where available

Formal mathematical property
→ formal proof where justified
```

The kit must explicitly avoid claiming that one evidence source is universally strongest.

The evidence mechanism must fit the claim.

---

# 19. Human approval gates

Approval boundaries should be observable.

Minimum gates:

```text
G1  unresolved intent
G2  spec challenge escalation
G3  high-risk plan
G4  specification change proposal
G5  critical/high-risk review finding
G6  insufficient or conflicting verification evidence
G7  destructive/production action
G8  final acceptance where policy requires human approval
```

The implementation can use:

```text
marker files
CI requirements
shell scripts
branch protection
repository conventions
```

The important property is that a gate is explicit and enforceable where feasible.

---

# 20. Context assembly contract

The root `AGENTS.md` should instruct agents to assemble task context in approximately this order:

```text
1. root repository instructions
2. engineering/policies/delegation.md
3. risk/verification policy as relevant
4. task intent
5. accepted specification
6. relevant engineering decisions
7. relevant skill references
8. active plan
9. relevant code
```

Agents must not assume that every document in the repository should be injected into every task.

The objective is **relevant context with explicit provenance**.

---

# 21. Skills manifest

File:

```text
engineering/skills/manifest.yaml
```

Purpose:

```text
explicitly declare the engineering methods the project relies on
```

Example:

```yaml
skills:
  grilling:
    source: external-or-local-reference
    revision: pinned-revision
    role: intent-clarification

  specification:
    source: openspec-or-project-reference
    revision: pinned-revision
    role: specification

  review:
    source: community-or-project-reference
    revision: pinned-revision
    role: code-review
```

Do not require all external skills to be vendored.

Do require critical external skills to have a visible, reviewable revision reference.

Avoid:

```text
latest
```

for critical engineering methods.

---

# 22. Decision memory

Path:

```text
engineering/decisions/
```

Use simple ADR-style documents.

Each decision should ideally state:

```text
Context
Decision
Why
Alternatives
Consequences
Status
```

Decision records explain why constraints exist. They are not substitutes for the current specification.

---

# 23. Git guardrails

## 23.1 `check-clean-worktree.sh`

Behavior:

```text
exit 0 → working tree clean
exit non-zero → working tree dirty
```

It must not stash, reset, or absorb user changes.

## 23.2 `start-work.sh <work-id>`

Behavior:

```text
1. require clean working tree
2. verify Git repository
3. identify default/main branch
4. create or switch to dedicated work branch
5. create work/<work-id>/ artifacts
6. print current HEAD SHA
7. print active branch
```

Default branch convention:

```text
agent/<work-id>
```

The script must refuse to silently proceed when unrelated local changes exist.

## 23.3 `check-workstream.sh`

Before delegated work, verify:

```text
branch is dedicated to current work-id
working tree is clean or changes are explicitly attributable to current work
accepted spec exists
plan exists
```

This can be called by agent instructions before implementation/review/refactor.

---

# 24. Verification script

Provide:

```text
scripts/verify.sh
```

It should:

```text
detect project/package manager where possible
read project-specific configuration
run configured mandatory checks
fail on mandatory failures
print exact commit SHA
emit machine-readable verification output
```

Do not hard-code NestJS, Node, Python, Rust, or any other specific technology into the core.

Provide extension/configuration points for the consuming repository.

---

# 25. Result recording script

Provide:

```text
scripts/record-result.sh <result-file>
```

It should validate or inject:

```text
current commit SHA
work ID
spec reference
verification reference
```

It must refuse to record a result when no exact commit SHA can be obtained.

A result such as:

```text
"new version is faster"
```

is not valid without an identifiable code state.

---

# 26. Failure convergence

The starter kit must protect against non-converging autonomous loops.

Example:

```text
Review A
→ Refactor
→ Review A
→ Refactor
→ Review A
```

After a configurable number of unsuccessful repair cycles, stop and escalate.

A conservative default is:

```text
2–3 unsuccessful repair cycles
```

Do not treat unlimited retry as free labor.

Retries consume:

```text
compute
latency
human attention
risk budget
```

---

# 27. Conflict resolution

The policy should define precedence among competing constraints.

Suggested starting point:

```text
explicit human requirement
    > domain invariant
    > security/safety constraint
    > accepted specification
    > correctness
    > reliability
    > performance
    > maintainability/style
```

This is a template, not a universal law.

The project must customize it.

Model majority must not be the default authority.

---

# 28. Acceptance debt visibility

The starter kit should be able to expose at least a lightweight signal when work has accumulated without sufficient evidence.

A simple implementation may track:

```text
work items completed
verification records present
acceptance decisions present
unresolved high-risk findings
```

The kit does not need a complex dashboard in v1.

It must at least make it possible to identify:

```text
engineering output without corresponding evidence
```

---

# 29. Provenance and state storage boundaries

The starter kit must distinguish three classes of data.

## 29.1 Durable engineering state

Keep in repository/version control when appropriate:

```text
code
specs
project-specific rules
policies
decisions
skill manifest
acceptance artifacts
verification references
```

## 29.2 Compact execution/provenance records

Keep as repository artifacts or external result records:

```text
run ID
commit SHA
spec reference
policy/skill references
verification ID
result ID
```

## 29.3 Raw execution telemetry

Do not store by default:

```text
full prompts
full context dumps
all tokens
every tool call
all retry transcripts
```

Store those separately only when an explicit audit/security/debugging requirement exists.

---

# 30. Workstream directory convention

For a task `cancel-order`:

```text
work/cancel-order/
├── intent.md
├── spec-challenge.md
├── spec-change.md      # only when needed
├── plan.md
├── review.md
├── verification.json
└── acceptance.md
```

Canonical spec proposal:

```text
specs/proposals/cancel-order.md
```

Canonical current spec after the required lifecycle:

```text
specs/current/cancel-order.md
```

Branch:

```text
agent/cancel-order
```

---

# 31. Minimal complete example

For `cancel-order`:

```text
Human
  → states What/Why

01 Grill
  → work/cancel-order/intent.md

02 Spec
  → specs/proposals/cancel-order.md

03 Spec Challenge
  → work/cancel-order/spec-challenge.md

Human
  → accepts spec

05 Plan
  → work/cancel-order/plan.md

06 Implement
  → branch agent/cancel-order
  → commit C1

07 Review
  → work/cancel-order/review.md

08 Refactor
  → commit C2

09 Verify
  → work/cancel-order/verification.json

10 Accept
  → work/cancel-order/acceptance.md

Human approval
  → only where policy requires it
```

If review discovers:

```text
"Current specification is semantically wrong"
```

do not patch the spec silently.

Instead:

```text
04 Spec Change
  → work/cancel-order/spec-change.md
  → decision
  → revised spec
  → affected implementation
  → verification
```

---

# 32. Analytics and specification evolution example

Suppose a performance analysis reveals:

```text
Current behavior:
API blocks while payment provider completes.

Analysis:
User only needs immediate acknowledgement.
```

The system should not automatically rewrite the current spec.

Instead:

```text
Analytics result
→ proposed semantic change
→ Spec Change Agent
→ Spec Challenge
→ human decision
→ accepted spec revision
→ implementation
→ verification
```

The experiment result must reference the exact commit it evaluated.

---

# 33. Acceptance example

For a low-risk refactor:

```text
review findings resolved
unit tests pass
type checks pass
integration tests pass
no scope expansion
commit identified
```

Policy may return:

```text
AUTO_ACCEPT_ELIGIBLE
```

For a destructive migration:

```text
verification passes
```

but policy may still require:

```text
HUMAN_APPROVAL_REQUIRED
```

This demonstrates the separation between evidence and authority.

---

# 34. Root `AGENTS.md` contract

The root file should remain short and operational.

It should instruct every agent that:

```text
This repository uses the AI Engineering Starter Kit.

Before independent work:
- require a clean working tree;
- use a dedicated branch;
- identify work-id;
- identify accepted specification;
- read relevant policies.

During work:
- stay within assigned scope;
- do not silently change What/Why or acceptance criteria;
- follow escalation policy;
- preserve workstream isolation;
- commit meaningful states.

Before claiming completion:
- run configured verification;
- record exact commit SHA;
- leave required structured artifacts.
```

Do not copy the entire guide into `AGENTS.md`.

---

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
templates
policies
agent instruction files
spec lifecycle conventions
```

## Phase 2 — Safety and traceability

Build:

```text
clean-tree check
start-work
workstream check
verification script
result recording
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
external skill installer/update tooling
experiment store
model-specific adapters
richer dashboards
```

---

# 37. Acceptance criteria for the starter kit itself

The kit is complete when a developer can copy it into an ordinary software repository and execute a small task through:

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
What were we trying to do?
Why?
Which spec was accepted?
Which policy/skill references applied?
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
| What / Why | `work/<work-id>/intent.md` |
| Intent Grilling | `01-grill.md` |
| OpenSpec / Specification | `02-spec.md`, `specs/` |
| Specification Challenge | `03-spec-challenge.md` |
| Specification Change | `04-spec-change.md` |
| Planning | `05-plan.md` |
| Delegated implementation | `06-implement.md` |
| Structured review | `07-review.md` |
| Delegated refactor | `08-refactor.md` |
| Verification | `09-verify.md`, `scripts/verify.sh` |
| Acceptance | `10-accept.md`, `acceptance.md` |
| Delegation policy | `engineering/policies/delegation.md` |
| Risk policy | `engineering/policies/risk.md` |
| Verification policy | `engineering/policies/verification.md` |
| Skill provenance | `engineering/skills/manifest.yaml` |
| Decision memory | `engineering/decisions/` |
| Spec state | `specs/current/`, `specs/proposals/`, status field |
| Git hygiene | `check-clean-worktree.sh`, `start-work.sh`, `check-workstream.sh` |
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
