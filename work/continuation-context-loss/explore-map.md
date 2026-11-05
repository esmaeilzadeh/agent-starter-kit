# Explore Map: Resume the uniquely active workstream

## Destination

On “continue” or “resume,” recover the active authorized work from repository state before treating the message as a new task.

## Notes

The card records a reproduced workflow defect and a concrete deterministic recovery procedure. No product or policy choice is needed to resume a uniquely identifiable active workstream.

## Decisions so far

Use the current branch, workstream artifacts, inner-loop state, and recent commits to identify the active workstream and exact stage/task. Preserve existing authorization. Ask a narrow workstream-identification question only if evidence leaves multiple candidates.

## Not yet specified

None for this bounded correction.

## Out of scope

Changing the existing safety checks, creating a durable off-path mode, or changing authorization scope.

## Handoff to Intent

Add a continuation-recovery rule to the always-loaded repository guidance and canonical Explore contract. Regenerate runtime bindings from `.agents/ask/`; verify the generated agents include the canonical stage pointer/content as appropriate. Close the overlapping `implementation-continuity` card in a separate follow-up only after this fix is merged.
