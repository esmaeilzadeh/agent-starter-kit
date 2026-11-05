## Specification

`specs/current/status-template-stage-detection.md` (revision 1; canonical criteria in `specs/current/status-template-stage-detection.json`).


## Approach

Make stage evidence specific to the artifact contract. A plan counts only when its Approach is meaningful or a complete work breakdown row contains both task ID and outcome. A review counts only when its Review verdict section is meaningful. Exercise the actual `./ask status` command end to end in committed temporary Git fixtures copied from the stock templates. Update the canonical 01 Grill contract to checkpoint the prepared intent and scaffold before approval questions, including re-approval after requested edits; regenerate its runtime projection.


## First task row
| stage-inference | Evidence-based plan and review stage classification | none | `_ask/scripts/status.sh`, `_ask/tests/test_status_stage_detection.py` | STATUS-BLANK, STATUS-FINDINGS, STATUS-PARTIAL-ROW, STATUS-APPROACH, STATUS-ROW, STATUS-VERDICT | Capture genuine Red then final Green for blank/incomplete evidence and Approach/populated-row cases when stock review guidance is present; run substantive-verdict preservation as a final-green regression; existing status shell contract remains green |

