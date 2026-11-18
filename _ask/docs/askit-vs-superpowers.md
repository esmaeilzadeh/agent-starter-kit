# AskIt and Superpowers: a developer comparison

Both frameworks ask agents to understand the request before coding, work from
a plan, test behavior, review changes, and verify claims. They differ most in
how they record authority, handle unresolved decisions during execution, and
prove completion.

This comparison reads the local `../superpowers` checkout, which matches the
requested neighboring framework (`../superpower` was not present). It does
not install or execute Superpowers. Its skill files are comparison sources,
not instructions for carrying out this documentation task.

## Versions and evidence

- **AskIt:** source checkout at
  `ce69399ee3c9b277329a8ba79fc27cd3ac61786f`, before this documentation addition.
- **Superpowers:** `22f0b463e7a5e579904dd6211a520321035526f7`, clean checkout
  when inspected. Source links below point to that exact GitHub revision of
  `obra/superpowers` for portability.
- **Scope:** checked-in contracts, skills, scripts, and documentation. This
  is a design/implementation comparison, not a live runtime evaluation or a
  benchmark of cost, speed, compliance, or defect rate.

Start with the [AskIt developer guide](developer-guide.md) if you want the
step-by-step AskIt walkthrough.

## 1. What each framework gives you

**AskIt** organizes a repository around named workstreams: approved intent,
specification, challenged requirements, a task graph, reviewed test obligations,
committed candidates, independent review, verification, and acceptance. Its
scripts check important relationships between these records. Policy and human
judgment still matter; cooperative attribution is not authentication.

**Superpowers** organizes agent behavior through composable skills and a
bootstrap that tells the agent when to invoke them. The inspected version also
has implementation support scripts, isolated-workspace guidance, per-plan
progress ledgers, review packages, and recovery instructions. It offers both
subagent-driven implementation and inline execution with a final review.
It is not limited to a set of prompts with no persistent state.

Sources: [AskIt workflow](../policies/workflow.md),
[AskIt completion contract](spec-test-traceability.md),
[Superpowers bootstrap](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/using-superpowers/SKILL.md),
[Superpowers subagent execution](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development/SKILL.md).

## 2. Map the workflows

These are closest counterparts, not interchangeable commands or identical gates.

| AskIt stage | Closest Superpowers capability | Practical difference |
| --- | --- | --- |
| **00 Explore** | `brainstorming`, including research and approved spikes | AskIt makes discovery an optional named stage with a durable Explore map and required handoff. Superpowers includes discovery in brainstorming and permits an explicitly agreed throwaway spike. |
| **01 Grill** | `brainstorming` | AskIt uses expanded selectable decisions, explicit assumptions, and complete-intent approval tied to a digest. Superpowers begins with open questions when Why is unknown, asks one at a time, then presents approaches/design for approval. |
| **02 Spec** | Brainstorming's short/full design document | AskIt separates intent from spec and creates stable JSON criterion IDs alongside prose. Superpowers sizes the design document to the change and commits it under `docs/superpowers/specs/` by default. |
| **03 Spec Challenge** | Brainstorming's project design-document check | AskIt has an explicit independent challenge, model selection, PASS/ESCALATE outcome, and test-contract review. For projects, Superpowers checks whether a builder can proceed, delegates when a subagent is available, and resolves remaining design questions before approval. Small designs skip that builder check. |
| **04 Spec Change** | Design revision and execution rulings | AskIt has an explicit human decision for semantic changes. Superpowers' execution skills resolve many plan defects and ambiguities through ledgered rulings, with the spec remaining binding and four named stop conditions. |
| **05 Plan** | `writing-plans` | Both decompose into reviewable outcomes and test steps. AskIt adds a TaskGraph, exact task/test mapping, and independently pinned obligations. Superpowers writes executable Markdown steps and asks the human to review the plan and select/preserve an execution method. |
| **06 Implement** | `subagent-driven-development` or `executing-plans`, plus TDD | AskIt uses a stateful one-writer task loop. Superpowers offers fresh implementer/reviewer contexts per task or inline implementation with a final fresh review. |
| **07 Review** | `requesting-code-review`, task review, final review | AskIt binds approval to candidate/evidence and task boundaries. Superpowers subagent execution checks spec compliance and quality per task, then performs a broad whole-branch review. Inline mode has no independent per-task review. |
| **08 Refactor** | TDD refactor, `receiving-code-review`, execution fix loops | AskIt's active task loop closes every valid local finding or retains an evidence-backed withdrawal. Superpowers distinguishes severity, defers minor findings to the ledger, and has bounded correction/adjudication rules. |
| **09 Verify** | `verification-before-completion` and finishing checks | Both require actual fresh checks. AskIt composes a committed CheckPlan with structured criterion/case execution and review evidence. Superpowers requires commands and outputs proving claims, including the project's full suite at task/finish boundaries. |
| **10 Accept** | `finishing-a-development-branch` | AskIt records semantic acceptance and context audit, normally with a human acceptance choice. Superpowers asks how to integrate the verified branch: merge, push/PR, or keep it. These decisions authorize different things. |

