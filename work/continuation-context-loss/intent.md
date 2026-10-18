# Intent: Resume active work from repository state

## What

Before applying new-task intake to “continue” or “resume,” inspect repository and workstream state. Resume a uniquely identified active authorized workstream at its exact stage and task, retaining prior approvals. Ask only for workstream identification when evidence shows multiple plausible active candidates.

## Why

A reproduced continuation failure discarded an active implementation and asked the user to re-authorize it, causing interruption and avoidable user effort.

## Non-goals

Changing safety gates, expanding approval scope, or changing task behavior.

## Known assumptions

The current branch, durable work artifacts, inner-loop state, and recent commits together are sufficient to identify an active workstream in the reported scenario.

## Open questions

None for this bounded fix.

## Human decisions

None required; behavior is directly established by the reported failure and the repository evidence required to resolve it.

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: Agent workflow instruction change; validated through canonical-source and generated-binding checks.
