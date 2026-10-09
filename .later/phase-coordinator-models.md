# Separate coordinator models for planning and implementation

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `structured-agentic-environment` side conversation
- **Start later:** new session, `./ask start-work phase-coordinator-models`
- **First stage:** 01 Grill; destination is clear, runtime handoff details need confirmation

## Why

Use a stronger coordinator for analysis and planning, then a lower-budget coordinator for implementation. Existing stage-agent model routing does not switch the active parent coordinator, so assigning cheaper workers alone does not achieve this workflow.

## Proposed What (unapproved)

- Add coordinator profiles separate from specialist/stage-agent assignments. Starting recommendation: Sol/high for stages 00–05; Luna/medium for stages 06–10. Keep models and effort configurable by runtime and workstream.
- Stop when the plan is ready. Offer explicit choices: **Continue with Luna** / **Revise plan**. A preselected choice is not a submitted response.
- Before the transition, commit a handoff containing approved scope, assumptions, tasks, verification requirements, unresolved issues and the current commit SHA.
- Resume the same workstream and branch with the implementation coordinator. Check its effective model and handoff identity; do not claim generated configuration changes the running parent model.
- Keep specialist/reviewer model selection independent, so the cheaper coordinator can request stronger analysis or review when required.
- Return to the planning coordinator for scope/architecture changes, unresolved ambiguity or repeated implementation failures. Preserve existing approval, validation and acceptance gates.

## Note

The human requested this card be added to the later inbox. This parks the proposal; it does not authorize implementation or change the active main-thread model. Resolve manual model switching versus a runtime-supported automatic session handoff during Grill. Measure total usage and successful outcomes before claiming budget savings.
