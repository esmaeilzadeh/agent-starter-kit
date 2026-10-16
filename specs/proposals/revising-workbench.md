# Specification: Revising the workbench

Status: PROPOSED revision 1 for `revising-workbench`, 2026-10-16.
Derived from the unapproved revision-4 proposal and independent challenge at
`159f516`. Complete-intent confirmation and independent review of these new
bytes are pending. No accepted pin, test plan or product authority is transferred.

Source intent: `work/revising-workbench/intent.md`.
Baseline: `specs/current/structured-agentic-environment.md` and adjacent JSON
at source commit `159f516`. Preserve baseline behavior except the explicit
amendments below. Existing criterion IDs retain their lineage; equality of IDs
across the two work contracts does not imply equal digests or shared completion.
Old design/plan/runtime records remain historical implementation context, not
this workstream's execution plan. Stop at specification and initialization.

## Authority and scope

A revisioned `work/<id>/engineering-model.json` owns broader engineering definitions and references. Existing canonical criterion JSON, accepted test plans, code, coordinator review/execution evidence and inner-loop runtime remain their own authorities. The model stores references, not competing Given/When/Then or test outcomes. Markdown, machine context and UI are projections. There is no editable “verified” field or UI shortcut to existing acceptance/integration gates.

The intended user is the human returning to their own work, with enough context to recover purpose and understand delivery without chat history. The pilot defines this environment's Epic and one complete representative Story, while entry and relationship behavior also covers existing Stories, Tasks and standalone work. The old harness-review example leaves the main pilot presentation; its records and evidence remain inspectable as explicitly selected historical work. Model creation/validation and controlled editing remain prerequisites for UI implementation. One local cooperating developer; Git remains the change review/history mechanism. No authenticated authorization or multi-host concurrency guarantee is claimed.

Engineering definitions, specification and plan text, and their code/test relationships remain repository-owned and versioned with code. The workbench projects those authorities and does not introduce a separately editable backlog database. An external tracker may provide a referenced identity and coordination context; it is not required to inspect repository-owned work. Jira deployment, API integration, synchronization, sprint management and organization-wide assignment workflows are outside this amendment. Local retained execution evidence remains separate and revision-bound; a historical checkout does not guarantee locally available runtime evidence.

## Definition contract

Proposed schema `ask-engineering-model/v2` (explicit migration required from v1): work_id, positive integer revision, nodes and edges. Stable node IDs are unique nonempty slugs within the model. Node types: intent, requirement, feature, story, scenario, decision, assumption, task, implementation, test, test_run, risk, evidence. Every node has a nonempty title and a type-specific definition lifecycle. Generic nodes use draft/active/retired; decisions open/resolved/retired; assumptions unverified/confirmed/rejected/retired; tasks planned/active/done/retired; risks open/mitigated/retired. Definition lifecycle never asserts execution outcome.

`contains` expresses intent→feature/story/requirement/scenario/task/decision/assumption/risk, feature→story/requirement/scenario/task/decision, story→scenario/task/decision, requirement→scenario. An intent is optional, with at most one per model; its presence does not mean every workstream is an Epic. Every feature/requirement/story/scenario/task may have zero or one containment parent, including active records. Missing parent/Story membership is visible and legal. More than one containment parent remains invalid. A Story is an observable user outcome; a Scenario is a concrete flow/example and may be the only Scenario of its Story. Feature denotes an optional capability, not exclusive ownership of a Story.

New support relationships: task→story/scenario `contributes_to`, and feature→story `enables`. These have many-to-many cardinality and do not imply execution ownership, blocking, completion or exclusive containment. A shared Task has one qualified identity, description, lifecycle and execution attribution regardless of the navigation path. Model identity is `(work_id, node_id)`; equal slugs in different workstreams are never silently joined. Existing reviewed TaskGraph and task scopes retain executable responsibility: a shared support link does not reassign a case or satisfy a second Task's completion obligations. A model Task linked to a TaskGraph record references its qualified identity rather than creating an independent status authority.