Stage sources: [AskIt contracts](../../.agents/ask/stages/).
Superpowers counterparts:
[brainstorming](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/brainstorming/SKILL.md),
[writing plans](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/writing-plans/SKILL.md),
[inline execution](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/executing-plans/SKILL.md),
[finishing](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/finishing-a-development-branch/SKILL.md).

## 3. Walk the same feature through both

Suppose you ask: “Export the filtered orders table as CSV so support can
analyze it. Do not change permissions.”

### In AskIt

1. Classify the outcome as feature work. Decide whether the destination is
   clear; Explore can be genuinely skipped.
2. Clarify decisions such as all filtered rows versus current page, columns,
   and timestamp format. Approve the complete committed intent/assumptions.
3. Produce the spec and criterion metadata; independently challenge them.
4. Prepare the plan, task graph, and test mapping. Independently review and
   pin the exact implementation/test obligations.
5. Execute task slices through Red → Green → Refactor → independent Review.
   Integrate only current approved candidates with passing evidence.
6. Run aggregate Verify, assemble completion/context-audit evidence, record
   the tested SHA, and ask you to accept the workstream.
7. Handle merge/release separately under repository policy and authorization.

The durable handoff answers “What did we agree to?”, “Which criterion does
this test prove?”, “Which candidate was reviewed?”, and “Which source passed?”

### In the inspected Superpowers version

1. Brainstorm against the existing project and request. Ask only missing
   questions that change what gets built, and understand Why before steering
   through named options.
2. Present approaches, write a suitably sized design document, perform the
   builder check for a project-sized design, and obtain design approval.
3. Write the implementation plan. Have the human review it and choose an
   execution method unless that method was already selected.
4. Reuse existing workspace isolation, or establish the agreed worktree/in-place
   arrangement. Execute with either fresh agents and review per task or inline
   work plus one final fresh review. Both retain a per-plan ledger and use TDD.
5. Verify and review the whole branch, then ask whether to merge, push and
   create a PR, or keep it. Detached workspaces have a reduced menu.

The durable handoff centers on the design, executable plan, commits, progress
ledger, reports, and review packages. Inline execution trades away independent
per-task review to avoid repeated fresh implementer/reviewer contexts. That
is an explicit workflow choice, not permission to skip testing or final review.

## 4. Compare the details that affect daily use

| Concern | AskIt | Inspected Superpowers |
| --- | --- | --- |
| **Entry routing** | Explicit bug/feature/mixed gate before stage/skill selection; reported bug must reproduce before its regression/fix. | Bootstrap routes building to brainstorming and bugs to systematic debugging; debugging requires root-cause investigation and reproduction before fixes. |
| **Very small changes** | Clear destinations skip Explore; focused reproduced bugs reuse existing contracts. Feature artifacts remain required on-path. | Brainstorming explicitly allows an entirely clear quick task to proceed directly; other small changes use a short design. |
| **Human question style** | Selectable alternatives with trade-offs and optional same-answer context; routine defaults are explicit. | Open-ended discovery until Why is understood; one question at a time; concrete options when appropriate afterward. |
| **Approval persistence** | `confirm-intent` binds the exact intent digest; stale/missing approval blocks normal feature implementation. | Design approval and plan review/handoff are conversational workflow gates recorded in documents/session context; the inspected core skills do not define an equivalent intent-digest CLI gate. |
| **Mid-plan judgment** | Unresolved What/Why, invariant, public API, architecture-boundary or security-policy changes escalate under delegation rules. | Execution resolves many ambiguities/conflicts through recorded rulings. Stops are destructive/irreversible operations, security-sensitive actions, external side effects normally requiring permission, or a plan with no non-guesswork path forward. |
| **TDD** | Immutable executed Red and final Green bound to accepted cases; typed reviewed exemptions for limited nonbehavioral work. | Strong test-first behavior: watch the intended failure, write minimal production code, run Green, refactor. Exceptions require human permission under its TDD skill. |
| **Verification machinery** | CheckPlan plus criteria/type/case evidence, reviewed mappings and source bindings; supported per-case runner currently Python `unittest`. | Project-native commands and actual output; examples span languages. The inspected workflow does not prescribe AskIt's canonical JSON criterion-completion gate. |
| **Execution modes** | Normal feature planning produces a graph; one unintegrated task writer. Optional isolated task branch/worktree. | Explicit subagent-driven and inline modes. Inline has no independent task review; final fresh review remains expected when tooling permits it. |
| **Parallelism** | Serializes conflicting workstreams and in-workstream writers; disjoint workstreams require an accepted split. | Dedicated parallel-dispatch skill for independent problem domains without shared state; the subagent task workflow itself dispatches implementers sequentially. |
| **Workspaces** | Workstream branch from `develop`; optional runner-owned task worktree and FF-only integration. | Detect existing isolation, prefer native worktree tools, ask consent if preference is unknown, and honor in-place work when declined. No universal `develop` requirement. |
| **Recovery** | Branch/artifact/state inspection, coordinator locks, candidate-bound evidence, checkpoints, exact authorization endpoint. | Per-plan ignored workspace under `.superpowers/sdd/`, progress ledger, reports, resume rules, and Git history. It explicitly guards against redispatching completed tasks after compaction. |
| **Review correction** | Active-task approval stays blocked by valid unresolved local findings, stale evidence, or exhausted retries. Broader work is parked separately. | Minor findings go to ledger/final review. Subagent fix loop allows five rounds, escalates implementation capability in later rounds, then requires controller adjudication/recorded rulings. |
| **Model policy** | Runtime bindings, stage/risk defaults, repository/workstream overrides, independent review/challenge model choices. | Role/task model guidance favors the least powerful adequate model and more capable help where needed; details depend on the harness. |
| **Skills/customization** | Manifest pins community methods; canonical stages plus consumer overlays generate runtime projections. | Composable skill collection with bootstrap/harness integrations; repository/user instructions take precedence over skills. |
| **Optional tooling** | Engineering Model, guarded workbench, exact workflow-reference catalogs, experiment provenance, tracker setup. | Brainstorming visual companion and session-diagnosis skill; workflow helpers focus on plans, implementation/review packages, and recovery. |
| **Finish** | Evidence eligibility and human semantic acceptance are explicit; release authority is separate. | Verify full suite, present an integration menu, execute the selected authorized action, and clean up according to workspace provenance. |

