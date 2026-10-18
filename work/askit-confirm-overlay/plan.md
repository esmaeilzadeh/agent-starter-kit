# Plan: Verify and close the askit confirmation defect

## Specification

Close the card only if the current implementation refuses non-Git use, asks before overlaying in an ordinary Git repository, and delegates to local `./ask` after Ask capability exists.

## Approach

Verify the existing fix commit is on develop, run the focused first-run and completion tests, record evidence, and remove the stale card.

## Work breakdown

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| ASKIT-001 | Evidence-backed stale-card closure | — | `.later/askit-confirm-overlay.md`, `work/askit-confirm-overlay/` | `test-askit-first-run.sh`, `test-askit-complete.sh` | Existing fix commit and both tests pass |

## Risks

The broader global askit bootstrap remains a separate proposal and must not be conflated with this fix.

## Verification approach

Check commit ancestry and run the two focused shell tests.

## Out of scope for this plan

Global askit bootstrap behavior and unrelated completion changes.

## E2E

`not_applicable`: the two isolated shell tests cover the CLI behavior.