Each test still covers at least one Scenario via test→scenario `covers`; a standalone Task may exist before test mapping. Implementation→scenario/task `implements`; test_run→test `executes`; evidence→test/test_run `supports`. `depends_on` keeps its revision-3 legal pairs. Reject broken references, illegal types/edges, duplicates, containment/dependency cycles, contradictory lifecycle/resolution and unexpected fields. Independent validation reports precise stable codes and IDs and never mutates. Support edges do not become dependency edges.

V1 records remain historical/read-only under their original rules. Adoption of v2 requires an explicit reviewed migration that preserves existing IDs, references and evidence attribution. No automatic conversion during browsing and no relabeling a v1 snapshot as v2-valid. A future plan must specify the concrete migration and independently reviewed task/test-contract updates before any implementation; this proposal does not authorize them.

Active requirement references select an existing canonical criterion. Active Scenarios additionally select a concrete canonical test-plan case by qualified work, plan revision/digest and case ID; that case's scenario owns their context/action/outcome. Tests select an existing test-plan case. Implementation references are safe repository-relative source paths, optionally symbols. Evidence/run references are safe repository-relative JSON paths; unavailable runtime evidence is visible missing evidence, not a malformed engineering definition. Resolve paths inside the repository, including symlink checks. Reference-only test/evidence nodes carry no mutable outcome. Draft requirement/scenario nodes may await a canonical reference.

Decisions have at least two unique option IDs/labels. A resolution records option_id, nonempty actor/rationale, UTC timestamp. Resolved state requires a valid resolution; open state has none. History preserves prior resolutions/reopening/invalidation. Actor attribution is cooperative local input, not authentication.

## Semantic editing interface

One shared module provides load/validate, snapshot/project and guarded mutation. Commands add_node, add_edge, remove_edge, resolve_decision, reopen_decision and revise_node cover this slice; change_batch stages coordinated commands/spec-file changes as one action. Node-plus-coverage/context edges can be created atomically; no missing parent is automatically fabricated. Existing batch atomicity remains unchanged. Stable IDs and node types are immutable. Revisions may change title/description/reference and declared type-specific lifecycle; decision options may change only while open. Resolve/reopen/retire use explicit attributable decision operations, with old choices/options retained in history; no raw resolved-state edit bypasses them.

Editing a dependency, resolving/reopening/changing an upstream decision, or adding/removing a dependency reopens affected transitively dependent resolved decisions, preserving prior resolution and reason in history. Planned/active tasks are blocked by open/retired decisions, unverified/rejected/retired assumptions or unfinished/retired task prerequisites. Only resolved decisions, confirmed assumptions and done tasks satisfy their respective prerequisites. Retiring an object never silently satisfies its dependents. A declared done task is not proof of behavioral completion; reopening work is explicit and existing evidence/acceptance authority remains unchanged.

Every mutation goes through the document-state action guard below. Expected state identity includes the model and referenced specification/definition inputs, not just the model-file digest. Valid edits increment the model revision exactly once. Invalid commands, missing attribution or stale inputs do not publish. CLI and UI call this shared interface. Changes remain visible Git changes; the app neither commits nor spawns work.

## Document-state action guard

Before every state-changing engineering action, capture and validate the current definition/reference snapshot. Failure stops before the action is invoked. Stage the action's candidate edits without exposing them to consumers; validate the resulting complete state after the action. Recheck the base input identities, then publish one immutable validated snapshot/generation. Invalid results or concurrent changes prevent publication and preserve the last stable generation. Multi-file actions must not expose partially applied specifications; atomic replacement of individual files alone is not a multi-file transaction.

The validation input set includes the Engineering Model, canonical specification definitions, linked criteria/test definitions and all relevant reference targets. A referenced specification edit/create/delete invalidates the current result even if the model file is unchanged. Bind validation identity to input paths/content, dependency discovery and validator rule version; timestamps alone are insufficient. Readers use bytes from the validated snapshot, not mutable files reread after validation. State-changing actions include semantic spec/model edits and workflow action admission; this guard adds no replacement test-completion or human-approval policy.

