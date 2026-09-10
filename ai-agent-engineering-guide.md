# Engineering with AI Agents: Delegation of Engineering Labor Without Losing Engineering Ownership

> A practical, detailed guide for developers who want to use AI agents as a delegated engineering workforce rather than as an opaque code generator.
>
> Companion implementation contract: [`ai-agent-starter-kit-spec.md`](./ai-agent-starter-kit-spec.md)
>
> This guide and the starter kit are intentionally designed as a matched pair. The article explains the concepts, boundaries, and reasoning model. The starter kit turns those concepts into repository artifacts, pre-built agent roles, workflow gates, and Git/provenance conventions.

---

## 1. The problem this guide solves

AI makes it possible to delegate much more software-engineering labor than before. The obvious use case is asking an agent to write code. The more important opportunity is broader:

> **Treat software engineering as a collection of different kinds of labor and deliberately allocate each kind to the actor best suited to perform it.**

A conventional developer may personally perform all of these activities:

```text
understand requirement
→ clarify ambiguity
→ design
→ plan
→ implement
→ debug
→ review
→ refactor
→ test
→ benchmark
→ decide whether the result is acceptable
```

An AI-enabled workflow can decompose this work much further:

```text
Human
  → intent / What / Why

Grill Agent
  → ambiguity reduction

Spec Agent
  → specification

Spec Challenge Agent
  → challenge the specification

Plan Agent
  → implementation plan

Implement Agent
  → coding labor

Review Agent
  → review labor

Refactor Agent
  → correction labor

Verify Agent + deterministic tooling
  → evidence

Accept Agent / Human
  → acceptance under policy
```

This is **Division of Engineering Labor**, not merely "AI-assisted coding."

The central question therefore changes from:

> Should I let AI code?

into:

> **Which engineering labor should be delegated, which judgment should remain human, what authority does each actor have, what evidence is required, and how can the resulting work remain traceable?**

---

# 2. Division of Engineering Labor

## 2.1 Labor is not one thing

Engineering contains different classes of work. A useful decomposition is:

- **Execution labor** — writing code, editing files, creating tests, refactoring, running commands.
- **Cognitive labor** — analyzing a system, comparing alternatives, organizing information, constructing a plan.
- **Judgment labor** — deciding what is appropriate, correct, preferable, or safe under uncertainty.
- **Verification labor** — checking whether a claim is supported by evidence.
- **Coordination labor** — passing structured outputs between activities and maintaining state.
- **Governance labor** — defining who is allowed to decide or act, under what conditions, and when escalation is required.

AI can perform some amount of all of these. The practical question is not whether it can perform them, but **where delegation remains trustworthy and economically sensible**.

## 2.2 Labor, Judgment, Capability, Authority, and Accountability are different

These five concepts must not be collapsed.

**Labor** asks:

> Who performs the work?

**Judgment** asks:

> Who decides what is correct, appropriate, or preferable?

**Capability** asks:

> What can this actor technically do?

**Authority** asks:

> What is this actor permitted to decide or enact?

**Accountability** asks:

> Who is responsible for the consequences?

They can be distributed independently.

For example:

```text
Database migration

Labor          → AI prepares migration
Judgment       → AI analyzes expected impact
Capability     → tool can execute migration
Authority      → human approval required for production
Accountability → human/team
```

The fact that an agent has the capability to do something does not mean it has the authority to do it.

Likewise:

> Delegating labor does not automatically delegate ownership.

---

# 3. What is Engineering-System Ownership?

When a developer delegates more implementation labor, conventional **code-level ownership** can decrease. That does not imply that engineering ownership has to disappear.

A different form of ownership becomes possible:

> **Engineering-system ownership = ownership of the system that turns intent into accepted software.**

This includes responsibility for the composition and validity of:

```text
What / Why
Constraints
Acceptance criteria
Architecture boundaries
Delegation policy
Escalation rules
Evidence policy
Reusable engineering methods
Decision memory
Provenance
```

This does not mean the developer must write all skills and rules personally.

A mature grilling workflow can be reused from a community repository. A specification methodology can be reused from OpenSpec. A review workflow can be reused from an engineering organization. The developer can own the **selection, composition, adaptation, applicability, and consequences** of those methods without owning their authorship.

This is analogous to using PostgreSQL without claiming to have engineered PostgreSQL. The important difference is that AI skills are not deterministic software components, so their behavior still depends on the agent runtime. Therefore reusable skills must be treated as methodology dependencies, not as guaranteed execution engines.

