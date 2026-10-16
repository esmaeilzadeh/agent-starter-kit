# Plan: Recover work context and inspect trustworthy evidence

Status: PROPOSED planning artifact only. Model: `gpt-6.1-sol`, reasoning `high`.

## Specification and readiness

This plan references exactly one product specification: [spec.md](spec.md),
PROPOSED revision 2, with its canonical criterion companion [spec.json](spec.json)
(SHA256 canonical JSON `626fab82df682bdc7b382e4188bc822e488a8bf4ca9682a209be535fcea119bd`).
Its baseline incorporation is defined there; historical source/plan/test records
are factual interfaces and pilot inputs, not a second product contract or approval.
The independent [spec-challenge.md](spec-challenge.md) PASS binds those proposed
bytes. It neither confirms intent nor authorizes implementation.

The user's request authorizes preparing this proposed plan. Complete-intent
confirmation remains pending. Before implementation, the coordinator must record
that exact confirmation, promote/register the same reviewed specification through
the kit, independently review and pin the exact TaskGraph/test-plan/delegation
contract, and reconcile branch admission. Preserve the human-chosen current
`revising-workbench` branch: `check-workstream.sh` currently requires
`agent/revising-workbench`, so the naming override alone cannot make its check
pass. Resolve that policy/tooling mismatch explicitly before execution; this plan
does not weaken or modify the branch guard. No refs, runtime state, migration,
implementation tests or accepted authority are initialized by preparing this plan.

## Approach

Extend the existing Python engineering model, shared snapshots/guard, read-only
evidence evaluator and native Streamlit UI. Keep v1 validation unchanged through
schema dispatch; explicitly adopt v2 for new definitions. Qualified product and
execution identities, selected canonical flows, captured source passages and
readable curated helpers feed one projection consumed by CLI and UI. The actual
initial Explore/Grill intake caller invokes the shared resolver before existing
work creation/admission. Streamlit stays; historical records remain in place.

Implementation choices, exact selector grammar, action-to-passage dependencies,
intake caller binding, migration/registration and comprehension record are in
[planning-design.md](planning-design.md). Read the applicable section before its
task. No unresolved product decision is delegated to an investigation task.
The prepared writing-for-agents skill informs these artifacts. UI implementation
uses the installed Streamlit skill and version-matched session-state, layout and
performance references; no dependency installation is needed to draft this plan.

## Work breakdown

