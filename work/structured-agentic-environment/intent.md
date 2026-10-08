# Intent: Engineering Model, then interactive workbench

## What

Build a broader, typed and independently validated Engineering Model for intent, requirements/features/stories/scenarios, decisions/assumptions/risks, tasks, implementation and test/evidence references. Add controlled, attributable semantic edits and deterministic machine/Markdown projections. Only after that foundation works, add an interactive local UI for work navigation, inspecting existing behavioral evidence and resolving meaningful decisions.

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

## E2E

Applicability: `applies`.

Journeys: CLI validate/project → resolve a decision → reload and see dependent tasks unblocked; interactive work → scenario → assertion/test/revision evidence; UI decision submit → durable model revision → reload with changed attention/task state. Rejected invalid/stale edits preserve bytes. Environment: disposable local Git/JSON fixtures, Streamlit 1.59, temporary browser/server for browser E2E. No real work or production data is mutated by tests; reset deletes only test-owned temporary directories. Existing archived harness records remain read-only.
