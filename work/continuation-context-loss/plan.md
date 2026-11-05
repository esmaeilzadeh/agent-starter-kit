# Plan: Restore continuation from repository state

## Specification

For a continuation request, inspect branch, workstream artifacts, inner-loop state, and recent commits before applying new-task intake. Resume one uniquely identified active authorized workstream at its recorded stage/task and preserve approvals. Request only workstream identity if multiple candidates remain.

## Approach

1. Add the recovery rule to always-loaded repository guidance and canonical `.agents/ask/stages/00-explore.md`.
2. Run `./ask sync` to regenerate runtime projections from the canonical stage source.
3. Verify the generated projection and sync idempotence; run the repository verification command and record any pre-existing infrastructure blocker.
4. Remove the two-line-of-work overlap card only after the same merged change is present on `develop`.

## Work breakdown

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| CONT-001 | Continuation recovery guidance in canonical and generated sources | — | `AGENTS.md`, `.agents/ask/stages/00-explore.md`, generated Explore projections | Sync idempotence | `./ask sync` succeeds twice without further diff |

## Risks

A broad instruction could mistakenly bypass a genuine new-task gate. The rule is explicitly limited to continuation language and resumes only uniquely identified active authorized work; ambiguous identity remains a narrow clarification.

## Verification approach

Run `./ask sync` twice and confirm the second run changes no tracked files. Inspect canonical and generated Explore content. Run `./ask verify`; if blocked by unrelated accepted-tests migration, record the exact blocker and verify the changed projections directly.

## Out of scope for this plan

Intent parser changes, new task routing, and changes to approval or worktree safety policy.

## E2E

`not_applicable`: this changes agent decision instructions, not product runtime behavior.
