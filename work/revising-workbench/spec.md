# Specification: Recover work context and inspect trustworthy evidence

## Status

PROPOSED, revision 2, 2026-10-16. Work: `revising-workbench`.
Source intent: [intent.md](intent.md). Criterion contract: [spec.json](spec.json).
The challenge corrections are integrated into the requirements below.
Independent review of these revised bytes remains pending.

## Goal and scope

The returning developer can open an existing Story or Task, understand its
purpose and promised behavior, find its delivery work, and assess readable tests
and actual evidence without reconstructing chat history. One representative
Story demonstrates that journey; relationship and entry rules apply generally.

The environment's Epic is “Inspect repository engineering work.” Its user is the
developer returning to their repository. Its promised outcome is recovery of
work context and an honest account of delivery and evidence. Scope includes
repository definitions, related work, source passages and retained local results.
Completion requires the acceptance criteria and representative journey below.
An execution workstream alone does not imply an Epic or create this definition.

Baseline authority is accepted revision 3 of
`specs/current/structured-agentic-environment.md` and its JSON, as present at
`159f516d5fb81575b1f96a1f310ae66e3427c31f`. Preserve its validator, semantic editing,
dependency invalidation, pre/action/post/publication guard, read-only evidence
authority, CLI projections and current decision safeguards. This specification
changes work entry, relationships, concrete flow selection and contextual
inspection. Existing plans, accepted pins and runtime state retain their original
work identity. Future adoption requires reviewed migration and a new test contract.

Non-goals: product implementation in this drafting task; replacing the frontend;
automatic test execution or acceptance; inline specification editing; tracker API
integration or backlog synchronization; reconstructing historical planning;
requiring every item to belong to an Epic or Story; changing evidence authority.

## Work entry

The adopted agent/coordinator intake owns subject resolution during its initial
Explore/Grill work selection, before branch creation, intent recording or delivery
admission. It invokes the shared read-only context resolver. The proposed CLI
`./ask model context` exposes the same resolution for inspection; testing that
command alone does not establish that the coordinator invokes it.

Resolve explicit request subjects first, using referenced repository items, later
cards or supplied tracker context. An explicit subject overrides a prior recorded
association. Conflicting explicit identities require clarification. Otherwise use
a valid recorded subject association. The branch locates execution records; it
does not classify the product subject. With no known subject, present a chooser
or explain the proposed standalone scope. A later card proposes work and does not
by itself prove a live Task or approved contribution.

Present subject identity, source revision, known relationships, bounded contribution,
exclusions and execution owner. An explicit subject differing from the checkout's
work stays distinct; clarify a material ownership conflict before writes. Missing
optional ancestors need no invented parent or clarification. Unavailable external
context is labeled unavailable. Inspection-only entry creates no branch, intent,
node or assignment. Writing a confirmed association uses the existing guarded
definition path and records it in the intent.

## Relationships and identity

Adopt `ask-engineering-model/v2` explicitly. Preserve baseline node types, stable
IDs, lifecycle rules and legal dependency pairs. An intent is optional, with at
most one per model. Feature, requirement, Story, Scenario and Task may each have
zero or one legal containment parent. A Story expresses a user outcome and may
have one or multiple concrete Scenarios. Feature expresses a related capability.

Retain the baseline legal `contains` pairs; add many-to-many task→story/scenario
`contributes_to` and feature→story `enables`. Support edges express contribution,
independently of containment, blocking and executable ownership. Reject duplicate
identities, broken local links, illegal edges, multiple containment parents,
containment/dependency cycles and contradictory lifecycle/resolution states.
Standalone Tasks and Scenarios without Stories are valid and visible.

Product identity is `(owning model work_id, node_id)`. Execution Task identity is
separately `(execution work_id, task_id)`. A model may contain at most one Task
alias for a given execution Task. Equal-looking IDs, later-card paths and supplied
tracker identifiers never create implicit joins. Keep definition lifecycle,
readiness, execution/integration state and verified completion separate; project
execution state from its existing owner. A declared `done` is no proof of delivery.

Support edges stay within one model in this version. A foreign product resolves
read-only in its owning model at an explicit revision; do not clone a local alias
or create a foreign support edge. Missing/conflicting targets remain explicit.
V1 retains its original validation rules and evidence attribution. Migration
preserves IDs and references, needs reviewed adoption, and never runs on browsing.

