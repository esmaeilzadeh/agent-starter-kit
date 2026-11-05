# Specification: Reliable workstream stage detection and resumable approval pauses

## Status

CURRENT

## Goal

Make `./ask status` report a stage only when its artifact contains evidence of that completed stage, and make the first intent approval pause resumable from a clean worktree.

## Non-goals

- Change the required review process or review template instructions.
- Change branch inventory, archive rules, or Git object identifiers.
- Automatically stash, discard, or move worktree files.
- Repair existing workstream artifacts.

## Behavior

- A review counts as complete only when `## Review verdict` has meaningful content. Stock instructions or findings without a verdict do not count.
- A plan counts as complete when `## Approach` has meaningful content or `## Work breakdown` contains a populated task row with both a task ID and outcome. Stock guidance, table headers, separators, blank rows, and incomplete rows do not count.
- Meaningful plan and review content continues to advance the inferred stage.
- Before asking for the required intent approval choice, the agent commits the prepared intent and generated workstream scaffold on the dedicated work branch. Approval is still tied to the exact intent content; any requested edit is committed before asking again.

## Interfaces

- `./ask status [--work-id <id>] [--json]` keeps its existing interface and reports evidence-based stages.
- `./ask confirm-intent` keeps its existing interface and digest-bound approval behavior.

## Constraints

- Stage detection reads committed workstream artifacts from Git refs.
- Human intent approval remains mandatory before implementation.
- Checkpoint commits remain on the dedicated workstream branch.

## Invariants

- Template instructions alone never count as completed stage evidence.
- A review is complete for status purposes only when a verdict is recorded.
- Prepared intent is committed before the approval question is presented.
- A choice to request changes never authorizes implementation.

## Failure cases

- Untouched plan and review templates are reported as `seeded` (or the highest earlier stage with substantive evidence).
- Findings without a review verdict and incomplete plan rows do not advance the stage.
- A meaningful verdict advances status to `reviewed`.
- A dirty checkout is not silently stashed or discarded to satisfy the pause checkpoint.

## Acceptance criteria

- `./ask status` on a Git fixture containing untouched stock plan and review templates reports `seeded`.
- A fixture with a populated task row or meaningful approach reports at least `planned`; a fixture with a recorded verdict reports `reviewed`.
- Findings without a verdict and incomplete task rows do not advance to `reviewed` or `planned`.
- The 01 Grill contract explicitly requires committing the completed intent and generated scaffold before presenting the approval choice, and committing revisions before re-presenting it.

## Open questions

None.

## Source intent

`work/status-template-stage-detection/intent.md`

## E2E

Applicability: not_applicable

If not_applicable, reason: The affected interface is a local Git inventory command and its repository workflow contract; temporary Git fixtures exercise the observable behavior.