---

# 4. The developer is not becoming a Product Owner

Engineering-system ownership is sometimes confused with becoming a Product Owner who simply describes requirements and lets AI deal with implementation.

The distinction is technical.

A Product Owner may primarily own:

```text
What
Why
Business priority
```

An Engineering-System Owner additionally owns or governs:

```text
technical constraints
architecture boundaries
acceptance evidence
verification policy
delegation boundaries
escalation conditions
engineering-method composition
technical decision memory
provenance of engineering results
```

The person can therefore know less about individual implementation details while knowing **more about the system that governs how implementation is produced and accepted**.

That does not automatically make the role superior. It changes the level at which ownership operates.

---

# 5. The canonical workflow

The default workflow used by the starter kit is:

```text
Intent
  ↓
Grilling
  ↓
Specification
  ↓
Specification Challenge
  ↓
Plan
  ↓
Implement
  ↓
Review
  ↓
Refactor
  ↓
Verify
  ↓
Accept
```

The important point is that this is **not a rigid one-way pipeline**. Discovery can send the work backward.

For example:

```text
Implementation
   ↓
problem discovered
   ↓
Is implementation wrong?
   OR
Is the specification wrong?
   ↓
Spec-change proposal when semantics must change
```

Likewise, analytics may discover new requirements after implementation has already begun:

```text
Analytics
   ↓
new understanding
   ↓
Spec proposal
   ↓
Grilling / challenge
   ↓
decision
   ↓
new implementation
```

The workflow is therefore a **controlled feedback loop**, not just a sequence of prompts.

---

# 6. Intent: What and Why remain the starting point

The human should begin with intent rather than prematurely specifying implementation.

At minimum:

```text
What are we trying to achieve?
Why does it matter?
What is explicitly not part of the problem?
```

A useful intent artifact contains:

```text
What
Why
Non-goals
Known assumptions
Open questions
Human decisions
```

The original human request and the clarified intent should not be treated as identical. The purpose of Grilling is to expose ambiguity before it gets encoded into a specification.

---

# 7. Grilling is ambiguity reduction, not polite paraphrasing

A good Grill Agent does not simply restate the developer's sentence.

It challenges it.

For a statement such as:

> "Make cancellation fast."

it might ask:

```text
What latency is considered fast?
Does the user need an immediate response or immediate completion?
What happens when the payment provider is unavailable?
What happens under concurrent cancellation?
Is cancellation allowed after shipment?
What is explicitly forbidden?
```

The output must become an **Intent Artifact**.

The important innovation is that Grilling should not necessarily happen only once.

There are at least three useful forms:

### Intent Grilling

> What do you actually mean?

### Specification Grilling

> Does this specification really represent what you mean?

### Discovery Grilling

> Did implementation, testing, or analytics reveal that we misunderstood the problem?

Therefore Grilling can recur throughout the lifecycle.

---

# 8. OpenSpec / Specification: converting intent into an engineering contract

The purpose of specification is to prevent every downstream agent from reconstructing the meaning of the request independently.

A useful specification should include, as appropriate:

```text
Goal
Non-goals
Behavior
Interfaces
Constraints
Invariants
Failure cases
Acceptance criteria
Open questions
Source intent
```

The most important property is not the format. It is **semantic explicitness and traceability**.

The specification says what the implementation is expected to realize. It should not silently mix hard requirements with mere implementation preferences.

For example:

```text
Requirement:
Cancellation must not allow an order to ship after successful cancellation.

Implementation preference:
Use PostgreSQL transaction.
```

These are not the same kind of statement.

The first belongs in the semantic contract. The second belongs in implementation planning unless it has been elevated to a project constraint.

---

# 9. Specification Validation: a specification can be perfectly coherent and still be wrong

A major missing piece in naive agent workflows is specification validation.

An implementation review asks:

> Does the code satisfy the specification?

A specification challenge asks:

> **Is the specification itself a faithful representation of the intended problem?**

The Spec Challenge Agent should look for:

```text
ambiguity
contradictory requirements
unstated assumptions
missing failure cases
incorrect acceptance criteria
hidden changes in business semantics
misalignment with the original Why
```

The output is either:

```text
PASS → eligible for human acceptance
```

or:

```text
ESCALATE → human decision required
```

This is why a second Grilling stage is not redundant. It challenges the interpretation introduced by the first stages.

