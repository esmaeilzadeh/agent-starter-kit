# Implementation checkpoint

Status: IMPLEMENTING. This file records progress, not completion or acceptance.

## Authority

The human authorized implementing the fixed plan, broader model before UI,
and merging the finished work to `develop` and pushing. `main` remains outside
that integration authorization. The earlier plan-only stopping point is
superseded; accepted criteria and test obligations remain unchanged.

## Implemented slices

- Typed document validation, canonical reference closure, captured content identities.
- Immutable validated generations, journaled multi-file publication and recovery.
- Semantic decision history, dependency invalidation and derived task readiness.
- Read-only inspection through the existing traceability completion evaluator.
- Native external-save observation with full-validation freshness fallback.
- Adopted-workstream admission around Verify, review/completion recording,
  acceptance checking and inner-loop execution/integration.
- Hashed cooperative publication history distinguishes guarded edit chains from
  raw canonical writes during a workflow action. This is local provenance,
  not authentication or a distributed transaction.
- Shared JSON/Markdown projections, read-only evidence inspection, CLI validation,
  admission, semantic edits, snapshots and native external-save observation.
- Native Streamlit workbench with read-only invalid-state display, attributed
  decision resolution, task consequences, canonical assertions and evidence
  inspection. The form retains the displayed identity until explicit refresh.
- AppTest and real-browser journeys for missing/historical evidence, stale
  spec-only forms, refresh, decision persistence and new-session reload.

Targeted guard/model/CLI/evidence/UI/browser suites passed 26 tests together at
the implementation checkpoint. The accepted test plan's UI selectors and
source paths were reconciled with the implemented test names; its requirements
and criteria were not changed. Some behaviors/tests post-date their production
code, so their historical red/green sequence is not claimed.

The complete guarded-action benchmark was run against commit `f5c2b48` on
Python 3.10.12, Linux x86_64, Intel i7-2720QM. It used three fresh processes
per action/workload and disposable repositories. Valid-action median/p95
measurements were approximately 570/600 ms (12-node pilot), 618/633 ms (100),
778/789 ms (1,000), and 2,901/2,943 ms (10,000). This supports retaining the
stdlib Python implementation for the current pilot: no native backend was
available or justified by this measurement. The 10,000-node synthetic case is
multi-second; no performance target was agreed, and timing includes benchmark
instrumentation. The measurement is indicative, not a production SLO.

## Remaining exit gates

1. Finish the final test-plan-bound test run and audit actual red/green evidence;
   retain the known chronology gaps instead of manufacturing failures.
2. Obtain an independent final review of the integrated branch and address any
   findings.
3. Run full Verify, exact-candidate result recording and acceptance checks.
4. Obtain required human Accept confirmation, then perform the authorized
   `develop` merge/push. No partial implementation merge.
