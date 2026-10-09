# Engineering Workbench interaction design

## Job and opening experience

The developer opens this tool to understand delivery and inspect proof: what the epic promises, how its stories and scenarios fit together, what tasks implement them, which tests verify those tasks, and what happened in the actual runs. The epic's meaningful name and purpose lead the page. Technical identifiers support inspection rather than dominate it.

The existing real pilot contains twelve model nodes, two linked scenarios and one explicitly future-work task blocked by a decision. It is a demonstration, not a complete record of delivered engineering work. The new projection must also read the current task graph and test scopes. It must label missing historical breakdown instead of inferring past completion from a file or green test.

## One hierarchy, one selected detail

Primary navigation is one connected structure:

**Epic → Story → Scenario → Task → Test → Result / Evidence**

There are no peer tabs named Overview, Objects, Scenarios and Evidence. The epic root is its overview. Selecting a story, scenario, task, test or execution opens that node's appropriate detail surface while retaining the hierarchy, breadcrumb and parent context. Evidence appears alongside the execution/result it supports. An advanced generic record inspector is optional secondary technical detail.

A test can verify multiple tasks or scenarios. Show one canonical record with links from all relevant contexts; a navigation path is not a new exclusive ownership relationship. Where stories have not been recorded, explain that gap and expose the existing scenarios directly under an explicitly labeled grouping. Do not create fictional stories or force illegal model containment edges.

The work/source switcher is app-level navigation, separate from the selected epic outline. Default to the work matching the current `agent/<work-id>` branch; recognize task-branch suffixes through inventory. Detached or non-work branches get a clearly labeled chooser, not an arbitrary work advertised as current. A gitless configured root offers its available local models with explicit Git/evidence limitations.

Header: selected epic name, purpose, checked-out branch and inspected source, document/evidence currency, and Refresh. A document-valid indicator does not imply verified work.

| Selected level | Detail content | Child/related navigation |
| --- | --- | --- |
| Epic root | Purpose, recorded stories, scenario summaries, task progress, known results and contextual attention | Open story/scenario; click a count to filter this hierarchy |
| Story | Recorded intent/description, related scenarios and their delivery state | Open scenario; return to epic |
| Scenario | Canonical Given/When/Then, related tasks and verifying tests | Open task/test; retain story and epic context |
| Task | Outcome, status dimensions, dependencies/blockers, implementation evidence and related tests | Open test or prerequisite; retain scenario context |
| Test | Verified behavior, qualified source and all related scenarios/tasks | Choose its execution/result; load selected source only |
| Result / evidence | Actual outcome, failure output, recorded run metadata, source applicability and supporting evidence | Return to test/task; inspect other runs or technical provenance |
| Attention record | Blocker, unresolved decision, failed/stale evidence or missing mapping | Focus its originating node; resolve an editable decision in context |

Search and status filters refine the same hierarchy. Optional All tasks or All tests shortcuts open filtered record lists with a path back to their epic/scenario, not a different information architecture. Attention is a contextual queue/drawer or focused detail, not a competing primary page. Route state holds source identity, selected canonical record, ancestor path, filters and optional execution; Back restores context.

Overview shows counts available from admitted metadata. Execution counts initially say `Not loaded`, not zero or passed. `Load results` updates summaries without executing tests. Result loading and source expansion are independent. If a filter excludes the selected item, show that fact and a clear-filter action; do not silently select another item.

## Representative layouts

These are proposed wireframes, not delivered UI. N is a placeholder for actual computed counts.

```text
+--------------------------+------------------------------------------------------+
| Work [current work v]    | Engineering Model and local workbench                |
| Checkout: agent/...      | Make decisions, implementation and proof inspectable |
| Viewing: working files   | Documents valid  Results not loaded [Refresh]        |
|                          |                                                      |
| [Search within work]     | Scenarios N  Tasks N  Blocked N  Open decisions N    |
| Filter [All statuses v]  | [each opens its exact records in this hierarchy]     |
|                          |                                                      |
| v Epic                   | Recorded stories and scenarios                       |
|   v Story                | [Named story / scenario summary]                     |
|     v Scenario           | Planned / Active / Blocked / Done                    |
|       > Task             | Tests: not loaded [Load results]                     |
|         > Test           |                                                      |
|           Result         | Needs attention                                      |
|                          | [Blocker and reason] [Decision and action]           |
| [Other work / snapshot]  | [Missing mapping / verification history gap]         |
+--------------------------+------------------------------------------------------+
```

```text
Epic / Story / Scenario / Selected task              [Back to scenario]
+--------------------------+------------------------------------------------------+
| Same work hierarchy      | Task title                                           |
| Scenario                 | Outcome and description                              |
|   Task: planned          | Declared: planned  Readiness: blocked                 |
|   Task: selected         | Evidence: not loaded / current / stale / missing      |
|     Test                 |                                                      |
|   Task: done             | Related scenarios [named links]                      |
|                          | Dependencies [task/decision] + exact reason           |
| Filter [All / Done ...]  | Tests [name] [type] [actual result]                   |
|                          | Implementation [recorded file/symbol or unavailable] |
+--------------------------+------------------------------------------------------+
```

```text
Epic / Story / Scenario / Task / Test / Run           [Back to test]
Same hierarchy stays visible; selected result is highlighted.

Test title                         Behavior being verified
Related scenarios [names]          Related tasks [names]
[View source]                      Actual outcome and failure assertion/output
Qualified source at chosen version Recorded run time/duration or unavailable
Syntax-highlighted relevant code   Current / historical / stale applicability
                                   Supporting evidence for this execution
                                   Workstream verification: separate verdict
[Technical details: collapsed]     [Other recorded runs]
```

Use approximately 1:2 outline-to-detail proportions on desktop. At narrow widths collapse the outline into a labeled work-navigation control above the detail and retain breadcrumbs/Back. At 390px there is no page-level horizontal overflow; code may scroll inside its own region. Expand only the active ancestry and immediate children, with pagination/search for wide sibling sets. Avoid recursively rendering all tests and results or stacking deep expanders.

## Relationships and data authority

