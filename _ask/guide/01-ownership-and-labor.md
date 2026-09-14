# Ownership and Division of Labor

# Engineering with AI Agents: Delegation of Engineering Labor Without Losing Engineering Ownership

> A practical, detailed guide for developers who want to use AI agents as a delegated engineering workforce rather than as an opaque code generator.
>
> Companion implementation contract: [`ai-agent-starter-kit-spec.md`](./ai-agent-starter-kit-spec.md)
>
> This guide and the starter kit are a matched pair. The article explains the concepts, boundaries, and reasoning model. The starter kit turns those concepts into repository artifacts, pre-built agent roles, workflow gates, and Git/provenance conventions.

---

## 1. The problem this guide solves

AI makes it possible to delegate much more software-engineering labor than before. Asking an agent to write code is the obvious use. The wider move is:

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
  → foggy idea / R&D need / clear intent

00 Explore (when the destination is not yet clear)
  → shared decision map, research, prototypes
  → destination clear enough to own What/Why

Human
  → intent / What / Why

01 Grill Agent
  → ambiguity reduction

02 Spec Agent
  → specification

03 Spec Challenge Agent
  → challenge the specification

05 Plan Agent
  → implementation plan

06 Implement Agent
  → coding labor

07 Review Agent
  → review labor

08 Refactor Agent
  → correction labor

09 Verify Agent + deterministic tooling
  → evidence

10 Accept Agent / Human
  → acceptance under policy
```

(`04 Spec Change` interrupts when semantics must change.)

That split is **Division of Engineering Labor**. "AI-assisted coding" is only one slice of it.

**Explore is first-class.** When the way from here to the destination is still foggy (greenfield product shape, large feature map, unresolved R&D), do not pretend Grill→Spec can invent the destination. Chart decisions (wayfinder-shaped), research facts, and cheap prototypes until the destination is clear; then enter the Engineering Pipeline (`01`–`10`). Explore produces **decisions and clarity**, not accepted product software by itself.

The question shifts from:

> Should I let AI code?

to:

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

AI can perform some amount of all of these. The practical question is **where delegation remains trustworthy and economically sensible**.

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

Capability to do something is not authority to do it.

> Delegating labor does not automatically delegate ownership.

---

# 3. What is Engineering-System Ownership?

When a developer delegates more implementation labor, conventional **code-level ownership** can decrease. Engineering ownership does not have to disappear with it.

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

The developer does not have to write all skills and rules personally.

A mature grilling workflow can be reused from a community repository. A specification methodology can be reused from OpenSpec. A review workflow can be reused from an engineering organization. The developer can own the **selection, composition, adaptation, applicability, and consequences** of those methods without owning their authorship.

This is like using PostgreSQL without claiming to have engineered PostgreSQL. The difference is that AI skills are not deterministic software components, so their behavior still depends on the agent runtime. Reusable skills are methodology dependencies, not guaranteed execution engines.

---

# 4. The developer is not becoming a Product Owner

Engineering-system ownership is sometimes confused with becoming a Product Owner who describes requirements and lets AI deal with implementation.

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

That changes the level at which ownership operates. It does not make the role automatically superior.

---