Run validation after every specification save/change through the shared change path or document-layer change observer. Startup plus consumer/action entry freshness checks cover external writes and missed observer events. Unmanaged editor/tool changes cannot be made transactional by wishful enforcement: until validated they are untrusted working state and must not become actionable UI/agent input. The last stable snapshot may remain visible only explicitly labeled last-validated/not editable; current actions fail closed. Repair/import is an explicit draft operation, not automatic UI repair or ordinary work on a broken base.

The validator is independently runnable and is the single implementation of graph/reference/lifecycle rules. UI code trusts its validated snapshot contract. User input/action conflicts and external evidence freshness remain separate runtime concerns. Initial import validates existing state before admitting it; there is no bootstrap shortcut treating an invalid initial document as stable.

The adopted pilot's managed public entry points are model/spec change_batch/edit, decision resolve/reopen/revise operations through that edit path, and workflow admission for implementation/review/verification/integration/acceptance. Proposed CLI surfaces are `./ask model edit|admit|validate|watch|show|ui`; these are planned interfaces, not existing commands. Wire existing `inner-loop run/resume` and its integration path, `verify`, `record-result --result pass` and acceptance checking to the same guard for the adopted workstream. Coordinator-managed review/implementation admission uses that interface as well. Readers/show/UI use document admission but do not create a new semantic change. Raw editor saves use the observer plus freshness fallback, not a second mutator. Tests must demonstrate successful pre-validation → one action → post-validation → one publication, with input/result identities, and prove each public state-changing entry point cannot bypass the shared guard. Other workstreams retain existing policy; no unadopted state is labeled validated.

## Performance and implementation freedom

Validator implementation is language-neutral. Reuse suitable existing fast tooling; a lower-level implementation is allowed. Select after a bounded benchmark of actual repository inputs plus deterministic 100/1,000/10,000-node graphs with recorded edge/file counts, invalid-link/cycle variants, cold/warm runs and the complete pre/post action path. Record hardware/tool versions, p50/p95 latency, peak memory and parse/I/O/graph/publication costs. Language labels alone are not evidence of speed. No numerical latency target or performance gain has been agreed or measured yet.

Keep a stable machine interface and diagnostics regardless of implementation. Incremental/cached validation is permitted only when it agrees with full validation, invalidates on referenced input/rule changes and preserves global uniqueness/cardinality/cycle checks. No cache or alternative backend may skip the before/after guard. Full validation remains available for parity tests, startup and final verification. Implementation selection must retain the existing traceability test-driver contract or receive a reviewed binding amendment before implementation.

## Projections and evidence

Machine JSON and deterministic Markdown expose identical object IDs, hierarchy, references, unresolved decisions, dependency reasons and derived task readiness. Projections preserve source/model digests and evidence revision identity. Scenario inspection reads canonical Given/When/Then and planned assertions/cases, source references, required test types, actual retained outcomes and provenance. A declared link is explicitly not proof of behavior.

The read-only evidence adapter reuses a shared nonmutating path through the existing traceability binding and completion checks rather than trusting a cached pass field. This includes static receipt/CheckPlan identity, pinned runner identity, static and behavior log digests, accepted authority, semantic review and actual cases. Extract read-only evaluation from the current report-writing completion operation without weakening normal command checks; do not reimplement a reduced subset in the UI. Historical checks bind to the inspected candidate's inputs, not unrelated current files. Missing local accepted ref, missing/malformed reports, changed logs/bindings or stale contracts are visible unavailable/invalid evidence. Historical candidate evidence is explicitly historical relative to the inspected checkout; it cannot establish current completion. Inspection must not write completion files, advance refs, run tests or call acceptance. No new completion policy is introduced.

## Interactive UI

