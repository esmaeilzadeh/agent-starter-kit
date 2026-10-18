# Intent: Make agent workflow decisions straightforward

## What

Refactor and reconcile agent-facing workflow instructions so that an agent can
identify its current state, next action, responsible role, required inputs and
evidence, exit condition, and escalation or human-confirmation condition from
clear, authoritative guidance. Cover overlapping stage contracts, policies,
templates, skills, and generated runtime bindings, including the boundary
between the task loop and the outer workstream lifecycle.

## Why

Overlapping and conditional instructions currently make agents assemble an
implicit workflow from several documents. This leads to hesitation, repeated
work, unnecessary confirmation requests, and inconsistent execution.

## Non-goals

- Remove or weaken existing safety, approval, verification, evidence, clean
  worktree, branch, or commit requirements.
- Adopt the candidate nested task sequence as a redesign without review.
- Change product behavior or domain requirements unrelated to workflow
  instruction clarity.
- Treat generated runtime bindings as independent sources of truth.

## Known assumptions

- Existing safety and acceptance requirements remain in force unless a
  separately approved change explicitly changes them.
- `.agents/ask/stages/` remains authoritative for stage contracts;
  `_ask/policies/` remains authoritative for cross-cutting policy; operational
  reference material stays with its owning protocol docs. A new lifecycle
  transition reference may define cross-stage transitions and be linked from
  those owners. Generated runtime bindings remain projections.
- The refactor clarifies the intended current behavior. Where the intended
  behavior cannot be inferred from the existing contracts, surface the
  decision for approval instead of choosing a behavior change implicitly.
- The documented flow must distinguish task completion from workstream
  completion and cover review, correction, verification, integration, retry,
  and resume transitions.
- Validation should include the seven scenarios listed in the later card:
  single task, dependent tasks, rejected review and correction, failed
  verification, interruption and resume, stale approval, and dirty source
  versus expected runtime evidence.
- The final design may reorganize instructions and add a canonical transition
  reference, but the precise source-of-truth arrangement belongs in Spec.

## Open questions

- Does the human approve the stated authority arrangement and the constraint
  to preserve existing behavior unless an explicit decision authorizes a
  change?
- Are the seven scenario walkthroughs and their observable next-action,
  responsible-role, evidence, exit, and escalation fields sufficient
  acceptance evidence?

## Human decisions

- The later card is now active at the user's request. Its proposed What was
  explicitly marked unapproved; this intent presents that scope for approval
  before Spec and implementation.
- Approval is requested for this complete intent and its listed assumptions.

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: Documentation and workflow-instruction changes;
the acceptance evidence is consistency checks and scenario walkthroughs, not
a user-facing product journey.

If `applies`: journeys, observable outcomes, environment, test data, reset:
