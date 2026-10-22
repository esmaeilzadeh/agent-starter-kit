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


## Resolved bug slices (2026-10-18)

- Continuation recovery is implemented in continuation-context-loss: a clear “continue” resumes the uniquely active authorized workstream instead of restarting new-task intake.
- Every required workflow confirmation now uses selectable choices; written approval sentences are never required. If native controls are unavailable, agents offer numbered choices. Unsolicited concise text approval remains supported, and conditional/negative replies remain rejected. See the active workstream `agent/agent-decision-clarity` for this implementation.

## Additional observed friction (2026-10-18)

The `verify-candidate-source-stability` follow-up supplied a concrete case for this card. The historical mutation reproduced and all 37 checks passed. The user approved the intent and directed merge to `main` plus push, but the agent spent several turns on artifacts before acting. Specific remaining friction to investigate:

- Define a straightforward evidence-only completion route and when structured test provenance applies.
- Avoid self-created dirty-tree blockers by sequencing state-writing operations so the agent closes its own clean-tree boundary promptly.
- Prefer the concrete next action and report only real blockers after the user has authorized it.

These examples do not approve removing intent confirmation, clean-worktree protection, evidence requirements, or other safety rules. The broader inventory and workflow nesting review remains open.

## Re-evaluate before asking the human (2026-10-22)

The user requested:

> re-eval the situation and check if it still need human decision if not stop and show your decision with the level of certainty (if it is up to 80%) else ask it as a choice question with consequences.

Add this decision check to the proposed work: reconsider the available evidence and existing authorization before escalating. When a human decision is unnecessary and confidence meets the agreed threshold, stop and present the agent's decision with its confidence level. Otherwise, ask one choice question and explain the consequences of each option. Do not repeat a decision already submitted.

For this re-evaluation, use a smarter available model when one exists, or increase the current model's reasoning effort when supported. Perform that reassessment before deciding whether human input is still necessary.

The requested threshold wording is preserved above. Before implementing this rule, resolve whether “up to 80%” means at least 80% confidence or a different boundary; this inbox update does not silently choose its meaning or authorize bypassing an explicit human-only gate.