The workbench exposes connected Epic, Story, Scenario, Task, Test and Result/Evidence records without requiring one complete chain. Epic is the presentation of a defined intent, not a label automatically assigned to every Feature or workstream. A requested existing Story or Task opens directly with known surrounding purpose and relationships; a standalone item opens without invented ancestors. With no explicit subject, use recorded work context or the current branch's work; where those do not identify one subject, offer a clearly labeled chooser. No branch/task suffix is silently interpreted as a product Epic.

The primary surface combines contextual navigation and selected detail. At each entry, explain the promise relevant to that item before its delivery/evidence. Breadcrumbs identify the actual route and source rather than fabricate a single ownership path. A shared Task is reachable from each linked Story/Scenario, preserving one identity and status. Back preserves the initiating context; related links expose other contexts. Optional filters refine these same records. Missing links, models and purpose are named plainly. Sources, logs and technical evidence load on request; meaningful definitions are not hidden behind raw JSON.

Join real task graph metadata and reviewed task scopes with canonical scenario/test references and actual runtime task evidence. Each task has a meaningful outcome, dependencies, owned paths, scoped tests and completion evidence. Missing historical breakdown remains explicit. Declared task lifecycle, readiness, execution/integration and proved completion are distinct. Every summary count opens the corresponding records. Decisions show the question, options, context and known dependent work, with actor/rationale required for guarded resolution.

Inventory comes from local live refs and default-branch archive semantics, including works without a pilot Engineering Model. Distinguish checked-out branch, selected work and inspected source. Other branches/revisions are read through immutable committed snapshots without checkout/ref changes, with consistent model/test/source versions and original evidence authority. Historical and cross-branch browsing is read-only. Missing models, local authority or sources are visible limitations; there is no automatic migration.

The document layer remains the sole validator/admission/guard. Editable decisions exist only in the active checkout's admitted current work. Preserve the full originally displayed state identity across navigation/reruns; concurrent edits require explicit refresh, and stale/invalid submissions leave bytes unchanged. Historical browsing cannot publish or resolve decisions. Actual test outcomes are distinct from workstream verification, historical/stale applicability and missing evidence. Source is selected by full qualified test selector at its selected revision. Show actual failure output and recorded run time/duration where present. Technical details explain commit, contract, snapshot and run identifiers with useful copyable values and existing commands; raw JSON and hashes are collapsed initially.

Apply the pinned frontend-design skill and Streamlit references. Use a coherent theme, compact navigation, responsive list-detail layout, readable labels, keyboard focus and non-color status indicators. Initial Overview does not parse test source or scan evidence. Cache only identity-bound reads; refresh and integrity changes invalidate cached views, and mutations always recheck admission. Measure initial load and common interactions. Proposed pilot budgets and benchmark methodology are specified in the design; record actual misses and justify a technology amendment with evidence before replacing Streamlit. Core CLI remains independent of UI dependencies. Arbitrary source editing, production deployment and automatic test execution/acceptance remain outside scope.

## Work context and request entry

A workstream is an execution boundary, not an Epic/Story classification. An agent beginning adopted work uses explicit subject IDs/paths in the request, the referenced repository item or supplied tracker/later-card context, then any existing work-context association to establish the bounded subject. Discovery does not commit, create a branch, rewrite identity or invoke external tracker APIs. Repository branch identity locates execution artifacts but alone cannot determine product scope.

Present the inferred subject, known relationships, requested contribution and exclusions in readable language. If two candidate items conflict, a referenced item is missing, or the requested change exceeds the existing scope, name the conflict and ask a load-bearing question before admitting that work. Missing optional ancestors alone does not block work. Unavailable tracker context is explicitly unavailable; the user can supply it or choose a standalone scope without an invented parent. Existing repository identities are reused; a later card remains a proposal, not proof of a live Task or approved scope.

