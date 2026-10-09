# Handoff: Structured, Interactive Agentic Development Environment

## Status

Exploratory architecture / product-direction note.

This is not yet an implementation specification. It captures the direction reached so far and provides a basis for further design in `agent-starter-kit`.

The key conclusion is that the problem is larger than specification review.

We are reconsidering the developer experience for software development in which AI agents perform a large portion of specification, planning, implementation, testing, review, and verification.

---

# 1. The problem

Current agentic-development workflows risk producing an undesirable inversion of human and machine work.

The agent performs much of the generative work:

- explores the repository;
- writes specifications;
- proposes architecture;
- creates plans;
- implements code;
- writes tests;
- reviews changes;
- generates verification reports.

The developer is then left with passive consumption:

- read a long spec;
- read a plan;
- inspect a large diff;
- read a review;
- inspect test output;
- compare generated documents.

This can increase throughput while making the developer's work less engaging and less cognitively valuable.

The developer becomes the proofreader of AI output.

That should not be the target developer experience.

The central question is:

> **If AI performs most of the construction work, what should the developer actually be doing?**

Working answer:

> **The developer should direct, challenge, inspect, and steer software construction rather than passively consume artifacts produced by agents.**

---

# 2. Target human role: technical director

The developer increasingly behaves like the technical director of a team of agents.

They should immediately be able to see:

- what is being built;
- why;
- what is complete;
- what remains;
- what is blocked;
- what is currently being implemented;
- which behaviors have tests;
- whether those tests passed;
- what evidence supports completion;
- which assumptions remain uncertain;
- which decisions require human judgment;
- which agents are working on which areas.

The developer should not reconstruct this state by reading five generated Markdown files.

The desired loop is:

**Observe → Challenge → Decide → Delegate → Inspect consequences**

rather than:

**Prompt → Wait → Read document → Approve → Read another document**

---

# 3. One engineering model, two consumers

A key clarification is that the structured model is **not only an agent-oriented specification format**.

It intentionally serves two very different consumers.

## Machine-native use

The model gives agents an explicit semantic structure.

The agent can determine:

- what requirements exist;
- which scenarios belong to them;
- which implementation satisfies each scenario;
- which tests claim to verify it;
- whether those tests were actually executed;
- what passed or failed;
- what evidence is missing;
- what became stale after a change.

This enables substantially stronger hardening than reconstructing engineering meaning from prose.

## Human-native use

The developer should normally not inspect the raw representation.

The same model is rendered through an interactive UI that lets the developer inspect the project at an appropriate level of abstraction.

For example:

**Feature**

→ **Story**

→ **Scenario**

→ **Implementation**

→ **Tests**

→ **Evidence**

The raw representation can therefore optimize for semantic precision and machine reliability without forcing humans to consume a machine-oriented format.

This is an intentional asymmetry:

> **Machine-native underneath, human-native on top.**

The UI is not a second source of truth. It is an interaction surface over the same engineering model.

---

# 4. Engineering knowledge becomes structured data

Today, important engineering knowledge is distributed across largely textual artifacts:

- intent;
- spec;
- spec challenge;
- spec change;
- plan;
- implementation;
- code review;
- verification;
- acceptance;
- tests.

Relationships between them are mostly implicit.

Instead, these concepts should become structured, addressable engineering objects.

Potential node types include:

- Intent
- Requirement
- Feature
- Story
- Scenario
- Behavior
- Constraint
- DesignDecision
- Assumption
- Task
- Implementation
- Test
- TestRun
- ReviewFinding
- Evidence
- Risk

Each object has a stable identity.

Example:

`FEATURE-12`

→ `STORY-12.3`

→ `SCENARIO-12.3.2`

→ `TEST-81`

→ `TEST-RUN-492`

Relationships are explicit:

- `derived_from`
- `contains`
- `depends_on`
- `implements`
- `verified_by`
- `challenged_by`
- `affected_by`
- `conflicts_with`
- `supersedes`
- `blocked_by`
- `produced_by`

Together these form the **Engineering Model / Engineering Graph**.

---

# 5. The structured model should be canonical

The direction should not be:

**Markdown spec → parse → structured representation**

Instead:

**Canonical Engineering Model → multiple projections**

including:

- Markdown specification;
- scenario view;
- design view;
- review view;
- Control Room;
- agent context;
- progress view;
- acceptance report.

Markdown remains useful.

It simply stops being the fundamental semantic representation.

A useful analogy is:

> **Markdown is a rendering of the Spec AST, not the AST itself.**

