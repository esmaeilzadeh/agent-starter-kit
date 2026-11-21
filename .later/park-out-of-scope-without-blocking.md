# Park out-of-scope findings without interrupting active work

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `shorter-hashes` Task 2, 2026-10-21
- **Start later:** new session, `./ask start-work park-out-of-scope-without-blocking`
- **First stage:** 01 Grill; destination is clear
- **Tags:** workflow, triage, bugs, features, refactoring
- **Attribution:** `shorter-hashes` Task 2; candidate base `a8c598967e44bcabf12c38ef486d57059d2d23b5`
- **Affected responsibilities:** active-work continuation, discovery triage, later-inbox intake
- **Publication status:** draft; not yet published to the integration branch or issue tracker

## Why

During active work, an out-of-scope finding prompted a decision request and paused the accepted task. The user directed that optional discoveries be parked by type so the current authorized work can continue without waiting for a separate scope decision.

## Proposed What (unapproved)

- When an out-of-scope bug, feature, refactor, policy issue, or other discovery arises during active work, create a typed `.later/<slug>.md` card with its evidence, source task, affected responsibilities, and proposed What/Why.
- Treat the current accepted scope as authoritative: do not expand the active task to handle a parked finding, and do not interrupt the active workflow to ask whether the finding should be handled now.
- Continue the current task after recording the card. If the finding makes that task impossible to complete correctly within its accepted scope, record the concrete blocker and continue any independent authorized work; do not silently broaden scope.
- Keep parked cards non-live. Start them only in a later session through the normal workstream intake process.

## Note

This card records the user's requested process rule. It does not authorize implementation of the cited Task 2 integration-gate defect in the active task.
