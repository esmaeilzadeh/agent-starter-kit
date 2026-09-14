# Explore and Engineering Pipeline Workflow

# 5. The canonical workflow

The starter kit has two joined stages:

1. **Explore Phase (`00`)** — optional when the destination is already clear; mandatory when R&D or wayfinding is required.
2. **Engineering Pipeline (`01`–`10`)** — Grill through Accept once What/Why can be owned.

```text
[optional / when foggy]
Explore (00)
  → map decisions
  → research facts
  → prototype when paper is not enough
  → destination clear
        ↓
Intent
  ↓
Grilling (01)
  ↓
Specification (02)
  ↓
Specification Challenge (03)
  ↓
Plan (05)
  ↓
Implement (06)
  ↓
Review (07)
  ↓
Refactor (08)
  ↓
Verify (09)
  ↓
Accept (10)
```

Explore binds community methods (for example wayfinder, research, prototype, grilling) via a versioned skill manifest and agent-driven skill preparation. Each product repo does not have to reinvent those methods. Discovery indexes such as [skills.sh](https://www.skills.sh/) are a starting point for finding pins; the project owns the pin and the preparation instruction.

Skip Explore only when the human already has a destination sharp enough for Intent → Grill. Do not stuff R&D into Implement.

Discovery can send the work backward. The Engineering Pipeline is a **controlled feedback loop**.

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

Analytics may discover new requirements after implementation has already begun:

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

**Guidance, not a lock.** On the Engineering Pipeline, every next stage still needs the previous **artifact** — skipping documents is meaningless. What you may skip is extra *approvals*: after one explicit “these defaults are OK,” later artifacts are prepared without a per-file bless. **Accept** is the second confirm. **00** may be omitted when the destination is already clear (real skip; no explore-map). `/off-path` (or “just code”) is **this session only** — warn once and follow; a new chat starts on-path. Policy: `_ask/policies/workflow.md`.

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

The original human request and the clarified intent should not be treated as identical. Grilling exists to expose ambiguity before it gets encoded into a specification.

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

### Grilling Expansion (before resolution)

A grilling round is not ready to close on “all recommended” / “all ok” until each **load-bearing** numbered question has been **expanded**: alternatives, tradeoffs, and failure modes are visible—not only a one-line A/B/C. Obvious defaults go in an “I’ll assume…” list; “defaults OK” covers that list. If the human asks to expand (or stakes are high), re-issue that question expanded before accepting an answer. Never auto-approve a real decision. Before the first numbered question, propose related extra Community Skills that would change What/Why, **ask before preparing them**, and pin accepted skills in the repo manifest. This rule is part of the starter kit’s `01 Grill` contract (and Explore decision grilling). See ADR 0016.

Grilling need not happen only once.

There are at least three useful forms:

### Intent Grilling

> What do you actually mean?

### Specification Grilling

> Does this specification really represent what you mean?

### Discovery Grilling

> Did implementation, testing, or analytics reveal that we misunderstood the problem?

Grilling can recur throughout the lifecycle.

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

The format matters less than **semantic explicitness and traceability**.

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

Naive agent workflows often skip specification validation.

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

A second Grilling stage is not redundant. It challenges the interpretation introduced by the first stages.

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

**Specification drift is information**. It should be visible and classified, not hidden by continually rewriting the canonical spec.

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

The environment must be controlled.

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

In an AI workforce this is **coordination and provenance infrastructure**.

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

A test can provide excellent evidence for an observed behavior without proving every possible input.

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
