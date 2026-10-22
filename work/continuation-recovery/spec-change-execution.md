# Specification change proposal: execute continuation recovery

## Current specification

The accepted `continuation-recovery` intent and recorded endpoint authorize
preparing and sealing a plan only. Implementation, runtime initialization,
behavior execution and product scheduling are excluded. The accepted recovery
contract is CR-01–CR-08 in `specs/current/continuation-recovery.json`.

## Proposed change

Extend this workstream from planning into implementation of the sealed four-task
repair graph, CR-1 through CR-4, on `agent/continuation-recovery`. Update the
workstream intent to state that it will implement and verify continuation
recovery under CR-01–CR-08. Keep product adoption/integration and product
scheduling excluded; CR-4 may produce only the read-only audit and reviewed
adoption proposal defined by the sealed plan.

The canonical accepted criteria remain unchanged. Implementation must follow
normal coordinator admission, Red → Green → Refactor, independent review,
integration, verification and acceptance gates.

## Why the change is needed

The plan has been sealed and independently approved, and the user has since
directed continuation after that endpoint. The current intent still names
implementation as a non-goal, so it does not accurately authorize the requested
next stage.

## Impacted artifacts

- `work/continuation-recovery/intent.md`: replace the planning-only What and
  non-goals with the proposed implementation scope after approval.
- `work/continuation-recovery/authorization.md`: record this later direction;
  it already records that the stop-after-seal endpoint was superseded.
- `work/continuation-recovery/inner-loop/tasks.yaml`: execute its existing
  CR-1 → CR-2 → CR-3 → CR-4 graph without changing accepted criteria.
- `work/continuation-recovery/plan-seal.md` and the registered authority remain
  historical planning evidence; implementation does not rewrite them.

## Impacted workstreams

Only `continuation-recovery`. The original `shorter-hashes` branch, state,
intent and authority remain outside this change.

## Migration / transition notes

After approval, update the intent and record the submitted exact-intent choice.
Then complete normal implementation admission and start CR-1 from the current
workstream coordinator head. Do not initialize or adopt the original product
runtime state. Preserve the sealed plan and its accepted authority unchanged.

## Acceptance criteria for the change

1. The user approves this scope change.
2. The revised intent is approved against its exact digest.
3. The existing CR-01–CR-08 contract and sealed four-task graph remain the
   implementation baseline.
4. Product adoption, integration and scheduling remain unauthorized.

## Decision

Pending user choice: **Approve spec change** or **Keep current spec**.
