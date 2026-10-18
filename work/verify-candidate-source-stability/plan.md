# Plan

## Specification

`specs/current/verify-candidate-source-stability.md` (CURRENT), criterion STAB-001.

## Approval record

The complete intent and every listed assumption were approved on the exact intent digest in `intent-confirmation.json`. Its recorded response supersedes the provisional “confirmation is pending” sentence in the original immutable intent snapshot; no intent content was changed after approval.

## Approach

Reuse the existing runtime-agent sync regression and the previously captured historical reproduction. Run CheckPlan on the final committed candidate, inspect isolated checkout status, then remove the later card with the evidence retained in the workstream. The direct bug fix predates this branch, so this work is validation and inbox reconciliation.

## Work breakdown

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| validate-and-close | Validate source stability and reconcile the parked card | none | `work/verify-candidate-source-stability/**`, `specs/current/verify-candidate-source-stability.*`, `.later/verify-candidate-source-stability.md` | STAB-I01 | Full `./ask verify`, clean candidate status, committed historical/current comparison, later card removed |

One task is appropriate: all outputs are evidence for one investigation, and splitting would add artificial boundaries.

## Risks

The original cause may not be the only mutation. Full CheckPlan plus the source-stability guard covers this. No new source fix is proposed unless verification finds another cause.

## Verification approach

Run STAB-I01 through the instrumented unittest adapter and run `./ask verify` on the final committed candidate. Require byte-for-byte projection snapshots and clean isolated Git status.

## Out of scope for this plan

Changing model bindings, weakening source checks, repairing optional skill installation, or changing public interfaces.

## E2E

Applies. Run the cleanup regression in a disposable committed candidate; inspect projection bytes and Git status before cleanup for normal and forced-failure paths. Then run the complete CheckPlan in an isolated checkout and retain its result.
