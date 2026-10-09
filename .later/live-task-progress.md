# Show live task progress during agent work

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `structured-agentic-environment` side conversation (2026-10-09)
- **Start later:** new session, `./ask start-work live-task-progress`
- **First stage:** 01 Grill; destination is clear, runtime integration needs confirmation

## Why

The human sees commands running, followed by a finished indicator, without a task list showing completed, active, remaining, or blocked work. AGENTS.md requires periodic prose updates, but the Plan contract and runtime bindings do not require publishing and maintaining a live checklist. The inner-loop coordinator stores task states, while its status command only prints a snapshot on request.

## Proposed What (unapproved)

- Publish a short, named task list before multi-step work begins; keep task identities stable across updates and resumption.
- Update the list when a task starts, completes, becomes blocked, or changes scope. Show the current task, completed work, remaining work, and the blocker or next action.
- Use the runtime's native plan/progress tool when available. Provide a visible checklist in chat when that tool is unavailable; command activity alone does not satisfy progress reporting.
- Map inner-loop task state to the displayed list when a TaskGraph exists. Keep implementation, review, and verification distinct so a completed edit is not reported as verified work.
- Keep the existing periodic progress messages and report interruptions or missing evidence promptly. Mark completion only after the task's required evidence is available.
- Verify a representative multi-task journey shows intermediate transitions before final completion, including a blocked task and the fallback without a native progress tool. Check each supported runtime's capabilities rather than assuming one interface.

## Note

The human requested parking this proposal on develop and pushing develop. This card does not authorize implementing the progress feature. Repository inspection established the missing progress contract; the particular interface's rendering behavior has not been reproduced. Codex documents separate command and plan events: https://learn.chatgpt.com/docs/app-server.