---

# 10. Specification drift and the analytics problem

Specifications and code do not always have to be synchronized at every moment.

A mature workflow should distinguish semantic states:

```text
OBSERVED
PROPOSED
ACCEPTED
IMPLEMENTED
VERIFIED
CURRENT
```

### Observed

What the current system actually does.

### Proposed

What analysis or reasoning suggests the system should do.

### Accepted

What the engineering authority has decided should be true.

### Implemented

The code has been changed to attempt the accepted behavior.

### Verified

Evidence supports the implementation.

### Current

The behavior is part of the canonical accepted system state.

This matters especially after analytics.

Suppose analytics discovers:

```text
Current code does A.
Analysis says B would be better.
```

Do not simply replace the current specification with B.

First establish whether:

```text
A is an intentional but undocumented behavior
```

or:

```text
A is a bug relative to current intent
```

or:

```text
The intent itself should change from A to B.
```

These are different engineering decisions.

The third case should produce:

```text
Analysis
→ Spec-change proposal
→ Grilling/challenge
→ Human decision
→ New accepted spec
→ Implementation
→ Verification
```

Therefore **specification drift is information**. It should be visible and classified, not hidden by continually rewriting the canonical spec.

---

# 11. Planning: decomposition without redefining the problem

Once a specification is accepted, planning can be delegated.

The Plan Agent should answer:

```text
What changes are needed?
What dependencies are affected?
What can be done independently?
What verification is required?
Where might the specification need to change?
```

A critical rule is:

> **An implementation problem may generate a specification-change proposal, but the implementation agent must not silently modify the accepted specification to make the implementation easier.**

The plan must link to exactly one accepted specification version.

---

# 12. Implementation is highly delegable labor

Implementation is generally one of the easiest forms of engineering labor to delegate because the input can be bounded and the result can be tested.

But the environment must be controlled.

The minimum Git invariant is:

```text
clean working tree
      ↓
dedicated branch
      ↓
implementation
      ↓
commit
```

Do not start a new delegated task on top of another task's undocumented uncommitted work.

This is not merely Git hygiene. In an AI workforce it is **coordination and provenance infrastructure**.

---

# 13. Review output should be executable downstream

A review should not merely produce prose such as:

> "The architecture could be cleaner."

A useful review finding should be structured:

```text
Finding ID
Severity
Location
Claim
Evidence
Suggested correction
Status
```

That allows:

```text
Review Agent
   ↓
review.md
   ↓
Refactor Agent
```

The developer does not necessarily need to read every finding.

This is a key delegation principle:

> **Reading review output is itself labor. Do not assume that every intermediate artifact must be manually consumed by a human.**

The question is whether the artifact is trustworthy enough and sufficiently structured to become the input to another delegated activity.

---

# 14. Refactoring is delegated correction

The Refactor Agent consumes:

```text
accepted specification
current implementation
project rules
review findings
```

For each finding it should choose one of:

```text
FIX
ACCEPT WITH RATIONALE
ESCALATE
```

A finding must not be marked fixed without relevant verification.

If a finding reveals that the specification is wrong, the agent should **not rewrite the spec in place**. It should trigger the Spec Change workflow.

---

# 15. Verification is not the same as another LLM saying "looks good"

The engineering system should not make an AI agent the sole judge of its own correctness.

Different claims require different evidence.

For example:

```text
Type correctness
→ compiler/type checker

Behavioral requirement
→ automated behavioral tests

Architecture dependency rule
→ static/architectural check

Security property
→ security-specific checks

Performance claim
→ benchmark / experiment

Formal mathematical property
→ formal proof where justified
```

There is no universal evidence ladder where one method is always stronger than another. **Evidence strength is claim-dependent.**

A formal proof may be extremely strong for the exact property it proves and completely irrelevant to whether the property was the right business requirement.

Likewise, a test can provide excellent evidence for an observed behavior without proving every possible input.

The central rule is:

> **For important claims, prefer evidence whose failure mode is different from the agent that produced the implementation.**

---

# 16. Independent verification and correlated failure

Three agents are not automatically three independent reviewers.

For example:

```text
Coder Agent   = Model X
Review Agent  = Model X
Accept Agent  = Model X
```

They may all inherit the same mistaken interpretation.

Useful diversity can instead come from:

```text
LLM review
+
compiler/type checker
+
runtime tests
+
static analysis
+
different review model/method
```