## Concrete flows and test coverage

An active Scenario selects a canonical test-plan case by `(source work_id,
test-plan digest, case ID)`. That case's `scenario` owns the concrete context,
action and expected outcome. Criterion references identify the broader obligation;
model prose can explain the flow but cannot supply competing editable assertions.
An unplanned Scenario remains draft with a visible missing-case limitation.

A Test's explicit `covers` edge must agree with the Scenario's selected case or
an explicit reviewed flow mapping in the canonical plan. Reject contradictions.
Criterion overlap alone is displayed as a related obligation, never inferred
flow coverage or proof. Two Scenarios for successful publication and stale
rejection can share EM-007 while selecting different concrete cases; a success
test must not appear as proving stale rejection. Shared Tests and Tasks retain
one identity and their original executable ownership on every navigation route.

## Source context and admission

Each context reference identifies a repository-relative path and a unique heading
path or stable plan-task selector. Display the selected passage with path,
section/task identity and inspected revision. Capture source bytes and selector
in the validated snapshot; offer surrounding text on request. Never substitute
a similar heading or current text into a historical view.

| Reference condition | Inspection and admission |
| --- | --- |
| Unsafe/escaping/symlink target or malformed selector | Reject document admission; permit read-only diagnostics of explicitly untrusted input and a labeled last-validated view. Ordinary actions stay blocked; repair/import is explicit. |
| No optional reference recorded | Admit; show no context recorded. |
| Safe missing file or well-formed selector with zero matches | Admit as unavailable context; do not choose another passage. |
| Well-formed selector with multiple matches | Admit as ambiguous context; do not choose the first match. |
| Unique safe match | Admit and display the captured passage. |

An admitted context limitation does not block unrelated guarded actions. An
action that requires the unresolved passage to establish its contract refuses
admission until it resolves uniquely. Missing required representative context
blocks that demonstration. Bind input identity to bytes, selector, dependency
discovery/rule version and missing/match state. File creation/deletion, linked-only
edits and unique-to-ambiguous transitions invalidate freshness. Readers consume
one validated generation. Existing pre/action/post/publication and stale-form
checks apply to all adopted public mutations and workflow admission entry points.

## Workbench behavior

Open a requested Story or Task directly with its known purpose and relationships.
With no selected subject, use resolved work context or a labeled chooser. Keep
checkout, product subject and inspected revision distinct. Inventory remains
based on local live refs and the default-branch archive; other committed revisions
are inspected without changing the checkout or refs and remain read-only.

Show Epic purpose, Story outcome, Scenario flow and Task outcome as meaningful
prose. Task detail includes relevant spec passages, its actual plan entry,
dependencies, owned work, related Stories/Scenarios, scoped Tests and evidence
limitations. A title, ID and source link alone are insufficient. An unplanned item
shows no recorded plan entry. A shared Task opens from each supporting context;
Back restores the initiating route. Breadcrumbs describe that route, preserving
missing relationships honestly. Summary counts open their exact underlying records.

Retain guarded reasoned decision forms in admitted current work. Historical
inspection cannot resolve decisions. Use responsive navigation and detail,
accessible names, keyboard focus, contrast and status text independent of color.
Overview performs no test-source parsing or evidence scan; selected details load
lazily. Identity-bound caches must expose changed or tampered inputs on refresh.
Measure actual initial/navigation latency against the existing documented pilot
budgets, recording samples and misses. A framework change requires measured
limitations and a reviewed amendment.

## Readable tests and actual results

For the selected Task and concrete Scenario, show the Test's setup/input, action,
expected behavior, assertion and source at the inspected revision. Include the
same-revision fixture/helper/global definitions and explanatory context needed
to understand their role. Curated explicit references are sufficient; no general
whole-program analyzer or mandatory test syntax is required.

Use the existing nonmutating evidence evaluation authority for report/log digests,
work/test/run/contract/candidate identity, accepted authority and semantic review.
Keep actual observations distinct from the assertion's expected behavior. Display
passed, failed, not run, skipped, runtime error, stale, historical and unavailable
states accurately, with retained failures and time/duration when present. Explain
technical identifiers in collapsed details. A case pass never implies workstream
completion. Inspection writes nothing, runs no tests and advances no accepted ref.

