# Plan: connected Engineering Workbench

## Status and authority

PLANNING ONLY. Continue `structured-agentic-environment` on `agent/structured-agentic-environment`. Stop after exact-contract independent review and pinning so the human can switch to Luna. Do not implement, run an inner-loop writer, initialize task execution, merge, push or claim feature completion in this turn.

Design authority is the latest ten-part human brief plus the clarification requiring one hierarchy. Earlier tabular navigation choices do not constrain this plan. Existing code and evidence are the baseline for reuse and truthful status, not product-design authority. The original intent confirmation is preserved; this user-directed scope amendment is recorded in `spec-change-workbench-redesign.md`.

## Specification

Exactly one current specification: `specs/current/structured-agentic-environment.md`, canonical criteria in adjacent JSON revision 3. EM-001–007 retain foundational behavior; EM-008–012 cover the current UI request. `workbench-design.md` defines the interaction details and wireframes without introducing another criterion authority. Independent review binds the exact spec, test plan, task graph and planning source revision.

## Approach

Build one connected **Epic → Story → Scenario → Task → Test → Result / Evidence** navigator with a selected detail panel. The epic root is its overview. Story/scenario/task/test/result are navigation levels with persistent ancestor context, not separate primary tabs. A record can be related from multiple contexts without acquiring a false exclusive parent. Optional task/test/status filters refine this same hierarchy. Generic Objects inspection moves into advanced details; evidence belongs beside its matching result.

Reuse the Engineering Model validator, immutable snapshot/admission, semantic guard and read-only traceability inspector. Add small read/projection adapters for actual task graphs, ref inventory, revision-correct source and selected result detail. The UI owns presentation and route state only. Keep domain rules and completion authority in their existing modules.

Use real task graph + test scopes + actual task state/results, not the pilot's lone blocked future-work task as a complete work history. New tasks begin planned with no claimed completion evidence. Missing historical breakdown, story records, task-test mappings and run metadata remain explicit. A test pass is distinct from complete workstream verification.

Retain Streamlit for this implementation. The measured small-pilot baseline supports reducing eager source/evidence work before replacing the framework. See `performance-baseline.md` for samples, limitations and the migration trigger. The pinned frontend-design skill and installed version-matched Streamlit references guide hierarchy, theme, layout, accessibility and lazy work.

## Work breakdown

All tasks below are planned future implementation outcomes. They are not reconstructed historical tasks or already completed work. Exact IDs, dependencies, owned paths and case assignments match `inner-loop/tasks.yaml` and `test-plan.json.task_scopes`. Every case has exactly one responsible task; tests may still verify several scenarios/criteria. A secondary task link is explicitly labeled scenario-mediated coverage and never changes execution ownership or task completion.

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| WB-001 | Join epic, canonical scenarios, task graph and reviewed test scopes without inventing task history | None | `_ask/scripts/engineering_model/workbench.py`<br>`_ask/scripts/engineering_model/projection.py`<br>`_ask/tests/test_engineering_workbench.py` | WB-relations, WB-task-history, WB-story-context, MV-valid, MV-graph, MV-fields, MV-refs, ME-decision, ME-revise, ME-reject, ME-race, EV-real, EV-missing, MP-shared, MC-journey, DG-pre, DG-post, DG-refs, DG-events, DG-parity, DG-publish, DG-bootstrap, ME-batch, DG-success, DG-entrypoints | Projection fixtures preserve relationship identity, task provenance and missing-history states; unchanged foundation regression suite remains executable |
| WB-002 | Discover live and archived work and read one consistent branch revision without changing checkout | WB-001 | `_ask/scripts/engineering_model/workbench_sources.py`<br>`_ask/tests/test_engineering_workbench_sources.py` | WB-inventory, WB-snapshot, WB-source-errors | Disposable Git refs show correct default work, archived/missing-model inventory, immutable source selection and unchanged HEAD/refs/model bytes |
| WB-003 | Present qualified source and actual retained execution with version and integrity-aware identity | WB-002 | `_ask/scripts/engineering_model/workbench_evidence.py`<br>`_ask/tests/test_engineering_workbench_evidence.py` | WB-evidence-identity, WB-source-version, WB-evidence-states | Adversarial identity, version, missing-data and tampered-log fixtures preserve evaluator authority and actual case outcomes |
| WB-004 | Keep one Epic to Story to Scenario to Task to Test to Result navigator, source context and captured edit identity stable across navigation | WB-003 | `_ask/ui/streamlit_app.py`<br>`_ask/ui/workbench_context.py`<br>`_ask/ui/workbench_navigation.py`<br>`_ask/ui/.streamlit/config.toml`<br>`_ask/tests/test_engineering_workbench_navigation.py` | WB-navigation, WB-form-context | AppTest exercises current work default, source badges, routes, Back/refresh, missing inputs and captured-form identity |
| WB-005 | Explain purpose, stories, scenarios, status and attention inside the connected hierarchy | WB-004 | `_ask/ui/workbench_overview.py`<br>`_ask/ui/workbench_scenarios.py`<br>`_ask/ui/workbench_stories.py`<br>`_ask/tests/test_engineering_workbench_overview.py` | WB-overview, WB-summary-links | Overview and scenario AppTest assertions prove readable relationships, count navigation and zero eager evidence/source work |
| WB-006 | Provide a task list-detail view with related scenarios, tests, blockers and implementation evidence | WB-005 | `_ask/ui/workbench_tasks.py`<br>`_ask/tests/test_engineering_workbench_tasks.py` | WB-task-detail, WB-completed-tasks | Task status/search filters and detail links retain completed work and distinguish lifecycle from verified completion |
| WB-007 | Open each attention record and persist attributed choices through the existing guard | WB-006 | `_ask/ui/workbench_attention.py`<br>`_ask/tests/test_engineering_workbench_attention.py` | WB-attention, WB-decision-choice | Attention links, option context, rejection without writes and new-session resolution consequences are verified |
| WB-008 | Expose selected test source, execution history and actionable technical provenance | WB-007 | `_ask/ui/workbench_tests.py`<br>`_ask/ui/workbench_debug.py`<br>`_ask/tests/test_engineering_workbench_tests.py` | WB-test-panel, WB-debug | Selected test/result/source journeys and collapsed debug copy/command behavior match their exact underlying identities |
| WB-009 | Measure and finish the redesigned experience in a real browser without weakening existing verification | WB-008 | `_ask/tests/test_engineering_ui.py`<br>`_ask/tests/test_engineering_ui_browser.py`<br>`_ask/tests/test_engineering_workbench_browser.py`<br>`_ask/tests/test_engineering_workbench_performance.py`<br>`_ask/ui/benchmark_workbench.py`<br>`_ask/ui/requirements-test.txt`<br>`work/structured-agentic-environment/workbench-validation.md` | WB-browser-journey, WB-browser-accessibility, WB-performance, WB-latency-budget, UI-inspect, UI-persist, UI-conflict, UI-browser, UI-empty, UI-gitless, UI-decision-object, UI-overview-results, UI-overview-hierarchy, UI-test-source, UI-expander-ids, UI-browser-gitless | Browser screenshots from real work, isolated end-to-end fixtures, keyboard/narrow-layout evidence, measured budgets and honest full verification outcome |

