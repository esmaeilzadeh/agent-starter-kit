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

## Additional observed friction (2026-10-18)

The `verify-candidate-source-stability` follow-up supplied a concrete case for this card. The existing cleanup fix was already present, the historical mutation reproduced, and all 37 checks passed. The user then explicitly approved the intent and directed merge to `main` plus push. The agent still spent several turns on stage artifacts and a structured acceptance contract before acting on that direction; the user had to interrupt with “what are you doing?! merge back and push finish!”

Specific decision and workflow friction to investigate:

- A clear reply, “approve and merge back to main and push,” was rejected by the intent-confirmation parser because it did not match its narrow phrase list. The user had to repeat the full prescribed sentence. Make the required scope clear before asking, and let a semantically explicit approval satisfy the gate when the system can safely bind it to the intent digest.
- The agent repeated readiness/permission framing after the user had already approved the intent and explicitly authorized merge and push. Preserve genuine safety checks, but don’t ask again for authority already granted.
- The agent treated a documentation-only investigation as requiring the full structured test acceptance path. `./ask check-workstream --acceptance` then failed because no accepted-tests authority ref existed, even though the requested source validation had passed. Define a straightforward completion route for evidence-only work, with a clear rule for when structured test provenance applies.
- Recording approval created a file that immediately made the next clean-worktree check fail until it was committed. Sequence state-writing operations so the agent closes its own clean-tree boundary promptly and explains the cause without presenting it as a user blocker.
- The agent continued narrating kit transitions instead of answering the user's direct status question and completing the explicitly requested merge/push. Prefer the concrete next action and report only real blockers.

These are observed examples for Explore and design work. They do not approve removing intent confirmation, clean-worktree protection, evidence requirements, or other safety rules; clarify how to satisfy them with fewer repeated turns and less avoidable process overhead.