The confirmed intent records the subject's qualified identity or explicit standalone state, source reference, contribution and known supporting relationships. A context-only request to inspect an item is read-only and does not create engineering nodes, branches or task assignments. Writing associations uses the existing guarded definition path. This specifies behavior for the adopted model/workbench; changes to the general reusable Explore/Grill protocol for discovering omissions are separate later work.

## Definitions and source context

An Epic detail states intended user, outcome, motivation, scope and completion conditions. A Story states user outcome, purpose and acceptance conditions. Scenario detail gives concrete context/action/expected outcome from its selected canonical case; criterion references provide the broader obligation. Task detail states the work outcome, relevant Story/Scenario links, dependencies, plan entry and evidence limitations. Definitions use normal explanatory prose; title/ID/source-link-only displays do not meet these requirements.

Repository model definitions can carry context references to specification and plan passages. A passage reference identifies a safe repository-relative path plus a unique heading path or a stable plan-task selector. Capture the selected file bytes and selector with the validated snapshot; reject unsafe paths and malformed selectors at admission. Well-formed zero-match or multiple-match selectors are admitted unavailable context, explicitly labeled missing or ambiguous. Expose renamed passages as unavailable; never choose the first match. Do not silently substitute a similarly titled section or current-file text into an older revision. Relevant referenced files participate in snapshot freshness/dependency identity, including linked-text-only changes. Passage-reference fields and their diagnostics belong to the v2 document contract, not UI-only heuristics.

Selected details show the relevant specification passage and plan task/entry in context, with source path, section/task identity and inspected revision. Longer surrounding text is available on request. For an unplanned item, show that no plan entry is recorded; do not fabricate a plan or block ordinary inspection. Define multiple relevant passages when a Task genuinely spans them; clearly identify what each explains. The human must recover why this work exists and what it promises without reopening chat history.

## Readable tests and evidence

Test detail explains the linked Scenario and Task, concrete setup/input, action, expected observation and assertion. Expose actual selected test source at the inspected revision. Helpers, shared fixtures and globals remain permitted, but show the relevant same-revision definitions and explanatory comments needed to understand their role. A helper name, unexplained constant or source excerpt alone is insufficient when it hides the behavior being checked. Do not require a specific testing framework, Gherkin syntax, inline every helper, or create a second editable assertion authority.

Result detail states the actual recorded outcome, source/candidate/run applicability and retained failure/output context when available. Separate explanation of what the assertion checks from observations actually retained by the run; never infer expected inputs were observed just because a test passed. Missing helper source, execution logs or runtime records are explicit limitations. Narrative explanations cannot override accepted test obligations, declared links cannot establish execution, and current completion still uses existing authority.

Human readability requires a successful candidate-bound review exercise: from the chosen Task, the human identifies its purpose, relevant spec/plan passage, supported Scenario, setup/action/expected behavior, assertion and actual outcome/applicability without assistance from chat. Record the candidate/snapshot, selected Task/Scenario/Test and all displayed helper/source revisions, each identification and its pass/fail disposition. Any failed identification blocks the representative demonstration until corrected and reviewed again or explicitly escalated for a scope decision. Relevant source/context edits invalidate the review. Automated mapping/source checks complement this review and cannot substitute for it. Existing reviewer-only authority rules apply to any future review-only criterion.

## Representative Story and counterexamples

Proposed Story: “As the developer returning to my work, I can open a delivery Task and recover its behavioral promise and evidence so I can decide what remains to do.” This is newly authored modeling, not reconstructed historical planning.

Main flow: open an existing Task linked to this Story -> read the matching spec passage and plan entry -> open its concrete Scenario -> inspect a Test and necessary helper context -> inspect a real retained outcome and its applicability. The real pilot inspects preserved records from `structured-agentic-environment`; unavailable evidence is labeled unavailable and cannot pass the executed-result portion of the demonstration. Test-owned fixtures can exercise future behavior but are labeled fixtures and never presented as retained pilot delivery evidence.

