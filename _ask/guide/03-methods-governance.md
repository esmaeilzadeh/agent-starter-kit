# Methods, Skills, Rules, and Governance

# 18. Where Lean, Prolog, Cursor, Codex, Claude, and reusable skills fit

These technologies are useful as examples of different layers, not as mandatory dependencies.

### Cursor / Codex / Claude Code

These systems increasingly provide mechanisms such as repository instructions, skills/rules, hooks, sandboxing, permissions, and agent workflows.

They are useful for **steering and constraining delegated labor**.

They do not make arbitrary engineering policy formally true merely because the policy is written in a rule file.

### Lean / Leanstral

Lean is an example of moving a particular class of claims from probabilistic model judgment to a formal verification kernel. This can be extremely valuable when requirements can be expressed formally and the cost is justified.

Leanstral is an example of:

```text
LLM-generated work
→ machine-checked proof
```

It is not a general replacement for ordinary application-code review.

### Prolog

Prolog can be particularly natural for executable policies and rule-based reasoning. It can serve as a policy/authorization layer or symbolic reasoning engine.

> Prolog execution is not automatically formal proof of arbitrary software correctness.

For ordinary application development, Prolog is better viewed as a specialized tool for the parts of the problem that naturally fit logic programming.

### Reusable engineering skills

Mature skills from community or organizational repositories should be reused rather than reinvented unnecessarily.

Treat them as dependencies:

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
grill requirements
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

The chain is:

```text
Capability ≠ Authority
Rule ≠ Enforcement
Skill ≠ Guarantee
```

A prompt that says:

> "Never violate dependency direction"

is not equivalent to a deterministic architectural checker.

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

Spend it where it has high marginal value.

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

The Accept Agent is not automatically the final authority.

The delegation policy determines whether the human must approve.

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

The workflow needs disciplined context assembly.

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

The objective is **isolation, reproducibility, and coordination of delegated labor**.

---
