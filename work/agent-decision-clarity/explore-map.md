# Explore Map: Agent decision clarity

## Destination

Make an agent's next action, responsible role, and required evidence clear at each workflow transition, while preserving accepted safety and human-authority constraints. The later card proposes refactoring prompts, skills, stage contracts, policies, templates, and generated runtime bindings, but marks that What as unapproved.

## Notes

- Workstream started from `develop` on `agent/agent-decision-clarity` after a clean-worktree check.
- Current canonical stage contracts live in `.agents/ask/stages/`; `_ask/policies/` supplies cross-cutting policy; `.cursor/commands/` and `.cursor/skills/` are generated runtime projections. `_ask/templates/` supplies artifacts.
- No external Community Skill was needed to inventory these repository-owned contracts. No additional skill has been proposed or pinned.

## Decisions so far

- The destination is foggy enough to require Explore: the card identifies symptoms and examples, but the affected source-of-truth boundaries and refactor scope need a full inventory.
- Keep the existing safety and human approval constraints in scope for analysis; do not assume the requested clarity work authorizes removing them.
- Treat the proposed nested sequence (Implement → Review → Fix as needed → Verify → Integrate, followed by workstream verification and acceptance) as a candidate only, not an approved design.

## Not yet specified

- Whether the change should make one canonical workflow decision model (for example a transition table) and have stage prompts, skills, and runtime bindings reference it, or only clarify the current documents in place.
- Which responsibilities belong to the task loop versus outer workstream stages. The current contracts say an inner-loop task is done when integrated/blocked/escalated, while the outer pipeline still has Review, Refactor, Verify, and Accept; the relationship is not stated as a complete state-transition model.
- The canonical owner of rules that appear in more than one layer, including role authority, stage exit conditions, retries/resume, and human approval. Runtime files are generated projections, but policy and stage contracts both include overlapping operational rules.
- Whether to change wording only, restructure artifacts, or change behavior where current contracts produce contradictory next actions. Any behavior or authority change needs explicit scope and approval.
- Which representative scenarios are release criteria and what counts as “one applicable next action and owner” for each.

## Out of scope

- Removing or weakening safety, verification, approval, branch, clean-worktree, or evidence requirements without explicit approval.
- Rewriting the workflow based only on the three examples in the card without checking all related contracts and bindings.
- Implementing the candidate nested sequence before its authority and boundaries are agreed.

## Handoff to Intent

The outcome to own is straightforward agent decisions across overlapping workflow instructions: for each relevant state, an agent should be able to identify the current state, next action, responsible role, required inputs/evidence, exit condition, and escalation or human-confirmation condition. Explore found that current contracts distribute these rules across stage contracts, cross-cutting policies, inner-loop documentation, templates, and generated bindings. In particular, Implement describes task completion at integrated/blocked/escalated, while outer stages still require Review/Refactor/Verify/Accept; Plan and Implement also differ in how unconditionally they describe the inner loop, and duplicate operational rules make authority unclear. The card's broad refactor proposal remains unapproved. Grill should confirm the intended source-of-truth/derivation strategy, whether behavior may change where current instructions conflict, and the exact scenario set and acceptance evidence before Spec and Plan.
