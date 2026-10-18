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

- Where should cross-stage transition authority live, and how should stage
  contracts, policies, skills, and runtime projections reference it?
- Should conflicting existing instructions be resolved to the current
  intended behavior only, or is any behavior change desired?
- What observable result demonstrates a scenario has exactly one applicable
  next action and owner?

## Human decisions

- The later card is now active at the user's request. Its proposed What was
  explicitly marked unapproved; this intent presents that scope for approval
  before Spec and implementation.

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: Documentation and workflow-instruction changes;
the acceptance evidence is consistency checks and scenario walkthroughs, not
a user-facing product journey.

If `applies`: journeys, observable outcomes, environment, test data, reset:

