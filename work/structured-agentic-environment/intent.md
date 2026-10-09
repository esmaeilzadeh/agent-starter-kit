# Intent: Engineering Model, then interactive workbench

## Current follow-up: tabular workbench

This is a follow-up fix within `structured-agentic-environment` on its existing branch, not a new workstream. Explore skipped: destination already clear. The original Explore artifact below this workstream remains historical context.

What: replace text-list and JSON-first inspection in `_ask/ui/streamlit_app.py` with read-only tables for tasks, engineering objects, canonical scenarios/planned tests, and evidence. Selectable rows open associated details, including long descriptions, assertions, nested evidence and existing decision forms. Keep raw evidence JSON in a collapsed debug section.

Why and intended user: the local developer needs to scan and compare engineering state, select an item, inspect its supporting details, and resolve an open decision without reading a JSON dump.

Interaction expectations: workstream selection establishes the displayed snapshot; selecting a row changes the inspected item. Existing refresh, evidence-candidate inspection and decision-resolution workflows continue to operate with their current validation and stale-state protections.

Assumptions: use native Streamlit tables; tables are read-only; retain the existing decision form as the edit mechanism; keep raw JSON collapsed for debugging; preserve complete inspectable details rather than dropping nested values to fit columns. Use the existing workstream, branch and artifacts. The training-run viewer is outside this fix.

Non-goals: inline table editing, new domain behavior, model/schema changes, a navigation redesign, a new frontend framework, deployment, and changes to evidence authority or validation rules.

Acceptance: the four inspection sections use readable tables; selected rows expose the correct complete details; evidence is no longer presented as an expanded JSON dump by default; existing refresh, candidate inspection, decision persistence and stale-state rejection continue to work.

E2E applies: use existing disposable local Git/JSON fixtures and a temporary Streamlit/browser environment to inspect table contents, select rows and verify associated details, inspect evidence, resolve a decision and reload, and reject a stale decision. Test-owned fixtures and temporary server processes are removed on teardown; do not mutate committed pilot data.

Human decisions: the user required this to remain a follow-up fix of the current task and replied “go for it” to the expanded recommendations for broad table coverage and selectable-row detail panels. Confirmation of the complete updated intent and assumptions is pending. No unresolved product question remains for this bounded fix.

## What

Build a broader, typed and independently validated Engineering Model for intent, requirements/features/stories/scenarios, decisions/assumptions/risks, tasks, implementation and test/evidence references. Add controlled, attributable semantic edits and deterministic machine/Markdown projections. Only after that foundation works, add an interactive local UI for work navigation, inspecting existing behavioral evidence and resolving meaningful decisions.

The document-state validator owns requirement/link validity. Every state-changing action must start from validated stable state and validate its result before publication. Revalidate after every specification save, including referenced documents. The UI consumes only validated snapshots; it has no duplicate graph-validation or repair logic. Fast existing tools and lower-level languages are allowed; Python is not a requirement.

## Why

The developer needs to inspect engineering claims, decide unresolved questions and see their consequences while agents consume the same definitions. Generated prose and a test link alone are not authority or proof of satisfied behavior.

## Non-goals

Replacing existing specification/test/completion authority; automatic code execution or acceptance from the UI; rebuilding harness-review; production deployment/authentication; database/multi-host infrastructure; a complete IDE, graph editor or multi-agent control room; migrating every workstream; claiming measured human/agent productivity improvement.

## Known assumptions

Local repository, one cooperating developer, revisioned JSON definitions and POSIX file locking are appropriate for the bounded pilot. Harness-review supplies real existing scenario/test/evidence records. A visibly labeled pilot decision exercises future-work interaction without pretending it blocked historical harness delivery. These are reversible implementation defaults within the authorized direction.

## Open questions

No blocking What/Why decision remains for this bounded slice. Comparative usability and broader taxonomy suitability remain future experiments, not fabricated results. Additional infrastructure or changes to existing semantic authority require Spec Change.

## Human decisions

Explore explicitly requested. Completed harness baseline belongs on main/develop; local develop was fast-forwarded to main. Human corrected the order to “Broader model first then interactive UI.” Human then required current models matched to each job and its budget, asked about effort, and said “ok continue and then continue the main plan.” This continuation uses that authorization; it does not authorize main/develop merges or pushes.

Subsequent clarifications require clean UI input, pre/post action validation and freedom to choose fast tooling/native code. The historical request “continue till you give me a plan” governed the earlier planning turn. The current request is the tabular workbench follow-up above. Decision record for the earlier validation change: `spec-change-validation-guard.md`.

## E2E

Applicability: `applies`.

Journeys: CLI validate/project → resolve a decision → reload and see dependent tasks unblocked; interactive work → scenario → assertion/test/revision evidence; UI decision submit → durable model revision → reload with changed attention/task state. Rejected invalid/stale edits preserve bytes. Environment: disposable local Git/JSON fixtures, Streamlit 1.59, temporary browser/server for browser E2E. No real work or production data is mutated by tests; reset deletes only test-owned temporary directories. Existing archived harness records remain read-only.
