# Plan: Present all confirmations as selectable choices

## Specification

Every required workflow confirmation is presented as an explicit selectable choice. If choice controls are unavailable, provide numbered choices and accept the number or label. Never require a written approval sentence. Keep existing approval boundaries, digest binding, conditional and negative rejection, unsolicited typed approval compatibility, and exact-scope enforcement.

## Approach

1. Identify every required confirmation point across canonical stages and policies.
2. Define consistent selectable choices for routing, intent, spec change, model selection, worktree decisions, skill preparation, and acceptance.
3. Clarify unsolicited concise affirmative parser compatibility while retaining conditional and negative rejection and digest binding.
4. Update canonical docs and regenerate every Agent and Cursor runtime projection.
5. Run focused confirmation, workstream, and projection checks; run repository verification and record any existing accepted-tests migration blocker.

## Work breakdown

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| CHOICE-001 | Every required confirmation is a selectable question | — | .agents/ask/stages, _ask/policies, AGENTS.md, _ask/guide, _ask/spec, generated Agent/Cursor projections | test-check-workstream-confirmation.sh, test-workstream-smoke.sh | Canonical and generated instructions agree; submitted choices preserve all approval gates |
| CHOICE-002 | Unsolicited clear compound approval remains accepted | CHOICE-001 | _ask/scripts/intent-confirmation.py, _ask/tests/test-check-workstream-confirmation.sh | test-check-workstream-confirmation.sh | Compound approval passes, exact response persists, conditional and negative responses remain refused |

## Risks

Overly broad parsing could accept conditional assent. The implementation requires an approval verb at the start and rejects conditional, negative, or revoking qualifiers.

## Verification approach

Run bash _ask/tests/test-check-workstream-confirmation.sh, bash _ask/tests/test-workstream-smoke.sh, ./ask sync, and ./ask verify.

## Out of scope for this plan

Removal of existing approvals, protected-branch authorization, or unrelated ordinary yes/no questions and decision alerts.

## E2E

not_applicable: isolated CLI confirmation and workstream gate tests cover the interaction.