The objective is **independent evidence**, not a larger number of LLM opinions.

---

# 17. The verifier itself must be trusted

Verification mechanisms are not magically correct merely because they are called "checks".

A test can be wrong. A static checker can be incomplete. A policy script can have a bug.

Therefore:

> **The verifier is itself part of the engineering system.**

Important verification mechanisms should be:

```text
versioned
tested
reviewable
traceable
```

This is one reason to prefer deterministic mechanisms whenever they can express the required property.

---

# 18. Where Lean, Prolog, Cursor, Codex, Claude, and reusable skills fit

These technologies are useful as examples of different layers, not as mandatory dependencies.

### Cursor / Codex / Claude Code

These systems increasingly provide mechanisms such as repository instructions, skills/rules, hooks, sandboxing, permissions, and agent workflows.

They are useful for **steering and constraining delegated labor**.

They do not make arbitrary engineering policy formally true merely because the policy is written in a rule file.

### Lean / Leanstral

Lean is an example of moving a particular class of claims from probabilistic model judgment to a formal verification kernel. This can be extremely valuable when requirements can be expressed formally and the cost is justified.

Leanstral is therefore an important example of:

```text
LLM-generated work
→ machine-checked proof
```

It is not a general replacement for ordinary application-code review.

### Prolog

Prolog can be particularly natural for executable policies and rule-based reasoning. It can serve as a policy/authorization layer or symbolic reasoning engine.

But:

> Prolog execution is not automatically formal proof of arbitrary software correctness.

For ordinary application development, Prolog is better viewed as a specialized tool for the parts of the problem that naturally fit logic programming.

### Reusable engineering skills

Mature skills from community or organizational repositories should be reused rather than reinvented unnecessarily.

But they should be treated as dependencies:

```text
source
version/revision
project binding
```

Avoid implicit `latest` dependencies for critical engineering methodology.

The human does not own the upstream skill. The human owns the decision to rely on that skill in this project.

---

# 19. Skill, Rule, Policy, and Capability

These concepts should be kept separate.

### Skill

A reusable method for performing a class of work.

Examples:

```text
g rill requirements
review code
refactor safely
write integration tests
```

### Rule

A constraint that should be obeyed.

```text
Do not cross architecture boundary X.
Do not modify public API without approval.
```

### Policy

Defines when something is allowed, forbidden, delegated, or escalated.

```text
AI may prepare a migration.
AI may not apply a destructive production migration.
```

### Capability

What an actor or tool can technically do.

```text
Can execute shell commands.
Can modify files.
Can run migration.
Can deploy.
```

The important chain is:

```text
Capability ≠ Authority
Rule ≠ Enforcement
Skill ≠ Guarantee
```

A prompt that says:

> "Never violate dependency direction"

is not equivalent to a deterministic architectural checker.

The practical rule is:

> **Move critical constraints out of LLM instructions and into machine-enforced mechanisms whenever practical.**

---

# 20. Rules have an enforcement spectrum

A rule can exist at different reliability levels:

```text
Prompt instruction
      ↓
structured rule/skill
      ↓
agent self-check
      ↓
hook / policy gate
      ↓
CI/static check
      ↓
deterministic verifier
      ↓
formal verification where appropriate
```

Do not confuse the top of this list with the bottom.

The fact that an agent can read a rule only means the rule was available to the agent.

It does not prove:

```text
rule retrieved
→ rule understood
→ rule applied
→ rule enforced
```

This distinction is fundamental to trustworthy delegation.

---

# 21. Delegation Policy and Escalation

Autonomy should be defined by both:

```text
Permission
Stopping conditions
```

For each class of work, define:

```text
Allowed actions
Forbidden actions
Required evidence
Escalation triggers
Human approval conditions
```

A conservative default risk policy is:

```text
Low risk
→ autonomous execution + normal verification

Medium risk
→ autonomous execution + stronger verification

High risk
→ agent proposal + explicit human approval

Critical / irreversible
→ human authority mandatory
```

Risk should be driven by:

```text
reversibility
blast radius
external impact
data loss
security consequences
business consequences
```

Not simply by number of changed lines.

---

# 22. Escalation is a first-class engineering skill

An agent should not merely know what to do. It should know **when not to continue**.

Typical escalation triggers:

```text
ambiguity in What/Why
change to acceptance criteria
change to business semantics
change to domain invariant
architecture boundary change
security policy change
destructive data operation
public API change outside approved spec
insufficient evidence
conflicting evidence
repeated non-converging fixes
```

