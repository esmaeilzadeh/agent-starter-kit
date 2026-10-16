# Use buttons for user questions and flag important decisions

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `revising-workbench` inbox request (2026-10-16)
- **Start later:** new session, `./ask start-work button-based-user-questions`
- **First stage:** 01 Grill; destination is clear

## Why

The user wants questions presented as selectable options with buttons, especially yes/no decisions. Requiring typed approval phrases adds friction. Important decisions still need a clear alert so the user understands their significance.

## Proposed What (unapproved)

- Present user questions with selectable options using the runtime's button/choice control. In particular, yes/no and approval questions must offer buttons.
- Never require the user to type a prescribed phrase such as “approve” to submit a decision.
- Clearly alert the user when a question is important, for example when approving a spec change. Explain what changes and the consequence of the choice next to the options.
- Keep explicit human confirmation requirements: a default or preselected option is not approval. Record the option actually submitted.
- If the runtime lacks choice controls, accept a natural-language answer without requiring an exact approval phrase.

## Note

This card records future work; it does not approve a spec change or implement changes to the question flows. Cover ordinary questions, yes/no confirmations, and important spec-change decisions when implementing.