Nine bounded tasks run in the order below, in one workstream with one writer.
Every row is the same task and scope as [inner-loop/tasks.yaml](inner-loop/tasks.yaml)
and [test-plan.json](test-plan.json). Exact owned paths are repeated here to make
review concrete. Shared paths are serialized by the explicit dependency chain;
read-only baseline test sources need no modification permission. Each task commits
its assertion-red tests before behavior implementation, then meaningful source
steps, and ends with candidate-bound final green and independent semantic review.
Unchanged regressions need fresh execution, without imported old exemptions.

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| RWB-101 | Version-dispatched validation, separate product/execution identities and canonical flow coverage; preserved v1 rules | None | `_ask/scripts/engineering_model/validation.py`; `_ask/scripts/engineering_model/identities.py`; `_ask/scripts/engineering_model/flows.py`; `_ask/scripts/engineering_model/canonical.py`; `_ask/scripts/engineering_model/domain.py`; `_ask/tests/test_revising_model.py`; `_ask/tests/revising_fixture.py`; `_ask/docs/engineering-model.md` | RWB-V2-GRAPH, RWB-QUALIFIED-ID, RWB-FLOW-SELECTION, RWB-V1-VALID, RWB-V1-GRAPH, RWB-V1-FIELDS, RWB-V1-REFS, RWB-V1-DECISION, RWB-V1-REVISE, RWB-V1-STALE, RWB-V1-CAS | Current v1 regression executions and new assertion red/final green for v2 graph, alias, lifecycle and selected-flow counterexamples; independent semantic review of version dispatch |
| RWB-102 | Safe selector resolution and dependency-bound snapshots across existing guarded actions | RWB-101 | `_ask/scripts/engineering_model/passages.py`; `_ask/scripts/engineering_model/snapshot.py`; `_ask/scripts/engineering_model/canonical.py`; `_ask/scripts/engineering_model/actions.py`; `_ask/scripts/engineering_model/admission.py`; `_ask/scripts/engineering_model/workflow.py`; `_ask/scripts/engineering_model/observer.py`; `_ask/tests/test_revising_context.py` | RWB-SELECTORS, RWB-PASSAGE-ACTIONS, RWB-CONTEXT-FRESHNESS, RWB-GUARD-PRE, RWB-GUARD-POST, RWB-GUARD-REFS, RWB-GUARD-EVENTS, RWB-GUARD-PARITY, RWB-GUARD-PUBLISH, RWB-GUARD-BOOTSTRAP, RWB-GUARD-BATCH, RWB-GUARD-ORDER, RWB-GUARD-ENTRYPOINTS | Selector/admission matrix and every public guard entry pass; action spy proves exactly pre/action/post/publication with identical captured lineage; linked-only and missing/ambiguous transitions invalidate |
| RWB-103 | Shared read-only resolver invoked by the adopted initial Explore/Grill coordinator caller before existing writes | RWB-102 | `_ask/scripts/engineering_model/context.py`; `_ask/scripts/stage-intake.py`; `_ask/scripts/engineering_model/__main__.py`; `_ask/scripts/model.sh`; `ask`; `.agents/ask/stages/00-explore.md`; `.agents/ask/stages/01-grill.md`; `.agents/skills/kit-00-explore/SKILL.md`; `.agents/skills/kit-01-grill/SKILL.md`; `.cursor/commands/00-explore.md`; `.cursor/commands/01-grill.md`; `.cursor/skills/kit-00-explore/SKILL.md`; `.cursor/skills/kit-01-grill/SKILL.md`; `_ask/tests/test_revising_intake.py`; `_ask/docs/engineering-model.md`; `_ask/scripts/engineering_model/domain.py`; `_ask/scripts/engineering_model/actions.py`; `_ask/scripts/engineering_model/workflow.py` | RWB-SUBJECT-RULES, RWB-FRESH-INTAKE, RWB-CONTEXT-CLI | Fresh-context adopted caller trace invokes the resolver before branch/intent/delivery operations; conflicting or inspection-only requests produce no writes/assignments; generated projections agree |
| RWB-104 | Qualified support graph, exact plan/spec passages, route data and read-only foreign revisions | RWB-103 | `_ask/scripts/engineering_model/workbench.py`; `_ask/scripts/engineering_model/projection.py`; `_ask/scripts/engineering_model/workbench_sources.py`; `_ask/tests/test_revising_projection.py` | RWB-PROJECTION, RWB-HISTORICAL, RWB-CLI-PROJECTION, RWB-CLI-JOURNEY, RWB-V1-PROJECTIONS | Standalone/shared work retains one identity; concrete flow scopes avoid criterion joins; source inspection leaves checkout/refs untouched; JSON/Markdown and CLI guarded reload regressions execute |
| RWB-105 | Same-revision explicit source context and existing authority-bound retained result inspection | RWB-104 | `_ask/scripts/engineering_model/workbench_evidence.py`; `_ask/scripts/engineering_model/readable_tests.py`; `_ask/tests/test_revising_evidence.py` | RWB-SOURCE-HELPERS, RWB-EVIDENCE-JOINS, RWB-EVIDENCE-STATES, RWB-V1-EVIDENCE-REAL, RWB-V1-EVIDENCE-MISSING | Selected test and necessary same-revision helpers are readable; adversarial report/log/candidate/source/contract joins reject and retained states remain distinct; unchanged evaluator regressions execute |
| RWB-106 | Direct Story/Task entry, chooser, shared Back routes, exact summaries and readable Task context | RWB-105 | `_ask/ui/streamlit_app.py`; `_ask/ui/workbench_context.py`; `_ask/ui/workbench_navigation.py`; `_ask/ui/workbench_overview.py`; `_ask/ui/workbench_stories.py`; `_ask/ui/workbench_scenarios.py`; `_ask/ui/workbench_tasks.py`; `_ask/tests/test_revising_ui.py` | RWB-APP-ENTRY, RWB-APP-TASK | AppTest assertions prove direct routes and returned route ancestry, summary record sets, complete contextual Task detail and historical read-only action restrictions |
| RWB-107 | Lazy helper/source/observation detail, explained collapsed provenance and stale-safe reasoned forms | RWB-106 | `_ask/ui/workbench_tests.py`; `_ask/ui/workbench_debug.py`; `_ask/ui/workbench_attention.py`; `_ask/ui/workbench_loading.py`; `_ask/tests/test_revising_detail.py` | RWB-APP-EVIDENCE, RWB-APP-DECISIONS, RWB-LAZY-CACHE | AppTest proves flow-specific readable source/results, all honest states and collapsed identifiers; current decision persistence and invalid/stale/historical no-write cases pass; zero eager scans and tamper refresh asserted |
| RWB-108 | Explicit reviewed v1 to v2 migration, new-work model/contract registration, genuine WB-003 inspection and bound comprehension format | RWB-107 | `_ask/scripts/engineering_model/migration.py`; `_ask/scripts/engineering_model/readability.py`; `_ask/scripts/engineering_model/__main__.py`; `_ask/scripts/model.sh`; `_ask/tests/test_revising_pilot.py`; `work/revising-workbench/engineering-model.json`; `work/revising-workbench/representative-story.md`; `work/revising-workbench/migration-review.md`; `_ask/docs/engineering-model.md`; `_ask/scripts/engineering_model/actions.py`; `_ask/scripts/engineering_model/workflow.py` | RWB-MIGRATION, RWB-NEW-CONTRACT, RWB-READABILITY-BINDING, RWB-GENUINE-WB003 | Explicit migration review and ID/reference/evidence-preservation diff; genuine authority-evaluated historical result and exact helper/spec/plan selections; failure/staleness-sensitive comprehension validation; no old record rewritten |
| RWB-109 | Browser E2E, accessibility/performance samples and successful candidate-bound representative human exercise | RWB-108 | `_ask/tests/test_revising_browser.py`; `_ask/tests/test_revising_performance.py`; `_ask/tests/revising_browser_support.py`; `_ask/ui/benchmark_workbench.py`; `_ask/ui/requirements-test.txt`; `_ask/ui/.streamlit/config.toml`; `_ask/ui/streamlit_app.py`; `_ask/ui/workbench_context.py`; `_ask/ui/workbench_navigation.py`; `_ask/ui/workbench_tasks.py`; `_ask/ui/workbench_attention.py`; `_ask/ui/workbench_tests.py`; `_ask/ui/workbench_debug.py`; `_ask/ui/workbench_loading.py`; `work/revising-workbench/workbench-validation.md` | RWB-BROWSER-NAV, RWB-BROWSER-GUARD, RWB-BROWSER-EVIDENCE, RWB-BROWSER-ACCESS, RWB-BROWSER-PILOT, RWB-BROWSER-BUDGETS, RWB-HUMAN-COMPLETION | Real browser traces/screenshots, keyboard/narrow/contrast assertions, raw 20 warm and five cold measurements, genuine representative journey and independent attributable ten-answer successful human record bound to final candidate; final workstream Verify/semantic review remain required |

