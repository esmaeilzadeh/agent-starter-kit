# Readable task blocker decisions

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `revising-workbench`
- **Start later:** new session, `./ask start-work <new-work-id>`
- **First stage:** 00 Explore if dest is foggy; else 01 Grill

## Why

RWB-107's desired readable decision context includes task blockers, but its accepted `owned_paths` do not include `_ask/ui/workbench_tasks.py`. Changing that renderer would cross the task boundary without an ownership amendment.

## Proposed What (unapproved)

Show task blocker decision context in the task detail view, including decision title, available choices, latest actor and rationale, and resolution attribution. Add focused AppTest coverage for open and resolved blocker decisions, while preserving the existing source-of-truth behavior.

## Note

During RWB-107, the first implementation and test were made in `_ask/ui/workbench_tasks.py` and `_ask/tests/test_revising_detail.py`. The workbench_tasks change is being removed from RWB-107; the relevant test assertion is being moved out with it. This card captures only the deferred task-table feature and does not authorize implementation. If a future task is meant to include this behavior, make ownership explicit in its accepted plan before editing `workbench_tasks.py`.
