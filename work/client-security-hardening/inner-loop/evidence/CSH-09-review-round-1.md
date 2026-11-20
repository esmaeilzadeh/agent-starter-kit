# CSH-09 independent review, round 1

Candidate: a838f86fb36a14113d778c89bab797a5fec5a93f
Reviewer: gpt-6.1-sol (medium)
Verdict: REJECTED
Boundary: ok

1. Direct public inner-loop spawn-writer calls spawn_writer without the new handoff gate. A confirmed mismatched orchestrator can start a writer through that route.
2. Manual observation cache accepts model/provenance without matching runtime/current selection binding; another runtime with the same model can reuse it.
3. Confirm-only submission with no new overrides deletes previously recorded exact exceptions. Preserve choices unless the human explicitly replaces/removes them.
4. Reviewer suggested enforcing identity on legacy unconfirmed plans; coordinator requested reconsideration because accepted CSH-011 explicitly assumes a confirmed policy/exact override and CSH09 preserves legacy behavior. Scope decision pending; first three findings independently require rejection.

Reviewer ran no tests. Frozen task finalGreen fc99b364d91c4ce28f26095f95dc5143 passed separately, but its cases did not cover these defects. Assertion strengthening and T34 fixture correction were accepted by reviewer.