## Dependencies and execution sequence

1. Finish the confirmation, specification promotion, branch-policy reconciliation
   and independent mapping review prerequisites above. Commit exact proposed
   contracts before review; resolve findings without silently changing What/Why.
   Review required types as well as existence of case links. Coordinator records
   `traceability accept-plan revising-workbench --revision <contract-sha>` with
   independent evidence only after these prerequisites, then commits its accepted
   record. The authority ref is coordinator-owned, outside candidate source.
2. Run graph/contract checks against the promoted spec and pin them before starting
   the first task. RWB-101→102→103→104→105→106→107→108→109 is a strict chain, so
   every shared source/module has one active writer. No parallel related branches.
   Production definitions and every changed public mutation stay behind the
   existing immutable-base runner and guard; candidate edits cannot replace gates.
3. For each task, commit genuine failing assertions at a red candidate, execute
   its accepted scope, implement and commit meaningful steps, then execute final
   green at the exact candidate. Setup/import/browser failures are blocked setup,
   never behavior red. Use TaskResult v2, coordinator-recorded independent review
   and existing FF-only inner-loop integration. Initialize runtime state only when
   execution is authorized. A task pass cannot complete the whole workstream.
4. RWB-108 adds a new model/pilot and explicit reviewed adoption metadata. Existing
   v1 model/plan/pin/runtime paths remain untouched. New work has its own product
   spec/digest and contract; equal EM IDs transfer no completion/red/approval.
   `traceability migrate` creates scaffolds only and must never be treated as
   reviewed model migration or accepted contract registration.
5. Freeze final source, retain real-browser/benchmark evidence, and conduct the
   independent human comprehension exercise against that exact candidate. All ten
   answers must pass with current bindings; preserve failures. Then run final
   semantic review, `./ask verify`, explicit workstream `check-completion` and
   `check-workstream --acceptance`, and `record-result` with the tested source SHA.
   Acceptance remains the separate human decision; no deployment/merge/push.

## Verification approach

The 53 explicit canonical cases cover all EM-001–018. `test-plan.json` owns exact
Given/When/Then, criterion-specific assertions, required types, selectors and
source paths. Every case belongs to exactly one task. No review-only criterion,
legacy approval transfer or unsupported shell/browser/human runner is declared.