| Displayed fact | Authority / join | Absent or conflicting data |
| --- | --- | --- |
| Epic | Admitted intent node and feature/containment hierarchy; Epic is a presentation label, not a new node type | Work title fallback labeled as metadata; missing purpose stated |
| Story | Existing story node and legal containment relationships | Missing story membership is disclosed; no synthetic story is presented as recorded |
| Scenario | Model reference to canonical criterion JSON, read from the chosen validated input set | Show unavailable behavior and its source; do not derive Given/When/Then from prose |
| Planned task | `inner-loop/tasks.yaml` stable ID, title, outcome, dependency and ownership metadata; retain separately identified model-only pilot tasks | Task not recorded, legacy breakdown incomplete, or orphan mapping shown explicitly |
| Task status | Actual runner state/result for that task ID and candidate; model lifecycle/readiness for model-only tasks | No runtime evidence means planned/not recorded; dependency readiness is not completion |
| Task → owned test | Exact accepted `test-plan.json.task_scopes` with task/work identity defines executable responsibility; exactly one responsible task per case in this plan | Never join IDs across workstreams; expose missing scope |
| Task → related scenario test | Recorded task/scenario association (explicit implementation links or its owned tests' criterion membership), then that scenario's canonical tests; labeled `Other tests covering this task's scenarios` | This is a scenario-mediated display association, not a second executable owner or proof of task completion |
| Scenario → task | Explicit model relations when present; otherwise criterion membership of the task's scoped tests, labeled `via test mapping` | Do not invent a containment edge or infer relevance from sibling nodes |
| Scenario → test | Canonical test criterion IDs and model `covers` references | Deduplicate by work + test identity; preserve all scenario memberships |
| Implementation | `implements` references and actual task completion evidence/owned changed files | Ownership is planned scope, not proof that a file changed |
| Test result | Shared read-only traceability inspector and integrity-bound retained run records | Incomplete global evaluation does not erase a recorded case outcome; label completion gap separately |
| Test source | Exact qualified selector and version from selected run/candidate or explicitly current checkout | Never display current source as historical source; unavailable version gets a reason |

For example, task A owns test X covering scenarios S1 and S2; task B owns test Y covering S2. X appears as task A's owned test and as a scenario-related test in task B, with its relation labeled through S2. Task B's scoped result does not automatically inherit X. A separate explicit recorded implementation association can also establish task → scenario; sibling placement alone cannot.

A test may cover multiple scenarios and be visible from multiple task contexts. It is counted once per filtered result set. Completion evidence includes candidate, run, test identity, plan binding and integrity state. All joins retain their source/provenance internally. The UI does not implement graph validation, change verdict policy, or repair documents.

Task status has distinct dimensions: declared lifecycle, dependency readiness, recorded execution/integration, and evidence currency. A declared `done` task with stale tests remains discoverable under Done, with its stale evidence visible. An integrated task can still lack accepted workstream verification. Neither becomes an unconditional “verified” badge.

## Branch and snapshot browsing

Reuse the inventory semantics of `./ask status --json`: unmerged local `agent/*` refs are live; default-branch work directories without live refs are archived; `.later` cards are parked, not live. Inventory includes works lacking an Engineering Model and explains which artifacts can be inspected. Do not hide every work that lacks the pilot JSON.

Resolve a selected ref once to an immutable commit and read its blobs/reference closure without checking it out or creating another work branch. Keep the original Git/evidence root for accepted refs and runtime artifacts. A temporary materialization, if required for the existing validator, is disposable and read-only for semantic actions; it never replaces original evidence authority or publishes a live admission pointer. Skip unsafe paths/symlinks with diagnostics, using the existing shared validation/path policy.

For another branch or historical commit: read its model, task graph, test plan and source from that same revision; evaluate retained evidence against that candidate using the original inspector. Default to read-only. Show `Viewing committed snapshot from …` in the main header. It cannot establish completion of the checked-out implementation. Missing refs/blobs/model or accepted registration get honest states. Refresh may move to a new tip only explicitly, then clears incompatible selections and caches.

The working checkout source is the only editable mode. Preserve the displayed admission identity while navigating and composing decisions. Detect external changes; show Refresh needed and keep old forms bound to the captured identity. Submission always rechecks the shared guard. Selection must never silently refresh an old form into authorization to edit new data.

## Attention and decisions

Summary links carry a route plus stable IDs/filter parameters. Blocked opens Tasks filtered to blocked; Open decisions focuses the attention queue filtered to open decisions; Failed tests opens the matching test result set. Back preserves the story/scenario/task context. Unknown result counts open an explanation/Load results action rather than claiming zero failures.

Blocker details name the prerequisite and actual reason. Decision detail shows the question/title, description, all option labels, recorded consequences, dependent tasks and previous choices/history. Do not invent consequences absent from records. Editable forms use explicit choices, actor and rationale; incomplete submissions leave bytes unchanged. A submitted choice persists and updates affected tasks after a successful guarded action. Historical/read-only forms explain the restriction and link back to current work.

## Test results, source and debug

Keep outcome, availability and currency distinct. `Not loaded` means not fetched. `Not run` requires a valid known inventory with no execution. `Unavailable` means absence or unreadable/unverifiable evidence. `Failed` is an actual behavior result. `Stale` and `Historical` describe applicability; they can accompany a recorded pass/fail. Runtime errors and skips keep their actual labels rather than being translated into behavior failures or passes.

A result detail shows the matching work, qualified test, execution/run, source version and validity. Missing timestamps/duration are explicitly unavailable; never derive a test duration from a whole-suite wall clock. A passing case with missing red-phase history reads `Execution passed; required verification history incomplete`, not work complete. Preserve previous runs read-only.

Source extraction resolves the full module/class/method selector, including same-named methods in different classes; support function/class display where applicable. Parse only selected source, cache by content identity, and show surrounding helpers only on request. Source references must remain inside the selected repository/snapshot.

Technical details use one shallow, lazy expander with unique stable keys. Explain candidate commit (source revision; `git show`), plan/spec digest (contract fingerprint; corresponding artifact and evaluator command), snapshot digest (captured document inputs; refresh/edit freshness), run identity (execution record/logs), and review identity (review artifact). Include copyable values, exact existing command examples and safe links. Do not turn digests into nonexistent Git objects. Raw JSON is optional and collapsed. Copy actions must not rerun evidence evaluation.

## Visual direction and accessibility

Use the evidence chain as the recognizable visual structure: readable relationship breadcrumbs and a consistent list-detail inspection surface. Content determines grouping. Revise the previous proposal's large nested card dump into a connected outline with compact sibling lists and one selected detail; avoid five nested borders and an enormous code-heavy Overview.

Palette: canvas `#F6F8FC`, surface `#FFFFFF`, text `#16243A`, secondary text `#526178`, action `#1D4ED8`, border `#DCE3EE`. Add semantic success/warning/error tokens with accessible foregrounds; each includes a written state and icon. Dark mode is outside this bounded pass unless the existing theme already supplies it.

Use a local system sans-serif stack for labels/body, 14–16px body, 20–24px section headings and 28–32px work title; use a monospace stack only for code/technical values. No external font request on startup. Use 4/8/12/16/24/32px spacing, readable text measures, a quiet sidebar, and consistent focus/selection. Native Streamlit theme and layout are first choice. Scoped CSS/custom components only if an observed accessibility/layout requirement cannot be met natively; record the specific need and avoid global internal-selector hacks.

Keyboard users can select work, navigate records, apply filters, inspect source, copy technical values and complete decisions. Use visible labels, focus indicators, normal text contrast ≥4.5:1, large text ≥3:1, and focus indicator contrast ≥3:1 against adjacent colors, and status text independent of color. Skeletons name what is loading; empty states explain absent records; errors identify the source and available recovery action. Avoid unprompted motion and respect reduced motion.

## Performance decision

See `performance-baseline.md` and raw measurement JSON. Retain Streamlit for the first implementation because shared validation is about 15ms median and the evidence-free projection about 1.3ms on this small pilot; observed browser overhead and eager source/evidence work are the first targets. This is a bounded recommendation, not a claim that Streamlit will scale indefinitely.

Keep definitions/relationships cached by captured content identity. Load selected test source and per-work evidence only when requested. Cache evidence using candidate, accepted-contract ref, review/execution/log content identities and validation rules; a TTL or candidate SHA alone cannot hide tampered or newly written evidence. Mutations bypass cache and recheck the guard. Refresh clears/revalidates all affected state. Use conditional page rendering and fragments only where they preserve captured-form semantics.

Proposed local acceptance budgets, to be verified with 20 samples on the same environment: warm new-session overview p95 ≤1.5s, common metadata navigation/filter p95 ≤500ms, selected source/result p95 ≤1s on the pilot, plus cold process-start-to-usable-page ≤4s (five restarts). Record budget misses transparently. Structural checks require zero evidence inspections and zero test-source reads on initial Overview, and bounded selected detail work. Repeat at deterministic 100/1,000-task fixtures with recorded edges/tests/files; no numerical large-fixture SLA is assumed.

If the optimized pilot repeatedly misses budgets or native controls fail the specified navigation/accessibility, stop for a documented architecture amendment: compare a thin FastAPI adapter over the existing Python domain/evidence modules plus React/TypeScript/Vite frontend. Reuse guards and evidence authority; estimated migration adds an API schema, route integration, build/dependency handling and rewritten browser tests (roughly 3–5 additional implementation tasks, not a calendar promise). Do not migrate speculatively or remove the current UI before a replacement passes the same journeys.
