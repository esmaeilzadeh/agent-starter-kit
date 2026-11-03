# Continuation recovery interrupt

## Human direction

On 2026-10-22, the user directed: “no these kind of error will be reproduce
multiple time in the process please fix it first then continue your work”.
The subsequent direction, “after plan for fix stop”, sets the current endpoint:
prepare and review the recovery-fix plan, commit its artifacts, then stop.
Implementation and resumption of product tasks are outside this turn's endpoint.
A generic continuation must respect this stop until explicitly superseded.

## Scope

Prepare a bounded shared-workflow repair for losing or contradicting task
execution state between runs. Keep this interrupt on `agent/shorter-hashes`;
create no overlapping workstream or task writer. Proposed requirements and plan
are in `continuation-recovery/spec-change.md` and `continuation-recovery/plan.md`.
Those documents are a supplemental proposal, not the active registered contract.

Keep approved `intent.md`, the product specification, accepted test classifications,
active TaskGraph, existing state/results and authority refs unchanged while
planning. Resolve their inconsistencies through the proposed recovery procedure,
not by manufacturing Red evidence or treating every passing case as regression.
This artifact records the explicit interrupt and stop without editing approved
product intent bytes.
