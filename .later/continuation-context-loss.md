# Preserve active implementation context across continuation

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `revising-workbench`
- **Start later:** new session, `./ask start-work <new-work-id>`
- **First stage:** 00 Explore if dest is foggy; else 01 Grill

## Why

When the user said “continue,” the assistant discarded the active implementation
context even though the checkout was on `agent/revising-workbench`, the plan and
inner-loop state were committed, and RWB-104 was marked `running`. It incorrectly
treated the request as a new, foggy task and asked the user to choose Explore or
Grill. The user had to restate that implementation was underway. This interrupts
authorized work and shifts repository-state recovery onto the user.

## Proposed What (unapproved)

Improve continuation handling so an agent entering a resumed conversation checks
the current branch, workstream artifacts, inner-loop task state, and recent commits
before applying the new-task Explore gate. If those sources identify an authorized
active task, resume its current stage and preserve its exact task context. If more
than one plausible task remains, ask a narrow identification question after
capturing the recovery failure here.

## Note

Observed 2026-10-17 in `/home/mohamad/Projects/UNI/ai-agent-start-kit`. The
checkout was `agent/revising-workbench` at `536dbe5` (`refactor workbench.py`),
with RWB-104 `running` in `work/revising-workbench/inner-loop/state.json` and
RWB-101 through RWB-103 integrated. The assistant initially called `./ask status`,
confirmed a clean tree, attempted `./ask prepare` (which failed to fetch the pinned
`frontend-design` revision), then asked the user to choose 00 Explore or 01 Grill.
The user clarified: “you was in the middle of implementing a plan why you forget it
report this as an issue to later inbox with full context and continue the
implementation”. The implementation is the approved `revising-workbench` plan;
continue RWB-104 under its accepted scope and evidence protocol. This card records
the agent continuity failure, not a product acceptance decision.