Required counterexamples: start at an existing Story rather than Epic; start at a standalone Task with no parent; select a Scenario without a Story; reach one shared Task from two Stories/Scenarios and return to the original route; encounter two conflicting subject matches; inspect renamed/ambiguous spec passages; change only a linked plan/spec file; inspect a Test whose assertion depends on a helper/global; inspect historical or missing evidence. One representative Story bounds authored product coverage, not coverage of these relationship/entry rules.

The exact real selectors and preliminary availability assessment are below. A future reviewed plan must assign new work and test scopes; no old task or test-plan pin becomes a new execution assignment. This proposal does not certify a live pilot result.

## Observable acceptance

Canonical proposed Given/When/Then: adjacent JSON. EM-001–007 and EM-012 retain their existing obligations; EM-008–011 are amended and EM-013–018 are new. These proposed identities do not change accepted authority.

- EM-001: Valid models are accepted and duplicate/broken identities, illegal edges/cardinality/cycles, malformed fields and lifecycle conflicts produce precise nonmutating diagnostics
- EM-002: Through a pre/post-validated action, attributable history, revisions, blockers and transitive decision invalidation persist; invalid/stale changes cannot publish or overwrite the last stable state
- EM-003: Assertions, actual outcomes and revision provenance are inspected through existing authority; missing/invalid/historical evidence is honest and inspection writes nothing
- EM-004: Both projections retain identical IDs/digest and task/attention state, useful errors preserve data and CLI edits survive reload
- EM-005: UI displays canonical assertions/tests/revisions and honest evidence states, consuming the shared validated snapshot without duplicating domain-validation or repair rules
- EM-006: A valid choice persists and changes task attention; stale or invalid submissions reject without writes
- EM-007: Validate the current stable state before invoking the action and the complete resulting state afterward; failures or stale identities prevent publication Every spec change invalidates affected validation, including linked-spec-only edits; startup/action/read checks recover from missed external-save events Readers consume one validated generation, with content/dependency/rule-bound identity; incremental/cache behavior agrees with full validation and no broken or mixed state is actionable Each enumerated public state-changing entry point uses the same guard; successful execution records exactly one pre-check, action, post-check and publication in order against captured input/result identities
- EM-008: Known context and qualified identities are preserved without requiring a complete hierarchy; shared Tasks/Tests have one canonical identity and missing links are visible without fabricated containment Relevant purpose is explained before delivery/evidence; support relationships do not alter execution ownership or completion authority
- EM-009: An explicitly selected valid Story/Task opens directly; otherwise recorded context/current branch locates the work or a labeled chooser is shown; checkout, selected subject and inspected source remain distinct Committed cross-branch inspection reads one validated revision and its matching source/evidence without switching checkout, changing refs or enabling semantic edits; unavailable artifacts are explained
- EM-010: Tasks expose readable outcomes, dependencies, supporting Story/Scenario links, same-revision specification passages and plan entries, scoped tests and recorded evidence, with absent context explicitly unavailable Every summary count opens its exact records as a filter of the same hierarchy; blockers name their cause and decisions show available choices and guarded resolution No missing history or declared done lifecycle is promoted to verified completion
- EM-011: Source is syntax highlighted and corresponds to the selected qualified test and revision; results match work, test, run and contract identities Passed, failed, not run, unavailable, stale, historical, skipped and runtime-error states preserve actual meaning; missing time and duration are explicit Debug identifiers remain collapsed initially and have explanations, copyable values and usable artifact links or commands; execution pass remains distinct from incomplete verification history Readable setup/action/expected behavior and relevant same-revision helper/global definitions explain the assertion; narrative expected behavior remains distinct from actual retained observations
- EM-012: Responsive list-detail navigation, accessible labels/focus/contrast and non-color status text allow the primary inspection and decision journeys Initial Overview performs no test-source or evidence scan; selected detail loads lazily and cache refresh or changed inputs cannot hide stale or tampered evidence Pilot latency budgets are measured with documented samples and misses; a technology replacement requires observed limitations and a reviewed amendment
- EM-013: Reuse known identity and state the bounded contribution/exclusions without creating an Epic or inventing ancestors Material missing/conflicting scope is surfaced before work admission; unavailable external context does not silently become a known local item
- EM-014: V2 accepts missing parents and the specified support edges while rejecting duplicate identities, illegal/multiple containment parents, broken links and cycles V1 remains interpreted under its original version; migration preserves identities/evidence and requires explicit reviewed adoption without automatic browsing writes
- EM-015: Show the selected same-revision passages with source identity, or explicit missing/ambiguous context; do not silently substitute another passage Referenced text participates in snapshot identity and linked-only changes invalidate freshness; inspection remains read-only
- EM-016: Expose readable setup, action, expected behavior and assertion with necessary helper/global context at the selected revision Actual recorded results and applicability are inspectable; at least one genuine retained result must pass integrity/applicability checks for the complete real demonstration; missing evidence is explicitly incomplete and fixture runs are not mislabeled as pilot evidence
- EM-017: The older harness is absent from the main pilot presentation while original records/evidence and explicit historical inspection are preserved
- EM-018: Repository inspection does not require a third-party service or duplicate editable backlog; source revision governs engineering context Unavailable tracker information is labeled and no automatic API integration, synchronization or authority transfer occurs

