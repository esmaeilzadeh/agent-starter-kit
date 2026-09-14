# Evolution and the Starter Kit

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

This is why the starter kit uses a Skill Manifest rather than requiring every Community Skill to be copied into the repository. Agents prepare pinned skills by instruction (open skills ecosystem / [skills.sh](https://www.skills.sh/) as a discovery starting point).

Critical methodology dependencies should be pinned to a known revision rather than following a moving `latest` source.

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
Agents (00 Explore + 01–10 Engineering Pipeline)
Policies
Gates
Git conventions
Skill Manifest + Skill Preparation (pinned Community Skills; skills.sh as discovery index)
Verification hooks
Provenance records
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
