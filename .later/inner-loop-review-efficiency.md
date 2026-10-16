# Improve inner-loop review efficiency across tasks

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `revising-workbench`
- **Start later:** new session, `./ask start-work <new-work-id>`
- **First stage:** 00 Explore if dest is foggy; else 01 Grill

## Why

RWB-103 exposed a repeatable process cost in the task-level implementation/review loop. Several candidates passed their mapped green tests and structural evidence checks, then independent review found additional defects or acceptance gaps. Each discovery required another immutable test-only red, source change, green run, candidate-bound review, and coordinator evidence refresh. The loop exposed useful defects, but the review findings accumulated serially instead of being consolidated early into one complete implementation checklist.

Observed RWB-103 sequence:

- Candidate `bdecb48` had a committed red/green pair for the four mapped test IDs and passed the assigned tests, but review found discarded explicit bounded fields, lost foreign revision context, malformed association history reaching a crash, unsupported foreign subject pointers, and gaps in real caller/association/intent coverage.
- Candidate `c7b63a7` fixed some of those findings, but review still reproduced loss of foreign context at publication, malformed top-level context acceptance, and gaps around successful caller and association paths.
- Candidate `9580886` fixed the first group and added a foreign pointer path. Fresh review still found stale foreign-context publication, malformed top-level fields, malformed history events, and the outstanding accepted coverage obligations.
- Candidate `7c7ec37` expanded tests for shared freshness and the association contract. Its immutable red run `ebc29096345f41fc8f79c12650357602` recorded behavior failures in three of four mapped cases; implementation was still in progress when this card was written.

The task already had an accepted TaskGraph and detailed completion-evidence descriptions. The problem to investigate is how the implementation and review protocol can reliably consume that complete contract, inspect real caller boundaries, and consolidate semantic review findings before each candidate is declared ready. This should apply across inner-loop tasks, not only revising-workbench or intake flows.

Useful evidence and context on the originating workstream:

- `work/revising-workbench/inner-loop/tasks.yaml` — RWB-103 scope and completion evidence.
- `work/revising-workbench/inner-loop/evidence/RWB-103-review-c7b63a7.md` — first full review with F1–F4 and G1–G4 findings.
- `work/revising-workbench/inner-loop/evidence/RWB-103-review-9580886.md` — follow-up review identifying remaining foreign-context freshness and malformed-input defects.
- `work/revising-workbench/traceability/RWB-103-review-input-c7b63a7.json` and `RWB-103-review-input-9580886.json` — machine-bound review evidence.
- Candidate history: `bdecb48`, `c7b63a7`, `9580886`, `7c7ec37`; active workstream state/result files record the corresponding task evidence.

## Proposed What (unapproved)

Investigate and improve inner-loop task execution efficiency across all tasks while preserving independent candidate-bound review and immutable test evidence. Determine whether the protocol needs: a single pre-implementation checklist synthesized from the full accepted task/spec/design and prior review findings; writer self-review against all planned caller, ownership, behavior, and evidence obligations before candidate submission; reviewer reports grouped into actionable must-fix and coverage items; and a coordinator readiness gate that prevents review of a candidate while its TaskResult, red/green evidence, or planned completion matrix is incomplete. Define how to avoid repeated reviews that merely rediscover already documented findings, while retaining genuinely independent review and fail-closed integration.

Do not weaken semantic review, erase rejected review evidence, reuse stale approvals after candidate changes, or bypass required red/green history. Measure the change against multi-task examples, including RWB-102 and RWB-103, and establish when an issue belongs to the task implementation versus a workstream-wide protocol improvement.

## Note

This is an investigation card, not authorization to change the active `revising-workbench` contract or to add process changes to that feature branch. RWB-103 was still running at candidate `7c7ec37` when recorded; its implementation, current final candidate, and human gates remain part of the active workstream. Keep this card separate from that branch. No push, merge to a shared branch, or deployment occurred.