## E2E

Applies. Guard journey verifies pre-validation → action → post-validation → publication and failure isolation, including external/linked spec edits. CLI journey, UI integration via Streamlit AppTest and real temporary browser E2E cover scenario inspection, persisted decision→unblock→reload and stale-form protection. Broken-document cases belong to document admission/validator tests, not UI business logic. Browser/server and data are test-owned, local, reset by teardown; never mutate the committed pilot from tests. Required types/cases are in the independently challenged test plan. Full repository Verify and candidate-bound independent semantic review remain mandatory after implementation. Planning checks establish contract consistency only, not feature behavior or comparative usability/productivity.


The amendment additionally requires the representative Task-entry journey,
Story-entry and standalone/missing-parent cases, shared-Task identity/navigation,
ambiguous request resolution, exact spec/plan passage selection and linked-only
freshness, helper/global readability context, and preservation of historical
harness data outside the main pilot. Use isolated temporary repository/model/
spec/plan fixtures and browser/server processes owned by tests, removed during
teardown. Never modify committed pilot/evidence to manufacture a passing case.
The human readability exercise is recorded alongside automated checks, with
existing authority for review-only criteria retained. Required test types and
case mappings need independent review in a future plan; no plan or behavior
execution is performed in this specification/challenge-only session.

## Concrete resolutions of the previous challenge

### F1: Flow authority and test association