This is a substantial evolution from the current decision-review proposal, which intentionally keeps the pilot in Markdown and does not require a JSON schema or UI.

---

# 6. Protect the semantic structure

The structured model has meaning beyond its individual fields.

Therefore arbitrary editing must not be allowed to silently corrupt it.

For example:

`SCENARIO-17`

may reference:

`REQ-4`

and:

`TEST-81`

The system must prevent states such as:

- references to nonexistent IDs;
- duplicate IDs;
- illegal relation types;
- invalid cardinality;
- forbidden cycles;
- structurally invalid nodes;
- inconsistent ownership;
- impossible lifecycle transitions.

This is the equivalent of referential integrity for the Engineering Model.

The important architectural principle is:

> **The persistence format is not the contract. The valid Engineering Model is the contract.**

---

# 7. Engineering Model interface

Agents should ultimately interact with the Engineering Model through a controlled semantic interface rather than treating its persistence files as arbitrary text.

Conceptual operations might include:

`createScenario`

`linkScenarioToRequirement`

`attachTest`

`recordTestRun`

`resolveDecision`

`attachEvidence`

`changeRequirement`

`markStale`

The important part is not the final API shape.

The important part is that operations express **engineering semantics**.

The interface can therefore enforce invariants before accepting mutations.

Humans should normally interact through the UI rather than editing the raw model.

This has another important consequence:

> Agents do not need to know how the model is physically persisted.

The persistence mechanism can evolve without redesigning agent workflows.

---

# 8. Engineering Graph Compiler / Validator

A validation layer should be able to load the complete model and prove that its structural invariants hold.

Conceptually:

**Engineering Model Source**

→ **Parse**

→ **Schema validation**

→ **Relationship validation**

→ **Semantic invariants**

→ **Valid Engineering Graph**

A broken reference should behave more like a compile error than a warning hidden in prose.

For example:

`SCENARIO-17 verified_by TEST-999`

when `TEST-999` does not exist should make the model invalid.

Validation should be independently executable in CI so that bypassing the normal mutation interface cannot silently introduce an invalid model.

A useful principle is:

> **Git provides revision integrity; the Engineering Graph Compiler provides semantic and relational integrity.**

---

# 9. Persistence and Git

Durable engineering definition should remain associated with the code revision it describes.

Git provides valuable semantics almost for free:

- history;
- branches;
- merge;
- pull requests;
- diff;
- rollback;
- revision identity;
- reproducibility.

Checking out an older software revision should make it possible to recover the engineering definition corresponding to that revision.

The exact persistence representation remains an implementation decision.

Candidates include:

- JSON;
- YAML;
- a purpose-built textual DSL;
- another deterministic representation.

The semantic model should not depend heavily on that choice.

---

# 10. Do not confuse Single Source of Truth with one physical storage system

Not every engineering fact belongs inside the specification model.

Different facts already have natural authorities.

For example:

**Engineering Model**

owns what should exist and the semantic relationships between requirements, scenarios, decisions, and expected verification.

**Git/code**

owns what implementation actually exists at a revision.

**Test framework / CI**

owns what tests actually executed and their results.

**Git history**

owns implementation history.

Therefore the more precise principle is:

> **Single Authority per Fact**

rather than forcing every engineering fact into one giant database or file.

The Engineering Graph connects authoritative facts while retaining provenance.

---

# 11. Three categories of state

The system should distinguish at least three kinds of state.

## Definition state

Examples:

- requirements;
- stories;
- scenarios;
- constraints;
- design decisions;
- accepted assumptions;
- semantic relationships.

Durable and revision-aware.

## Evidence state

Examples:

- implementation references;
- code symbols;
- commits;
- tests;
- assertions;
- test runs;
- review findings;
- verification results.

Evidence must retain provenance and revision information.

## Runtime state

Examples:

- active agents;
- current assignments;
- queued jobs;
- running tests;
- execution logs;
- temporary locks;
- heartbeats.

Runtime state is ephemeral and should not be confused with durable engineering definition.

---

# 12. Database as projection, not necessarily authority

A database can later provide a fast projection of the Engineering Graph for the interactive environment.

Queries may include:

- Which scenarios have no tests?
- Which requirements lack implementation evidence?
- Which work is blocked?
- Which design decisions remain unresolved?
- What became stale after this change?
- Which agents are currently active?
- What needs human attention?

Conceptually:

**Canonical/revisioned Engineering Model**

→ **Compiler / Indexer**

