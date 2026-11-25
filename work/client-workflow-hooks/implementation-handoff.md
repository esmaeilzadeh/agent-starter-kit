# Implementation handoff

- Workflow authority is frozen at `0e303265ceae1fbcdc9b2261bd922b003ab68924` in `/tmp/askit-dogfood.0BXUZGWN`.
- The human confirmed the complete intent and the exact Codex model plan. The independent spec challenge and plan review passed.
- Client instruction files such as `AGENTS.md`, `CLAUDE.md`, and `CODEX.md` are outside the install and upgrade write set. Keep executable hooks and workflow instructions in AskIt-owned paths. Add the AskIt registration only if absent in each editor's native hook registry. Preserve existing unrelated handlers, settings, and handler order.
- Implementation is pending at `CWH-01`. The active Codex session reported `gpt-6.2-sol` in its current turn metadata. The approved implementor is `gpt-6-luna`, and the frozen implementation preflight returned `manual_handoff`.
- In Codex, select `gpt-6-luna` with `/model` and verify with `/status`. On resumption record the observed model and provenance with `ask orchestrator-handoff resume`, run the implementation gate, and start with the four Red cases. No task writer has started.
