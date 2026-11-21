# Route task activities through fit-for-purpose workflows

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `continuation-recovery`, 2026-10-24
- **Start later:** new session, `./ask start-work task-activity-routing-flows`
- **First stage:** 00 Explore; identify the activity types and their distinct evidence and approval needs before settling the route model
- **Tags:** routing, task-types, workflow
- **Attribution:** user's request to investigate the gate across task types and define a flow
- **Affected responsibilities:** request classification, workflow selection, and task completion evidence across bug fixes, features, investigations, refactors, documentation, test/harness work, and operational changes
- **Publication status:** draft

## Why

The current request gate distinguishes reproduced bug fixes, behavior changes,
and mixed requests. Other work discussed alongside it—investigation, refactoring,
documentation, test or harness maintenance, performance work, dependency or
platform upgrades, data migrations, security work, and release or operations
tasks—can require different steps and evidence. Routing all of them through the
feature path may add unnecessary process, while treating them as bugs or leaving
them unrouted can omit important checks.

These labels may overlap and may describe either an intended outcome or an
activity. The gate needs an evidence-based inventory before it grows into a
separate workflow for every label.

## Proposed What (unapproved)

- Inspect the current request gate, its authoritative sources and generated
  projections, plus representative repository work. Identify where requests
  become ambiguous, inherit the wrong workflow, or receive unnecessary gates.
- Propose a small shared intake and routing flow. Distinguish task outcome,
  activity, risk, expected behavior, and authorization so similar labels with
  different consequences can follow different routes.
- For each validated activity type, define its entry condition, essential
  actions, approvals, artifacts, verification evidence, completion condition,
  and escalation or resume behavior. Include investigation-only, refactor,
  documentation, test/harness, performance, dependency/platform upgrade, data
  migration, security, and release/operations work as candidate types; validate
  or revise that list from actual examples.
- Preserve the established routes: reproduce a reported defect before writing
  its focused regression or changing code; keep passing edge guards Green;
  apply the feature workflow to requested behavior changes; split mixed
  independently deliverable outcomes and preserve their dependencies.
- Specify how routing composes with continuation recovery, an active workstream,
  and requests that should be parked, so classifying a new task cannot silently
  replace authorized work.
- Prefer shared steps with route-specific evidence over a full workflow per
  label. Produce a concise decision table and flow, then update canonical
  instructions and generated bindings only as needed to make the selected route
  unambiguous.
- Walk through representative requests for each selected route and check that
  each reaches one clear next action with proportionate evidence and no
  conflicting or redundant approval. Add automated routing checks only where
  the chosen contract is deterministic and testable.

## Note

This card records an investigation and proposed workflow design; it does not
authorize changing the current request gate. The current gate is recorded in
`work/continuation-recovery/request-routing-guard.md`,
`AGENTS.md`, `.cursor/rules/workflow-guidance.mdc`, and
`_ask/policies/workflow.md`. Coordinate with `.later/agent-decision-clarity.md`
if its broader prompt/rule inventory is active, and keep this work focused on
task classification and route flows.