Execution order is WB-001 → WB-002 → WB-003 → WB-004 → WB-005 → WB-006 → WB-007 → WB-008 → WB-009. Shared existing UI regression tests are adapted in WB-009, after the selected detail renderers exist. Other tasks use separate test modules, keeping source ownership clear. One writer and one workstream branch; no parallel related branches.

WB-001 carries the unchanged model/guard/CLI/evidence suite as regression protection for the new read projection; this does not assign it historical authorship. WB-009 carries the existing UI/browser journeys plus the final browser/performance cases. Existing test IDs and change classifications are retained, except an explicit expected-assertion amendment for lazy overview source; no existing new case is relabeled regression to conceal missing red evidence. Future assertion/selector changes require continuity review.

## Dependencies and affected components

- Shared model/projection: `_ask/scripts/engineering_model/`; add workbench relationship/source/evidence adapters. No new node type is required for Epic and no schema invention is required for absent stories.
- Branch inventory: reuse the semantics of `./ask status --json`, local refs and archive lookup; selected-source blob reads must retain original Git/evidence authority and validation semantics.
- Task history: read the accepted graph/scopes and existing runtime task results without generating them. Status dimensions stay distinct.
- UI: current `_ask/ui/streamlit_app.py` becomes the thin shell; detail modules are owned per task. Native theme lives in `_ask/ui/.streamlit/config.toml` and must not unintentionally change the unrelated training-run viewer.
- Dependencies: current pins are Streamlit 1.59.2 and Playwright 1.63.0. Core CLI stays stdlib-only; no React/build/API infrastructure is introduced by this plan.
- Design skill: `anthropics/skills` frontend-design pinned to `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f` in the manifest. The skill was read from that exact revision outside the repo; never vendor its tree. Streamlit local references were discovered from the installed package.

## Observable acceptance and verification

The hierarchy and selected detail must be usable from the epic root through story/scenario/task/test to an actual result and its evidence. Back and related links preserve context. Missing story/task mappings are visible. The current branch work is the default; foreign committed source is read-only and leaves checkout/refs/files unchanged. Every count leads to its exact records. Completed tasks remain discoverable with their actual tests and results.

Source selection uses full qualified test identity at the selected revision. Result attachment retains work/test/run/contract identity. Availability, execution outcome, currency and workstream-verification status remain separate. Missing timestamps/durations are unavailable, not invented. Debug values are collapsed, explained and copyable with valid source/log/review links or existing commands.

