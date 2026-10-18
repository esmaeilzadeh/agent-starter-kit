# Intent: Make every agent confirmation a selectable choice

## What

Present every required confirmation across the Agent Starter Kit workflow as a question with selectable button options, including entry routing, intent approval, spec changes, runtime/model selection, worktree choices, skill preparation, and acceptance. Never ask the human to write or repeat a prescribed approval sentence. If the interface cannot provide choice controls, offer numbered choices and accept a number or option label. Keep the existing approval boundaries, workstream digest binding, conditional/negative rejection, and exact-scope enforcement. Update canonical protocol and policy sources and regenerate every derived Agent and Cursor bundle.

## Why

The agent repeatedly requested typed sentences and redundant confirmations across its workflow, including after the user had already clearly authorized the complete intent. Choice-based prompts remove that friction while preserving existing decisions and approval scope.

## Non-goals

Removing intent confirmation, accepting conditional approval, weakening stale-intent invalidation, or changing merge/push authority.

## Known assumptions

Where the interface lacks native choice buttons, numbered choices serve as the selectable fallback; unsolicited typed approval remains accepted.

## Open questions

None for this bounded parser and instruction fix.

## Human decisions

All workflow confirmation points are in scope; no workflow approvals are removed.

## E2E

Explore skipped: destination already clear.

Applicability: not_applicable

If not_applicable, reason: The isolated confirmation test exercises the parser and workstream gate with a temporary repository.
