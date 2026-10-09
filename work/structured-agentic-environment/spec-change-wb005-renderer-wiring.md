# Specification Change Proposal

## Current specification

WB-005 owns `_ask/ui/workbench_overview.py`, `_ask/ui/workbench_scenarios.py`, `_ask/ui/workbench_stories.py`, and `_ask/tests/test_engineering_workbench_overview.py`. Its accepted outcomes and test IDs are already captured in `plan.md`, `inner-loop/tasks.yaml`, and `test-plan.json`.

The integrated `streamlit_app.py` imports and calls none of the three WB-005 renderer modules. The selected-detail dispatcher currently handles epic, story, and scenario inline. With WB-005 barred from editing the app entry, its new renderers can pass isolated tests but cannot appear in the running UI.

## Proposed change

Add `_ask/ui/streamlit_app.py` to WB-005's owned paths and clarify its completion evidence to require wiring the overview, story, and scenario renderer modules into the existing selected-detail routes. Keep the existing behavior and case assignments: `WB-overview` and `WB-summary-links` remain the only WB-005 tests, and WB-005 remains dependent on WB-004.

The app entry change is limited to dispatch and data handoff. The renderers continue to use the already captured, validated projection and its source context. WB-005 must retain the UI rule to disclose missing stories or task mappings instead of inventing relationships.

## Why the change is needed

The current ownership boundary makes the planned visible result unreachable from the app. Repository search confirms there is no import or call site for the WB-005 modules. Adding the app entry to the same task gives one writer authority to connect the accepted renderers to the accepted WB-004 navigator without changing user-facing semantics or introducing a second task that competes for the same UI surface.

## Impacted artifacts

- `work/structured-agentic-environment/plan.md`: WB-005 owned paths and completion evidence.
- `work/structured-agentic-environment/inner-loop/tasks.yaml`: add `_ask/ui/streamlit_app.py` to WB-005 `owned_paths`.
- No changes to `test-plan.json`, criteria, test IDs, task order, or declared product behavior.

## Impacted workstreams

- `structured-agentic-environment`, currently at WB-005. WB-005 implementation is paused until this proposal is confirmed, reviewed, and accepted.

## Migration / transition notes

No data or runtime migration is required. If confirmed, recompute and independently review the task graph/plan bindings, refresh the accepted plan digest, and restart WB-005 against the amended clean base. Preserve all earlier WB-004 candidate and UI checkpoint evidence.

## Acceptance criteria for the change

1. The amended task graph lists `_ask/ui/streamlit_app.py` only under WB-005 in addition to its existing WB-004 ownership.
2. WB-005's existing mapped AppTests fail when the overview/story/scenario renderer dispatch is absent and pass when exercised through the actual app entry.
3. The original WB-005 behavior, test IDs, dependencies, and task order remain unchanged.
4. Independent review approves the exact amended plan and task graph before WB-005 implementation resumes.

## Decision

Pending human confirmation.
