# Plan

## Specification

`specs/current/continue-current-branch-priority.md` and its canonical JSON
criteria. The acceptance criteria are review-only because this change is agent
instruction text; no product runtime behavior is introduced.

## Approach

1. Update the continuation recovery rule in `AGENTS.md` and canonical
   `.agents/ask/stages/00-explore.md`.
2. Generate runtime projections with `./ask sync`.
3. Inspect each changed canonical and generated instruction against all four
   acceptance criteria, then independently review the candidate.
4. Run `./ask verify` and record any verifier blocker with its exact output.

## Work breakdown

Break implementation into reviewable tasks before coding. Use one row per
cohesive outcome; one task is valid when the work is a single deliverable, with
the reason recorded. Keep IDs aligned with `inner-loop/tasks.yaml` and
`test-plan.json`'s `task_scopes`.

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| CONT-001 | Correct continuation target resolution and regenerate runtime instructions | — | `AGENTS.md`; `.agents/ask/stages/00-explore.md`; generated Explore bindings | — | Canonical rule and every generated projection satisfy CONT-001–CONT-004; sync is idempotent |

Assign every planned test case to its responsible task. Give tasks without an
executable test a specific verification rationale. Create
`work/<work-id>/inner-loop/tasks.yaml` from `_ask/templates/inner-loop-tasks.yaml`.

This documentation-only task has no executable behavior test. Direct scenario
review of canonical and generated instructions is the evidence for all criteria.

## Risks

Over-prioritizing a stale or conflicting branch could resume the wrong stage.
The rule therefore requires matching artifacts, respects an explicit target,
and asks when stage or authorization evidence remains conflicting.

## Verification approach

Run `./ask sync` twice and confirm the second run produces no further diff.
Inspect canonical and generated instructions against all four criteria. Run
`./ask verify` before completion.

## Out of scope for this plan

Changing Engineering Model subject resolution, `./ask status` semantics,
branch/merge policy, or any authorization gate.

## E2E

`not_applicable`: the work changes agent decision instructions, not product
runtime behavior.