Detailed evidence for the less obvious distinctions:

- Bug routing: [AskIt workflow](../policies/workflow.md),
  [Superpowers debugging](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/systematic-debugging/SKILL.md).
- Execution authority: [AskIt delegation](../policies/delegation.md),
  [Superpowers execution](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/executing-plans/SKILL.md).
- Evidence: [AskIt traceability](spec-test-traceability.md),
  [Superpowers verification](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/verification-before-completion/SKILL.md).
- Correction: [AskIt task loop](../../.agents/ask/task-loop.md),
  [Superpowers fix loop](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development/references/fix-loop.md).
- Recovery: [AskIt evidence mechanics](inner-loop-evidence.md),
  [Superpowers resume rules](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/subagent-driven-development/references/resuming.md).
- Parallelism/workspaces:
  [AskIt worktree policy](../policies/worktree.md),
  [Superpowers parallel dispatch](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/dispatching-parallel-agents/SKILL.md),
  [Superpowers worktrees](https://github.com/obra/superpowers/blob/22f0b463e7a5e579904dd6211a520321035526f7/skills/using-git-worktrees/SKILL.md).

## 5. Which fits your workflow?

These are judgments from the inspected designs, not measured superiority claims.

**AskIt is a closer fit when** your team wants reconstructable approval and
completion records across sessions, explicit control over semantic changes,
reviewed criteria-to-test obligations, and repository-level workflow tooling.
Budget for artifact maintenance, contract review, and supported test adapters.
Its general stage prose should not be mistaken for an already portable
structured runner for every language.

**Superpowers is a closer fit when** you want agent workflow skills that work
with project-native tools, prefer a design/plan/ledger-centered handoff, and
want an explicit choice between per-task reviewers and cheaper inline
execution. Budget for checking that the harness bootstrap actually loads,
preserving the ignored ledger workspace, and trusting/auditing execution rulings.
Its skill mandates are meaningful, but are not the same mechanism as AskIt's
script-validated source/evidence relationships.

Both can be heavy if every small request becomes a full project. Use their
actual small-task/bug routes and stated opt-outs rather than inventing a
lighter procedure while claiming to follow all their gates.

## 6. Can you use them together?

They share useful methods, but enabling two full workflow owners creates
conflicts. If combining them, explicitly select one governing protocol and
borrow named methods within its boundaries.

| Potential collision | Resolve before combining |
| --- | --- |
| AskIt asks selectable Grill questions; Superpowers starts Why discovery with open questions | Choose which intake contract governs this workstream. |
| AskIt records intent approval once and continues; Superpowers asks for design approval and plan review/method selection | State which artifact/decision satisfies which gate; do not assume one unseen document was approved by another decision. |
| AskIt requires Spec Change for semantic changes; Superpowers execution permits many ledgered rulings | Preserve the governing spec-change authority; do not let a borrowed execution skill broaden it. |
| AskIt serializes task writers; parallel-dispatch can run independent work concurrently | Keep borrowed parallel research/work within the governing writer and scope rules. |
| AskIt pins structured cases; Superpowers runs native project commands | Native passing output alone cannot fulfill AskIt's structured completion contract. |
| Different branch/worktree and finishing conventions | Preserve the chosen branch base and release/merge authority. |

For an AskIt project, a practical combination is to keep AskIt in charge of
intent, specifications, task ownership, evidence, and acceptance, while using
a selected debugging or test-design method where its rules agree. The imported
method does not replace required artifacts, independent review, or supported
execution evidence. This is a possible integration approach, not an integration
implemented or tested by this comparison.
