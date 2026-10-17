# Preserve implementation continuity across turns

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `revising-workbench`
- **Start later:** new session, `./ask start-work <new-work-id>`
- **First stage:** 00 Explore if dest is foggy; else 01 Grill

## Why

During an active implementation, the assistant lost track of the approved work and asked the user whether it was continuing. The user had already instructed it to continue, then had to grant permission again. The user also had to re-establish context by asking why `_ask/tests/test_revising_projection.py` changed and whether the change was spec cheating. This interrupts work, makes the user repeat decisions, and weakens confidence that tests and implementation remain bound to the accepted plan.

## Proposed What (unapproved)

Improve cross-turn and post-compaction continuity so an active implementation resumes from the repository's current workstream state, preserves the user's existing authorization, reports meaningful progress, and does not ask for confirmation again unless a genuinely new permission boundary appears. Before explaining test changes, inspect the exact diff and map each assertion to the accepted task/spec; distinguish added regression coverage from weakened acceptance criteria. Record a concise continuation note when needed, including current branch/work ID, accepted scope, completed commits, exact candidate and test evidence, reviewer findings, unresolved work, and the next required action.

## Note

Observed on `agent/revising-workbench` while implementing accepted task RWB-106, “Open subjects and contextual Task routes in Streamlit.” The user said “continue,” asked that the dropped continuity be reported to the later inbox, then asked “do you continuing the implementation?” and granted permission. The implementation was already authorized by the earlier request; the additional permission prompt was redundant. The user then questioned `_ask/tests/test_revising_projection.py`, whose changes belonged to RWB-104's accepted projection ownership and added malformed runtime-state regression assertions. RWB-106 subsequently passed its assigned exact-candidate checks, but independent review found several UI gaps requiring further fixes. This card concerns the assistant's continuity and evidence-backed explanation behavior, not the product UI changes in RWB-106.
