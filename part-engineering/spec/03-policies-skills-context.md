# Policies, Skills, and Context

# 15. Pre-built agent contracts

## 15.0 00 Explore Agent

Purpose:

```text
When the destination is foggy, chart decisions (and run research/prototypes)
until What/Why can be owned — then hand off into Intent / 01 Grill.
```

Must:

```text
treat Explore as decision work, not implementation
keep a durable map (explore-map artifact and/or tracker map)
separate human decisions from research facts
prepare Community Skills declared for Explore via Skill Preparation
expand grilling questions before resolving Explore decisions (Grilling Expansion)
stop and hand off when the destination is clear
```

Must not:

```text
silently start Implement to "figure it out"
vendor skill bodies instead of pinned prepare
pretend fog is cleared while material decisions remain open
reimplement a full community wayfinder stack when a pinned skill suffices
```

Bind (via Skill Manifest), do not copy by default:

```text
wayfinder / research / prototype / grilling (and related)
discovery: skills.sh as a starting index
```

Output:

```text
work/<work-id>/explore-map.md (and/or tracker map pointer)
handoff notes sufficient for 01 Grill
```

Gate:

```text
DESTINATION_CLEAR → eligible for Intent / 01 Grill
STILL_FOGGY → continue Explore (or escalate to human)
```

---

## 15.1 01 Grill Agent

Purpose:

```text
Turn ambiguous human intent into an explicit Intent Artifact.
```

Must:

```text
ask questions
expand each decision question before resolution (alternatives, tradeoffs, failure modes — not bare A/B/C alone)
expose assumptions
distinguish What from Why
identify non-goals
identify unresolved decisions
stop when human judgment is required
never treat “all ok” as valid if the frontier was never expanded
```

Must not:

```text
invent business decisions
jump into implementation prematurely
pretend unresolved ambiguity is resolved
auto-approve recommended answers without explicit human confirmation
resolve on letter choices the human has not had expanded enough to refuse with understanding
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
part-engineering/policies/delegation.md
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
part-engineering/policies/risk.md
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
part-engineering/policies/verification.md
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
2. part-engineering/policies/delegation.md
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
part-engineering/skills/manifest.yaml
```

Purpose:

```text
explicitly declare Community Skills the project relies on as versioned dependencies
(like a package lockfile — source + pin + role — not vendored skill trees)
```

Discovery starting point:

```text
https://www.skills.sh/
```

### Schema (v1)

```yaml
skills:
  wayfinder:
    source: mattpocock/skills          # owner/repo or full git URL
    revision: "v1.2.3"               # tag, branch, or 40-char SHA — required; never latest
    skill: wayfinder                 # CLI --skill; required when source repo has many skills
    role: explore-map                # kit semantics (explore-map, intent-clarification, …)
    required: true                   # optional; prepare fails closed when true
```

Pin maps to the skills CLI as `source#revision` (`#` is the revision fragment; do not use `@` for versions).

Dual lock:

```text
part-engineering/skills/manifest.yaml  → authoritative human-reviewed pins
skills-lock.json (repo root)      → CLI install record; commit it
.agents/skills/                   → prepared bodies; gitignore by default; regenerate via prepare
```

**Cloud:** project agents must run `prepare-skills.sh` before roles that need Community Skills (do not rely on global installs). Optional documented escape: `--vendor` / `--copy` with committed `.agents/skills/` for environments that cannot prepare at session start — not the default.

### Skill Preparation

Provide:

```text
part-engineering/skills/prepare-skills.sh
```

Behavior:

```text
1. read manifest.yaml
2. fail if revision missing or equals latest
3. for each entry: npx skills add "${source}#${revision}" --skill "${skill}" --agent cursor --yes
4. verify .agents/skills/<skill>/SKILL.md exists
5. print summary; exit non-zero on required failures
```

Agents must be instructed (via `AGENTS.md` / stage contracts) to run preparation before roles that need Community Skills.

Do not vendor Community Skill bodies into the product repo by default.

Avoid:

```text
latest
skills update
```

for critical engineering methods (bump pins deliberately in the manifest instead).

Kit Protocol Files (`part-engineering/agents/*.md`, policies, templates, `part-engineering/guide/`, `part-engineering/spec/`) are **shipped by the kit**. Community Skills are **prepared from pins**.

---

# 22. Decision memory

Path:

```text
part-engineering/decisions/
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