→ **Queryable projection**

→ **Developer UI**

The database can be rebuilt.

This avoids making operational storage the only place where engineering intent exists.

---

# 13. Traceability must be evidence-backed

A relationship such as:

`REQ-17 implemented_by user-service.ts`

is not sufficient by itself.

Implementation evidence should ideally identify:

- revision;
- file;
- symbol;
- relevant range or diff;
- why this implementation satisfies the requirement.

Similarly:

`SCENARIO-17.2 verified_by TEST-42`

does not prove verification.

The system should eventually identify:

- the scenario;
- relevant test;
- assertion responsible for verifying it;
- latest execution result;
- code revision against which it ran.

The system should distinguish:

**the test executed the code path**

from:

**the test asserted the required behavior.**

This distinction is fundamental to stronger agentic hardening.

---

# 14. Progress should be derived from evidence

Agents should not report arbitrary progress such as:

> "This requirement is 80% done."

Instead, state should derive from graph relationships and evidence.

A scenario could progress through something resembling:

**Specified**

→ **Designed**

→ **Implemented**

→ **Tested**

→ **Verified**

→ **Accepted**

The UI might show:

> Scenario 17.2  
> Implementation: present  
> Unit verification: present  
> Integration verification: missing  
> Human decision: resolved  
> Latest relevant test: passed at revision X

Progress becomes inspectable rather than self-reported.

---

# 15. The UI should be work-centric, not agent-centric

The environment should not become merely an agent dashboard.

Agents are workers.

Engineering work is persistent.

If Agent A stops and Agent B continues, the developer's mental model should remain stable.

The primary navigation should therefore revolve around:

- features;
- stories;
- scenarios;
- decisions;
- implementation;
- tests;
- evidence;
- dependencies.

Agent activity is projected onto these objects.

For example:

> Scenario 17.2  
> Status: Implementing  
> Worker: Agent 3  
> Blocking decision: None  
> Implementation evidence: Pending  
> Tests: 2 planned

---

# 16. Developer Control Room

The Engineering Model enables a different kind of development environment.

At a high level, the developer sees the workstream.

They progressively drill into:

**Feature**

→ **Story**

→ **Scenario**

→ **Design / implementation**

→ **Tests**

→ **Evidence**

The developer should be able to answer immediately:

- What is done?
- What remains?
- Why is this blocked?
- Which test covers this scenario?
- What exactly does that test assert?
- Did it pass?
- What code implements this?
- Why was this design selected?
- What is currently being changed?
- What becomes affected if this requirement changes?

A developer can select a scenario and inspect its test directly without first navigating through generated reports.

---

# 17. Attention Queue

The developer should not continuously babysit agents.

The system should identify places where human judgment has unusually high leverage.

These become the **Attention Queue**.

Examples:

- unresolved product intent;
- consequential design choice;
- conflicting requirements;
- unsupported assumption;
- surprising verification result;
- high-impact requirement change;
- ownership/security decision;
- disagreement between independent agents;
- insufficient acceptance evidence.

Routine work can continue without interruption when authority permits.

The developer becomes a high-leverage supervisor rather than a continuous reviewer.

---

# 18. Active human interaction

When human attention is required, do not default to:

> Read these three pages and approve.

Use interaction appropriate to the engineering problem.

Examples include:

### Predict → Reveal

Developer predicts behavior before seeing the current specification or implementation behavior.

### Break My Design

Developer attempts to break the proposed architecture under failure, load, or future change.

### Counterexample Hunt

Developer invents scenarios that violate the current behavioral model.

### Diagnose Before Reveal

Developer investigates a failure before seeing the agent's explanation.

### Choose the Trade-off

Developer chooses between genuine design alternatives or proposes another.

### Challenge the Assumption

Developer identifies which underlying assumption should be tested or rejected.

These are not mandatory games.

They preserve meaningful engineering cognition.

---

# 19. Gamification is a design principle, not the product

Avoid superficial mechanics such as:

- points;
- XP;
- badges;
- arbitrary streaks;
- leaderboards.

Engineering already contains strong intrinsic interaction loops:

**prediction → consequence**

**hypothesis → experiment**

**attack → defense**

**decision → trade-off**

**challenge → evidence**

**uncertainty → discovery**

**problem → resolution**

The environment should expose these loops rather than decorating document review with game mechanics.

---

# 20. Multi-agent orchestration

Once engineering work is structured, multiple agents can operate against different parts of the graph.

For example:

- Agent A implements Scenario 12.1;
- Agent B attacks Design Decision 8;
- Agent C verifies Scenario 9.4;
- Agent D researches an unresolved assumption.

The developer sees work and dependencies rather than disconnected agent conversations.

They can redirect work:

> Pause implementation until this design uncertainty is resolved.

> Assign another agent to attack this architecture.

> Continue unaffected scenarios while this one is blocked.

This creates a genuine technical-director experience.

---

# 21. Documents remain useful

This direction does not eliminate documents.

Developers may still want:

- complete specifications;
- architecture documents;
- review summaries;
- implementation reports;
- acceptance reports.

These become **generated projections over the Engineering Model**.

For example:

`Engineering Model → render → spec.md`

Documents become convenient views rather than competing semantic authorities.

---

# 22. Relationship to the existing decision-review proposal

The existing proposal contains several concepts worth preserving:

- focus developer attention on consequential decisions;
- separate behavioral and design review;
- predict/reveal interaction;
- preserve evidence;
- distinguish human decisions from agent defaults;
- surface stale decisions;
- avoid treating completion of cards as proof of correctness.

Its current architecture, however, remains document-oriented: the agent maintains a Markdown review record and coverage map.

The new direction generalizes this into:

**Structured Engineering Model → multiple agent and human projections**

Decision Cards can still exist.

They simply become one interaction generated from the model rather than another canonical document.

---

# 23. Complexity discipline

This direction can easily turn into building an entire development platform before proving the core idea.

Avoid that.

The conceptual architecture can remain ambitious while implementation proceeds incrementally.

A useful progression is:

**Phase 1 — Structured model + validation**

Prove that meaningful engineering artifacts can be represented structurally and validated.

**Phase 2 — Traceability**

Connect scenarios to implementation, tests, and evidence.

**Phase 3 — Human projection**

Build a small UI that makes individual scenarios and their evidence easy to inspect.

**Phase 4 — Attention and interaction**

Introduce human-attention detection and interactive challenges.

**Phase 5 — Multi-agent Control Room**

Only after the substrate proves useful, build richer orchestration and runtime views.

Do not introduce a database, graph database, service architecture, or elaborate runtime merely because the eventual product might use one.

Each addition must solve an observed problem.

---

# 24. Suggested first experiment

Choose one bounded existing workstream.

Transform only enough of it to represent:

**Feature → Story/Scenario → Test → Evidence**

Then test whether the system can reliably answer:

- Show every scenario.
- Which scenarios have no tests?
- Show the tests for Scenario X.
- What exactly does each test claim to verify?
- What was its latest result?
- Where is Scenario X implemented?
- Which scenarios changed after their latest verification?
- What currently requires human judgment?

Then expose this through a minimal human-readable projection.

The experiment succeeds only if it benefits both sides:

### Agent benefit

The agent can perform stronger, more deterministic hardening and traceability.

### Developer benefit

The developer can understand and supervise work faster and more meaningfully than by reading generated artifacts sequentially.

If only the first benefit appears, we have built machine metadata rather than a new developer experience.

If only the second appears, we have built a dashboard without improving engineering reliability.

The value comes from serving both from the **same semantic model**.

---

# 25. Open questions

Do not prematurely lock:

- exact schema;
- JSON vs YAML vs DSL;
- Feature/Story/Scenario granularity;
- ID semantics;
- relation types;
- mutation interface;
- validator/compiler design;
- how Spec Challenge maps into the model;
- how plans map into the model;
- code-symbol references;
- test-to-scenario mapping;
- assertion-level verification;
- stale-edge detection;
- merge semantics;
- database/index architecture;
- UI information architecture;
- multi-agent ownership;
- authorization boundaries.

These should be resolved experimentally.

---

# 26. Product thesis

Traditional IDEs are primarily organized around:

**files → symbols → code → debugger**

An agentic development environment may instead need to be organized around:

**intent → behavior → decisions → work → implementation → evidence**

Code remains essential.

It is simply no longer necessarily the primary navigation abstraction for the human.

The developer operates where human judgment has the highest leverage and drills into implementation when needed.

The core thesis is:

> **Redesign the developer experience for a world where developers direct software construction rather than perform every construction task themselves.**

The Engineering Model provides the semantic substrate.

Its strict structure enables stronger machine reasoning and hardening.

The UI turns that same model into a comprehensible human workspace.

Evidence keeps agent claims accountable.

Interactive challenges preserve meaningful human engineering involvement.

Agents perform much of the construction.

The developer becomes the technical director of that construction.