A Scenario's concrete flow is selected by `(source work_id, test-plan digest,
case id)` and reads the canonical case's `scenario` Given/When/Then. Model
descriptions can explain it but cannot override it. Distinct flows sharing one
criterion use distinct case selectors. A test proves that flow only through an
explicit `covers` link consistent with the selected case. Criterion overlap
alone is labeled related obligation and creates neither flow coverage nor proof.
Reject contradictory active case/coverage references. An unplanned flow remains
draft with an explicit missing-case limitation until a reviewed case exists.
Counterexample: successful publication and stale rejection both concern EM-007;
the success test must not appear as proving the stale-rejection flow.

### F2: Passage classification and action admission

Unsafe/escaping/symlink targets and malformed selector shapes invalidate document
admission. Missing optional references, safe missing files, well-formed zero
matches and multiple matches are admitted context limitations, not structural
corruption. They never silently resolve to an alternative passage. Capture
existing target bytes and selector plus absence/match state in snapshot identity;
creation, deletion, rename or changed match count invalidates freshness.

A safe unresolved context reference alone does not block unrelated guarded
actions. An action requiring that passage to establish its contract refuses
admission until it resolves uniquely; incomplete representative context blocks
the demonstration. Invalid current documents permit only read-only diagnostic
inspection of raw untrusted input and a labeled last-validated snapshot. Their
ordinary mutations/workflow actions stay blocked; repair/import is explicit.
Exercise inspection and action admission against each classification, including
missing-to-present and unique-to-ambiguous transitions.

### F3: Owning request-entry caller

The adopted workflow's agent/coordinator intake calls the shared context resolver
before branch creation, recording intent or admitting delivery. Expose the same
read-only resolution through proposed `./ask model context` for inspectable
evidence; a resolver unit test alone cannot verify coordinator invocation.
Explicit request subject wins over a prior recorded association. A referenced
repository/later/supplied tracker item resolves that explicit subject; conflicting
explicit identities stop for clarification. Then use a recorded subject if valid.
The branch locates execution records and never invents a product subject. If none
is known, present standalone scope or a chooser. An explicit subject differing
from the branch is shown with the bounded contribution and execution owner;
clarify ownership conflict before writes. Inspection-only entry returns context
without branches, intent writes or assignments. Test actual coordinator intake in
a fresh context with no association, an explicit override and conflicting items.

### F4: Identity and status authority

Repository product identity is `(owning model work_id, node_id)`. An execution
Task is separately `(execution work_id, task_id)`; later-card paths and supplied
tracker identifiers are references to resolve, never implicit equality joins.
Within one model, at most one Task node aliases a given execution Task. Duplicate
aliases reject. Definition lifecycle expresses modeling state; execution state,
integration and verification are projected from their existing authorities and
are displayed separately, never overwritten by lifecycle. Support edges are
local to one model for this version. A foreign product resolves to its owning
revision for read-only navigation; no cloned local alias or cross-model support
edge is created. Missing/conflicting targets require visible resolution; no
cross-workstream writes or tracker API integration is implied.

### F5: Required real example and retained evidence

Select historical execution Task `(structured-agentic-environment, WB-003)`.
Its canonical plan entry is table row WB-003 under `Work breakdown` in
`work/structured-agentic-environment/plan.md` (resolve by task ID, not title).
Its relevant main-spec passages are `Projections and evidence` and `Interactive
UI` in `specs/current/structured-agentic-environment.md`, bound to the inspected
revision. Concrete flow: canonical case `WB-evidence-identity` in that work's
`test-plan.json`; test selector
`test_engineering_workbench_evidence.WorkbenchTests.test_results_match_work_test_run_and_contract`
in `_ask/tests/test_engineering_workbench_evidence.py`.

Retained task record:
`work/structured-agentic-environment/inner-loop/results/WB-003.json`.
Candidate: `70dd295aacff869857081a94870d02fcbf4d640c`.
Red run: `111e0f24d5e448c387cd1558b864b18e`;
final-green run: `799924ec199b4717a3eabf4fb39a1bdc`.
Both declared output log paths exist in the original local checkout. These
ignored local runtime artifacts are not copied into the new Git workstream;
the isolated clone can therefore display unavailable evidence. The committed
record contains output excerpts, which are not substitutes for missing required
run/authority artifacts. Full report/log digests and accepted applicability must
be evaluated through the existing read-only evidence authority before claiming
the demonstration succeeds. Require at least one genuine retained result, not
only fixture outcomes. If local authority/artifacts cannot establish it, report
the exact prerequisite as blocked; do not weaken the criterion automatically.

### F6: Successful readability disposition

For the selected candidate, the returning human must correctly identify purpose,
spec/plan context, concrete flow, setup, action, expected observation, assertion,
actual retained outcome and applicability. Store each result with candidate and
snapshot identity and selected test/helper/global source revisions. An unresolved
comprehension failure blocks demonstration completion. Changes to relevant
definitions, selected source, fixtures/helpers or evidence invalidate this review.
Curated explicit helper references are permitted; a whole-program analyzer is
not required. Automation remains required, and this specification grants no
review-only authority or independent approval.
