# Prefer the checked-out workstream when resolving “continue”

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `shorter-hashes` continuation (2026-10-20)
- **Start later:** new session, `./ask start-work continue-current-branch-priority`
- **First stage:** 01 Grill (destination is clear)
- **Tags:** workflow, continuation
- **Attribution:** user-reported workflow bug during continuation recovery
- **Affected responsibilities:** continuation recovery, active-workstream selection, terminal-stage handling
- **Publication status:** draft

## Why

When the user said “continue” while checked out on `agent/shorter-hashes`, I inspected the branch and artifacts, found that exact workstream recorded, and still asked which of many live workstreams to resume. The current branch is strong context for the intended workstream; a terminal recorded state should be reported as complete at its authorized endpoint, without making the user choose among unrelated live workstreams. The unnecessary question ignored the most relevant session evidence and added friction.

## Proposed What (unapproved)

- Define how continuation recovery uses the current branch, its workstream artifacts, inner-loop state, and recent commits to identify the intended workstream.
- Treat an explicitly named workstream as authoritative; otherwise prefer the workstream represented by the checked-out `agent/<work-id>` branch when the user says “continue” or “resume.”
- If that workstream has a valid terminal result or explicitly authorized stop, report that endpoint directly instead of asking which unrelated live workstream to resume.
- Ask the user to choose only when the recovery evidence leaves multiple plausible targets, such as a non-workstream branch with no uniquely active authorized workstream.
- Add continuation scenarios covering a checked-out branch at an unfinished stage, a checked-out branch at an authorized terminal stop, and ambiguous context without a work branch.

## Note

This card records the observed continuation-selection bug. It does not authorize changes to the `shorter-hashes` scope or continuation policy.