Inherited EM-001–007 retain validation, attributable edits/invalidation, CLI parity,
evidence integrity, snapshot UI, reasoned/stale decision forms and all guard
entrypoints. Existing source methods were inspected and are declared as current
`regression` executions under new case IDs; new/changed behaviors require new
red/final-green evidence. Keep v1 fixtures distinct from v2 optional-parent cases.
New coverage includes the PASS challenge counterexamples: criterion overlap is
not flow proof; shared Task Back routes preserve origin; branch/later context
cannot create subjects; safe context gaps block only dependent actions; unsafe
input blocks admission; missing-to-present and duplicate passages stale snapshots;
fixture results cannot stand in for genuine WB-003 evidence; failed or stale human
understanding blocks demonstration.

Each runner is supported `python3 -m unittest <exact-qualified-case>` with adapter
`unittest`. Namespace-qualified `_ask.tests.*` selectors are executable imports
from the repository root and intentionally belong to this new contract; the old
WB-003 executable selector remains unchanged in historical inspection. Future
new test files/methods are implementation deliverables, not a claim they exist
or passed today. One case per runner keeps browser measurements within the
existing 300-second adapter timeout and ensures no unmapped discovery cases.
Avoid dynamic subtests. Playwright runs inside ordinary unittest methods, so the
existing adapter records real case outcomes. Missing browser/dependency/server
is an error/refusal, never skipped green. Human answers remain supplemental
attributable evidence; the automated binding test cannot supply those answers.
No runner change is planned. If genuine bounded execution cannot fit the pinned
runner, stop and review an explicit scoped tooling amendment before relying on it.

## E2E and browser evidence

Applicability: applies. Real Playwright browser/server journeys cover direct
Story/Task entry; standalone/missing-parent records; shared Task/Back; exact counts;
current/historical/foreign revision inspection; helper-dependent concrete flows;
all outcome limitations; valid decision persistence and invalid/stale/historical
refusal; exact genuine representative Story; and keyboard/narrow accessibility.
AppTest integration covers the same domain joins and snapshot/forms deterministically
but does not stand in for focus, layout, browser latency or human understanding.

Use test-owned temporary repositories, ephemeral localhost ports and owned browser/
Streamlit processes with finally/addCleanup teardown. All write journeys remain
in temporary repos. Genuine representative tests read the original retained root
through the nonmutating evaluator and candidate code, with before/after source/ref/
evidence checks. Missing exact reports/logs/reviews/authority is a named blocking
prerequisite. Keep raw benchmark output, traces, screenshots and human records
outside immutable candidate source in the new work's traceability runtime subtree.
The old main harness is removed from main pilot presentation only; its historical
paths, identity and explicit inspection remain.

Measure actual representative pilot with 20 warm samples: nearest-rank p95
Overview ≤1500ms, metadata navigation/filter ≤500ms, selected source/result
≤1000ms; five cold restarts each ≤4000ms. Retain environment, candidate, selected
identities, all samples and misses. Record deterministic 100/1000-task structural
workloads without inventing a large-fixture latency SLA. Assert zero initial
source/evidence scanning and content-bound refresh/cache invalidation. Browser
assertions check 390px navigation, accessible names, keyboard/focus, normal text
contrast ≥4.5:1, large text/focus ≥3:1 and written statuses independent of color.

## Risks, escalation and scope

MEDIUM: version/admission and contextual evidence changes affect several public
entrypoints. Preserve immutable verification authority, stale-form identity and
one validated generation. Explicit mutation registry tests and independent
semantic review are required before claiming preserved safeguards.

Named readiness blockers are pending complete-intent confirmation/spec promotion,
new exact contract review/pin and branch-policy reconciliation. Genuine historical
report/log/authority availability and a successful final-candidate human exercise
are mandatory execution prerequisites, not optional substitutions. Record exact
missing inputs if encountered. No product requirement is relaxed to make a check
pass, and an availability observation supplies no execution proof.

Escalate acceptance/identity changes, unsafe passage policy changes, any authority
weakening, inability to retain genuine evidence, unresolved human failures,
repeated budget/accessibility misses, or a needed runner/framework replacement.
Use Spec Change plus independent review for changed obligations/architecture; do
not silently broaden task paths or alter the reviewed contract. Ordinary task
details and routine fixes within that contract need no additional human blessing.

Out of scope: implementing this plan in the planning session; parked fresh-work
orchestration; unrelated backlog work; rewriting old evidence/plans; tracker API
integration or backlog storage; inline spec editing; automatic tests/acceptance on
inspection; frontend replacement; deployment/merge/push. The current delivered
artifacts prepare a reviewable plan only.