UI checks cover accessible labels, visible keyboard focus, non-color state text, rendered normal-text contrast ≥4.5:1, large-text contrast ≥3:1, focus-indicator contrast ≥3:1 against adjacent colors, and 390/1440px layouts. Initial overview must perform zero evidence inspections and zero test-source reads. Only selected source/detail loads. Integrity-aware caches invalidate on underlying definition, source, accepted authority or evidence/log changes; edits always recheck the guard.

Proposed same-machine pilot budgets: 20 samples for warm new-session overview p95 ≤1.5s, metadata navigation/filter p95 ≤500ms and selected source/result p95 ≤1s; five process restarts for cold start-to-usable ≤4s. These are new acceptance targets, not measured successes. Repeat structural workloads at 100/1,000 tasks with recorded graph/test/file sizes; disclose larger-fixture timing rather than invent an SLA. Do not reduce correctness checks to hit budgets.

WB-latency-budget explicitly enforces the sampling protocol and numerical budget comparisons with content-specific readiness markers and candidate-bound raw results. WB-browser-accessibility exercises the rendered interface rather than only checking theme constants.

Before implementation: validate graph, exact task/case coverage and canonical contract consistency, commit planning source, independently challenge it, address findings, and pin approved contracts through `./ask traceability accept-plan`. A plan pin approves obligations, not application behavior or verification history. Preserve prior accepted authority through Git/ref object history and the archived review/evidence records.

For each implementation task: commit meaningful failing behavior assertions before production changes, capture genuine assertion-red through the accepted runner/task scope, implement the bounded outcome, run relevant checks, independently review continuity/candidate, and commit the completed slice with actual task evidence. Do not treat missing future methods/import errors as behavioral red. The existing unittest adapter discovers the engineering suite, then filters to the exact accepted case IDs for task scope. Preserve that supported binding. All discovered modules must still import cleanly because discovery errors invalidate the run; add each task's future test module only when starting that task, and obtain behavioral red through assertions rather than missing imports/selectors. Any necessary runner-binding change requires independent review and a new pin before use.

After WB-009: run all mapped cases and browser journeys in the pinned environment, independently review the candidate, run `./ask verify`, acceptance checks and candidate-bound result recording. Full verify/result pass requires the repository's genuine evidence requirements. Retain the prior 34-case passing run as historical execution, and the missing red-phase history as a separate unresolved verification gap; this plan cannot certify or fabricate its repair. Record partial if required evidence remains missing.

## E2E

Applies under EM-005/006 and EM-008–012. Use Streamlit AppTest for admitted state and detail interactions, and real Playwright Chromium for explicit epic → recorded story → scenario → task → test → result/evidence navigation, keyboard/narrow layouts, selected source/results, cross-branch browsing, attributed decision persistence in a second session, stale linked-spec rejection, and refresh recovery.

Build disposable Git/JSON repositories with actual scoped tasks and captured execution evidence, a many-to-many test, incomplete records, two branches and historical source. Keep the real committed pilot untouched by tests. Test-owned temporary servers, browsers and repositories are removed in teardown; no checkout/ref mutation is allowed during browsing. Final screenshots use real workstream data and label any missing legacy history.

## Risks, escalation and spec-change triggers

- Historical work cannot be reconstructed from the pilot node graph alone. Render authoritative available artifacts and gaps; do not fabricate a comprehensive history.
- Ref-only inspection can accidentally validate one revision and display another source/evidence. Resolve one immutable commit; retain original authority; test moved refs and duplicate test IDs adversarially.
- Caching can conceal modified evidence or stale decision identities. Content-bound invalidation and guarded edits take priority over latency.
- Native Streamlit controls may limit outline density, responsiveness or accessible context. First implement a bounded drill-down/outline using native controls; a narrowly scoped component requires an observed unmet requirement. Framework migration requires measured repeated budget misses or demonstrable interaction limitations and an independently reviewed amendment.
- New domain relationships, completion-policy changes, automatic historical migration, or edits from a foreign snapshot require Spec Change. Changes to What/Why cannot be hidden inside a UI adapter.
- Any unmet prerequisite or missing review is explicit handoff state. No repeated permission questions are required for the user-authorized planning scope.

## Out of scope

Production hosting/authentication, an IDE/source editor, automatic test execution or acceptance, changing completion authority, training-run viewer redesign, inventing missing history, starting another workstream, and merging/pushing during this planning turn.

## Handoff and stopping condition

Independent review and accepted contract identity are recorded in `workbench-plan-review.md` and `traceability/workbench-plan-review.json`; coordinator pinning updates `traceability-accepted.json`. Planning checks and final source SHA belong in `planning-validation.md`.

Stop after those artifacts are committed and the reviewed contract is pinned. Application files remain untouched. The human will switch to Luna and explicitly say `continue` before WB-001 starts. At that point honor the user's model choice over the historical 06-implement model override, update model metadata if needed, and recheck clean worktree/current contract before executing.