Stopping is not failure.

> **A controlled escalation is often a successful execution of delegation policy.**

---

# 23. Human Attention Allocation

The objective is not simply to remove humans from every loop.

Human attention is itself a scarce engineering resource.

The goal is to spend it where it has high marginal value.

Examples of good delegation candidates:

```text
boilerplate
mechanical refactoring
routine test generation
structured review findings
repository-wide repetitive edits
```

Examples that often deserve human attention:

```text
changing business semantics
changing security assumptions
changing architecture boundaries
changing acceptance criteria
accepting conflicting evidence
changing delegation policy
```

Therefore:

> **Optimize the allocation of human attention, not merely the reduction of human labor.**

---

# 24. Acceptance is not identical to reading code

This is central to the model.

A human can potentially accept a change without reading every line if the workflow provides a sufficiently trustworthy evidence package for the risk involved.

That package may contain:

```text
accepted spec
verification status
review findings
risk classification
commit SHA
relevant benchmark results
unresolved issues
```

The Accept Agent can produce:

```text
AUTO_ACCEPT_ELIGIBLE
HUMAN_APPROVAL_REQUIRED
REJECT
```

But the Accept Agent is not automatically the final authority.

The delegation policy determines whether the human must approve.

The deeper principle is:

> **Acceptance can be delegated as labor; ultimate authority need not be.**

---

# 25. Acceptance Debt

Aggressive delegation creates a new kind of debt.

Suppose:

```text
500 autonomous changes
20 strong verification packages
```

The system has produced a lot of labor but relatively little evidence.

That accumulated gap is **Acceptance Debt**:

> engineering output for which the available evidence is insufficient relative to the confidence required to accept it.

Acceptance debt should become visible rather than silently accumulating.

This is different from technical debt:

```text
Technical debt
→ implementation quality problem

Acceptance debt
→ confidence / evidence problem
```

---

# 26. Context Management

A correct rule is useless if the relevant agent never receives it.

Therefore the workflow needs disciplined context assembly.

A useful order is:

```text
repository instructions
→ delegation policy
→ task intent
→ accepted spec
→ relevant decisions
→ relevant skills
→ active plan
→ relevant code
```

Do not solve this by putting everything into one enormous prompt.

The question is:

> **What context is necessary for this specific decision, and where did that context come from?**

Context assembly is itself engineering coordination labor.

---

# 27. Decision Memory

Specifications and decision records serve different purposes.

Specification:

> What should the system do?

Decision record:

> Why did we choose this solution or constraint?

For example:

```text
ADR:
Use asynchronous cancellation because payment-provider latency
must not block the user-facing request.
```

Without that history, a future agent may "improve" the architecture by reintroducing synchronous calls.

Important decisions should therefore be kept as durable engineering memory, normally version-controlled alongside the repository.

---

# 28. Conflict Resolution

Multiple agents can disagree.

For example:

```text
Performance Agent → add cache
Security Agent    → do not cache this data
Architecture Agent→ no new infrastructure
Coding Agent      → Redis simplifies implementation
```

Do not resolve this by model majority by default.

A project should define precedence for its constraints.

A conservative template might be:

```text
explicit human requirement
    > domain invariant
    > security/safety constraint
    > accepted specification
    > correctness
    > reliability
    > performance
    > maintainability/style preference
```

The project must customize this order.

When policy cannot resolve the conflict, escalate.

---

# 29. Provenance: store engineering state, not every token

Provenance does **not** mean storing everything an agent did.

Normally, the durable engineering state should include:

```text
Intent / Spec
Rule / Policy versions
Skill references
Code commit
Verification result
Acceptance decision
```

Every material experiment or benchmark should identify the **exact code commit** that produced the result.

For example:

```json
{
  "result_id": "exp-042",
  "commit": "8f31c42",
  "spec": "spec-17",
  "verification": "verify-88",
  "result": {"p95_ms": 83}
}
```

Raw prompt tokens, complete context dumps, every tool call, and retry logs normally do not belong in Git. They may be retained separately if a project has a specific audit, debugging, security, or operational need.

The correct objective is:

> **Enough provenance to reconstruct which engineering state produced a result.**

---

# 30. Repository state is coordination infrastructure

With multiple agents, Git becomes part of the delegation protocol.

Recommended invariants:

```text
1. Start independent work from a clean working tree.
2. Use a dedicated branch for each independent plan/workstream.
3. Do not work on another task's undocumented uncommitted changes.
4. Commit meaningful engineering states.
5. Record result → exact commit.
6. Preserve spec → change → review → verification → acceptance lineage.
```

The objective is not a beautiful Git history for its own sake.

The objective is **isolation, reproducibility, and coordination of delegated labor**.

---

# 31. Engineering lineage

A useful mental model is:

```text
Intent I17
   ↓
Spec S24
   ↓
Policy/Skill Set K8
   ↓
Plan P12
   ↓
Commit C42
   ↓
Review R91
   ↓
Refactor C47
   ↓
Verification V71
   ↓
Result E19
   ↓
Acceptance A8
```

This is not a requirement to build a graph database in v1.

It is a requirement to maintain enough stable identifiers and references that this lineage can be reconstructed.

---

# 32. Engineering-System Evolution

A mature workflow should learn from repeated failures.

Suppose a review finds the same class of problem twenty times.

Do not simply tell the agent twenty times to be more careful.

Ask:

```text
Why does this keep happening?
```

Possible system-level responses:

```text
new rule
improved skill
new test
static checker
a better spec template
new context retrieval rule
new delegation boundary
```

The hierarchy of fixes should generally prefer stronger mechanisms:

```text
better prompt
→ structured procedure
→ deterministic check
→ architectural/tooling constraint
```

This leads to a fundamental property of the engineering system:

> **Failures in delegated labor become inputs into improvements of the system that delegates the labor.**

That is the difference between an AI workflow and an engineering system.

---

# 33. External methods and meta-engineering

The human does not need to reinvent the engineering methodology every time.

A mature ecosystem can produce reusable methods:

```text
community
  → grilling skill
  → review skill
  → OpenSpec workflow
  → testing methodology

project
  → selects and composes them

AI workforce
  → executes them
```

This creates another level of division of labor:

> **Engineering knowledge production itself can be divided and reused.**

This is why the starter kit uses a skill manifest rather than requiring every external skill to be copied into the repository.

However, critical methodology dependencies should be pinned to a known revision rather than following a moving `latest` source.

---

# 34. What the starter kit deliberately does not assume

The framework does not assume that:

- one model is sufficient for every task;
- multiple agents automatically create independent verification;
- a long rule file is formal governance;
- AI can safely redefine requirements;
- humans can stop reading code for every category of change;
- formal verification can replace ordinary testing;
- Prolog or Lean is required for normal software development;
- all agent execution traces should be persisted;
- every engineering method must be authored by the project team.

The goal is not maximal autonomy for its own sake.

---

# 35. The practical strategy for a developer

Start conservatively.

Use this sequence:

```text
1. Express intent.
2. Grill it.
3. Produce a specification.
4. Challenge the specification.
5. Resolve required human decisions.
6. Create a clean branch.
7. Plan from the accepted spec.
8. Delegate implementation.
9. Review structurally.
10. Delegate routine corrections.
11. Run deterministic verification.
12. Escalate high-risk or ambiguous issues.
13. Record the result against the exact commit.
14. Accept according to evidence and policy.
```

Then observe repeated failures and improve the engineering system.

Do not begin with a giant autonomous swarm.

Begin by making **boundaries, artifacts, state transitions, evidence, and provenance explicit**. Increase autonomy as the verification and coordination system earns trust.

---

# 36. The core operating principle

The objective is not:

> "Let the AI do everything."

It is:

> **Make every important kind of engineering labor explicit, assign it to the most suitable actor, preserve human authority over intent and consequential decisions, and retain enough evidence and provenance to know what was done and why it should be trusted.**

The most useful practical rule is:

> **Delegate labor aggressively where the work is bounded, reversible, and verifiable; preserve human judgment and authority where intent, trade-offs, risk, or irreversible consequences dominate; and move critical constraints from probabilistic instructions into deterministic enforcement whenever practical.**

---

# 37. Companion starter kit

The companion build specification is [`ai-agent-starter-kit-spec.md`](./ai-agent-starter-kit-spec.md).

It implements the concepts above as:

```text
Artifacts
Agents
Policies
Gates
Git guardrails
Verification scripts
Result provenance
Skill manifests
Specification lifecycle
```

The canonical pre-built flow is:

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

The article's concepts map directly to those components in the starter-kit contract.
