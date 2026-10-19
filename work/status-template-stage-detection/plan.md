# Plan

## Specification

`specs/current/status-template-stage-detection.md` (revision 1; canonical criteria in `specs/current/status-template-stage-detection.json`).

## Approach

Make stage evidence specific to the artifact contract. A plan counts only when its Approach is meaningful or a complete work breakdown row contains both task ID and outcome. A review counts only when its Review verdict section is meaningful. Exercise the actual `./ask status` command end to end in committed temporary Git fixtures copied from the stock templates. Update the canonical 01 Grill contract to checkpoint the prepared intent and scaffold before approval questions, including re-approval after requested edits; regenerate its runtime projection.

## Work breakdown

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| stage-inference | Evidence-based plan and review stage classification | none | `_ask/scripts/status.sh`, `_ask/tests/test_status_stage_detection.py` | STATUS-BLANK, STATUS-FINDINGS, STATUS-PARTIAL-ROW, STATUS-APPROACH, STATUS-ROW, STATUS-VERDICT | Capture genuine Red then final Green for blank/incomplete evidence cases; run preserved Approach, populated-row, and verdict behavior as regression cases at final Green; existing status shell contract remains green |
| approval-checkpoint | Clean resumable intent approval pause | none | `.agents/ask/stages/01-grill.md`, `.agents/skills/kit-01-grill/SKILL.md`, `.cursor/skills/kit-01-grill/SKILL.md`, `.cursor/commands/01-grill.md` | — | Canonical stage and every generated runtime projection require commit before initial approval and before renewed approval after edits; direct independent review confirms all four files are synchronized |

The task graph and test mapping are committed at `work/status-template-stage-detection/inner-loop/tasks.yaml` and `work/status-template-stage-detection/test-plan.json`. The approval-checkpoint task has no executable behavior test because its outcome is a model-facing protocol instruction; direct source/projection review is the appropriate evidence.

## Risks

- Section parsing can mistake Markdown framing or instructional prose for evidence. Tests use stock templates plus minimal valid and invalid edits.
- A complete task row may validly have an empty dependency field. Detection requires only task ID and outcome.
- Generated stage projections can become stale if sync is skipped. Verify canonical and generated files together.
- Workflow instructions are followed by agents rather than mechanically enforced; direct review provides evidence but cannot guarantee future compliance.

## Verification approach

- Run the mapped status integration cases at immutable red and final-green candidate revisions through `./ask traceability run`.
- Run the existing status shell test and all required checks with `./ask verify`.
- Independently review the exact candidate, mapped assertions, TDD continuity, and canonical/generated 01 Grill checkpoint language.

## Out of scope for this plan

- Merging `agent/shorter-hashes` or changing its task/test identifier proposal.
- Changing the status output interface or stage ordering.
- Automatically committing unrelated user files, stashing, or discarding changes.

## E2E

Applicability: applicable

Applicability: The mapped cases themselves run a complete local end-to-end journey through the public CLI using committed temporary Git fixtures. No additional external system journey applies.