Human comprehension requires a successful recorded exercise. From the selected
Task, the returning human identifies purpose, spec/plan context, concrete flow,
setup, action, expected observation, assertion, actual outcome and applicability
without chat assistance. Bind each pass/fail answer to the candidate/snapshot and
selected Task/Scenario/Test, source and necessary helper/fixture revisions. Any
unresolved failure blocks demonstration completion until corrected and reviewed
again, or explicitly escalated for a scope decision. Relevant context, source or
evidence changes invalidate the review. Automation remains required; this exercise
grants no review-only authority and cannot certify unexecuted behavior.

## Representative Story

“As the developer returning to my repository, I can open a delivery Task, recover
the behavior it promises and understand its evidence so I can decide what remains.”
This is current modeling; its linkage to old records does not reconstruct old
planning or claim that this Story previously existed.

| Selected record | Exact source |
| --- | --- |
| Execution Task | `(structured-agentic-environment, WB-003)` |
| Plan entry | `work/structured-agentic-environment/plan.md`, `Work breakdown`, row `WB-003` |
| Main-spec context | `specs/current/structured-agentic-environment.md`, `Projections and evidence` and `Interactive UI` |
| Concrete flow | `WB-evidence-identity` in that work's `test-plan.json`, bound to its inspected digest |
| Test | `_ask/tests/test_engineering_workbench_evidence.py`, `test_engineering_workbench_evidence.WorkbenchTests.test_results_match_work_test_run_and_contract` |
| Necessary test context | Same-revision `WorkbenchTests.setUp`, `_report`, `_ledger`, `_blob_digest`, `git`, `write` and `commit`, including their fixture values and imported production boundary |
| Retained Task result | `work/structured-agentic-environment/inner-loop/results/WB-003.json` |
| Recorded candidate | `70dd295aacff869857081a94870d02fcbf4d640c` |
| Recorded red / final green | `111e0f24d5e448c387cd1558b864b18e` / `799924ec199b4717a3eabf4fb39a1bdc` |

The concrete flow selects a result by work/test/run/contract identity while
excluding foreign or contradictory records. The selected test builds temporary
repository/report fixtures; those fixture outcomes are distinct from the genuine
retained execution of that test. Inspect source and spec/plan passages at their
declared revisions, retaining explicit historical applicability.

Both log paths named by the committed Task result were present in the original
checkout during the preliminary availability check. This is an availability
observation, not validation of run authority or completion. Full local reports,
logs and authority must pass the existing evaluator before demonstration success.
Require at least one genuine retained execution result plus the successful human
exercise. If a necessary record/authority is unavailable, identify the exact
blocked prerequisite; fixtures, output excerpts and unavailable labels cannot
substitute for the required real result. Preserve historical records at their
original paths. Remove the old harness example from the main pilot presentation
while keeping explicit historical inspection available.

## Acceptance criteria

[spec.json](spec.json) records the observable Given/When/Then contract. EM-001–007
retain the accepted foundation obligations. EM-008–018 cover relationships and
identity, navigation, Task detail, readable evidence, performance, request intake,
versioned migration, passage admission/freshness, the complete real demonstration,
historical preservation and the repository/tracker boundary. Their IDs retain
lineage; the new work identity/digest never inherits old completion or approval.

## E2E and verification

Applicability: applies. Cover direct Story and Task entry, standalone/missing-parent
records, shared Task navigation and Back, two concrete flows sharing a criterion,
fresh coordinator intake with explicit/recorded/conflicting subjects, inspection-only
entry, each reference classification and its action-admission result, linked-only
freshness changes, helper-dependent assertions, and the representative real journey.

Use unit checks for graph/identity/selector rules, integration tests through the
actual coordinator intake and shared guard, Streamlit AppTest and a real temporary
browser for user journeys. Record the candidate-bound human exercise alongside
automation. Test-owned repositories/data/servers are reset and removed on teardown;
never alter committed pilot evidence to manufacture a result. A future independently
reviewed plan assigns concrete test cases, migration and delivery ownership, retaining
genuine red/final-green and semantic review obligations. This drafting task establishes
requirements only and does not execute or certify the proposed product behavior.
