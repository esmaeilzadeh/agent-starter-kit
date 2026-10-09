# Refactor prompts, skills, and rules so agent decisions are straightforward

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `structured-agentic-environment` side conversation (2026-10-09)
- **Start later:** new session, `./ask start-work agent-decision-clarity`
- **First stage:** 00 Explore; the desired outcome is clear, but the full conflict inventory and refactor boundaries need investigation

## Why

The human reports that system behavior became foggy after the inner loop was added. Individual checks are detailed, but the agent must reconcile overlapping prompts, skills, stage contracts, and policies to decide what happens next. This increases the chance of hesitation, repeated work, unnecessary confirmation requests, and inconsistent execution.

Concrete examples from the current contracts:

- Implement declares the current task done when integrated, although integration already requires independent review; Review also appears as the next outer stage. The nesting and return transitions need to be explicit.
- Implement conditionally enters the inner loop when `tasks.yaml` exists, while Plan requires creating that file. The effective default is obscured by conditional wording.
- Task review and verification coexist with outer review and verification. Their scope, ownership, evidence, and completion conditions must be clear to the agent at each transition.

These observations support a clarity problem; they do not establish that every reported behavior was caused by the inner loop.

## Proposed What (unapproved)

- Inventory conflicts and ambiguous instructions across entry prompts, canonical stage contracts, skills, policies, templates, and generated runtime bindings. Include approval, delegation, clean-worktree, branch, and commit rules where their interaction changes the next action.
- Establish explicit authority and precedence for overlapping instructions. Keep canonical decisions in one place and derive or reference runtime projections without introducing competing rules.
- Define how the outer workflow contains the task loop. For each state, specify the acting role, required inputs, permitted action, exit condition, next state, and escalation or human-confirmation condition.
- Distinguish task completion from workstream completion and make review, correction, verification, integration, retry, and resume transitions explicit. Resolve conditional-versus-required behavior consistently across Plan and Implement.
- Refactor the affected prompts, skills, and rules into direct decision instructions so the agent can identify the current state, next action, and responsible role without assembling an implicit workflow from several documents.
- Preserve existing safety and acceptance requirements unless a separately approved intent or spec change authorizes changing them.
- Validate representative scenarios: a single task, multiple dependent tasks, rejected review and correction, failed verification, interruption and resume, stale approval, and dirty source versus expected runtime evidence. Each scenario should identify one applicable next action and owner, with no conflicting instructions or accidental extra approval gates.

## Note

The human requested: "add it to latter inbox: refactor to fix such conflicts in prompt,skill and rules and make the decision straitforward for the agent".

An explicit nested task sequence (Implement → Review → Fix as needed → Verify → Integrate, followed by workstream verification and acceptance) is a candidate to investigate, not an approved redesign. This card parks the refactor; it does not start implementation or change the current workflow.
