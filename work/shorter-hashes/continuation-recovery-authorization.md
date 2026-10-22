# Continuation recovery interrupt

## Human direction

On 2026-10-22, the user directed: “no these kind of error will be reproduce
multiple time in the process please fix it first then continue your work”.
The subsequent direction, “after plan for fix stop”, sets the current endpoint:
prepare and review the recovery-fix plan, commit its artifacts, then stop.
Implementation and resumption of product tasks are outside this turn's endpoint.
A generic continuation must respect this stop until explicitly superseded.

On 2026-10-22 the user subsequently directed: “apply all review changes and seal
the plan and stop”. This authorizes resolving R1–R4, independently reviewing the
supplemental and combined contracts, and registering the combined planning
contract through the existing accepted-tests mechanism. It supersedes the earlier
restriction on changing planning artifacts/authority for this sealing operation.
Implementation, bootstrap state mutation and product resumption remain stopped.

## Scope

Prepare a bounded shared-workflow repair for losing or contradicting task
execution state between runs. Keep this interrupt on `agent/shorter-hashes`;
create no overlapping workstream or task writer. Proposed requirements and plan
are in `continuation-recovery/spec-change.md` and `continuation-recovery/plan.md`.
The supplemental requirements join the combined planning contract when the
review and coordinator registration recorded in `continuation-recovery/plan-seal.md`
succeed.

Keep approved `intent.md`, original product criteria/test classifications and
existing task state/results unchanged. Add the recovery criteria/cases and
ordered repair tasks through the reviewed combined contract. Preserve prior
authority provenance before registering its replacement. Resolve execution
inconsistencies through future recovery, not manufactured Red or automatic
regression reclassification.
This artifact records the explicit interrupt and stop without editing approved
product intent bytes.
