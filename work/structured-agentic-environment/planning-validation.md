# Connected workbench planning validation

Scope: planning only on the existing `agent/structured-agentic-environment` branch. Current design authority is the latest human brief and single-hierarchy clarification. No application implementation or feature verification is claimed.

Prepared: revision 3 canonical specification, self-contained plan and design/wireframes, nine-task graph, test mapping, design-skill pin, and real-workstream performance baseline with raw samples. The prior table-first plan is retained as historical context only in `plan-tabular-history.md`.

Checks before independent review:

- `./ask check-clean` passed at entry.
- `./ask prepare` and `./ask sync` completed. GitHub clone errors occurred; existing skills remained available. The exact pinned frontend-design skill was retrieved/read outside the repository; a subsequent `SKIP_INSTALL=1 ./ask prepare` validated all pins without claiming a new CLI installation.
- `./ask inner-loop validate structured-agentic-environment` passed.
- Direct canonical `validate_plan(spec, plan, graph)` returned zero violations.
- All 57 cases map exactly once to the same nine graph task IDs; graph case lists match `test-plan.json.task_scopes`.
- `./ask model validate --work-id structured-agentic-environment` passed with zero diagnostics.
- `git diff --check` passed.

Independent challenge found and corrected: executable test ownership versus scenario-mediated related tests, a missing numerical performance-test obligation, explicit Story traversal, precise rendered contrast/focus assertions, and the actual task-runner filtering behavior. Exact committed-source review and coordinator pin are recorded in `workbench-plan-review.md`, `traceability/workbench-plan-review.json`, and `traceability-accepted.json` after approval.

No future tests have been implemented/executed. Earlier passing cases and incomplete required red history remain historical evidence; a planning pin is not a verification pass. No new task execution state or task completion result is manufactured. Full feature Verify belongs after implementation.

Stopping condition: stop after independent planning review, corrected contract validation, coordinator pinning and commits. The human will switch to Luna and say `continue` before implementation.
