# Independent RWB-103 review: b215ab9

**Overall REJECTED: required ownership amendment. Semantic APPROVED. Ownership REJECTED (`glob_too_narrow`).** Reviewer `/root/review_revising_plan`, selected `gpt-6.1-sol` / high. Exact candidate `b215ab9af93fb2fc8e8be08c319d5576f8c5cdcc`; task base `ec1c2d614e014ade18a54fbfa13c970f77cb0322`; accepted contract/inventory base `5964fbfb56128e95676f0b991852ac58529cb8f8`. Complete task diff and immutable archive inspected. Earlier reports remain preserved; no source, state, refs or commits changed by reviewer.

## Sole blocker B1: required publication helper is outside ownership

The immutable accepted RWB-103 graph omits `_ask/scripts/engineering_model/admission.py`. Candidate changes `_publish` there to carry external guarded observations through final publication checks. Complete ec1→b215 diff has 18 paths: 17 fit accepted ownership, and this required helper is the sole outside path.

This is `glob_too_narrow`, not an unrelated extra to discard. The helper change is necessary for the reviewed final-publication responsibility and must receive a narrow independently reviewed ownership/completion-evidence amendment and accepted graph pin. No source exemption, state shortcut or integration authorization is granted. No other ownership or semantic blocker was found.

## F5b correction and independent boundary probes

The implementation now rechecks journal observations after managed recovery writes. On stale external input it restores local projection bytes, retains the old publication pointer and clears the journal when rollback has no conflict. Publication refusal follows the same rollback path.

`_publish` accepts the trusted journal observations and checks them together with ordinary snapshot freshness after generation staging, after publication-event persistence and after pointer-temp fsync immediately before replacement. Existing callers retain default behavior when no extra observations are passed. This extends the final check to the actual foreign inputs rather than checking only the local snapshot.

I independently exercised exact candidate source with real guards/action/write/publication and only controlled external-save timing:

- Existing mapped post-local-write foreign save refuses, restores local bytes and leaves the published generation unchanged.
- Foreign save after generation manifest staging refuses and rolls back.
- Foreign save after publication-event persistence refuses and rolls back.
- Foreign save during pointer temporary-file fsync is detected by the final input check; pointer replacement is prevented and local bytes restored.
- Interrupted durable journal, recovered with `validated=None`, then foreign save after real local write refuses with recovery conflict, restores base local bytes, clears safe journal and retains the old pointer. No semantic action is re-executed.

The latter four probes started with an actual pre-existing admitted generation, so preservation compares a real old pointer rather than only absence of a generation. Foreign external bytes are preserved. Source inspection confirms the same guarded observations flow through normal and recovery publication. F5/F5b are resolved to the same final freshness boundary used for ordinary local inputs.

## Prior findings, assigned scope and tests

All earlier F1/F1b, F2, F3/F3b, F4 and G1–G4 remain resolved as assessed in the preserved d95 report: merged bounded shape validation; qualified subject/owner conflict handling; foreign revision retention and honest tracker metadata; pre-action malformed history handling; nominal foreign pointer support; real fresh caller order/no-write checks; positive known-subject CLI parity; successful uniquely required passage and real input/result/publication lineage; concrete confirmed-context-to-intent responsibility in canonical/generated Grill instructions before complete intent approval.

All four assigned cases and every selected criterion/type are semantically approved: EM-002 integration, EM-004 integration, EM-007 integration, EM-013 unit/integration, EM-015 integration, EM-018 unit/integration. This is task-scoped source assessment, not whole-workstream acceptance. Shared authority, immutable runner, accepted criteria/cases/types, state CAS and FF-only integration rules are unchanged. Canonical/generated stage bodies remain included; the production delta since d95 is the reviewed recovery/publication fix only.

Independent immutable-candidate execution:

- `python3 -m unittest _ask.tests.test_revising_intake`: four pass.
- `python3 -m unittest discover -s _ask/tests -p test_engineering_guard.py`: ten pass.

Ambient PYTHONPATH/PYTHONHOME were removed and bytecode disabled. The additional boundary/recovery timing probes also passed. These are reviewer exploratory executions, separate from retained candidate evidence.

## Retained red/green and machine binding

Current registered test-only red `570a0c60346c4f56f00186552b0ddade14f2600b`, run `0a35488281d041d9ad7814e67a4c2070`, has one genuine association behavior assertion failure and three passes. It preserves real local recovery writing and schedules the foreign external save afterward, asserting refusal/rollback/pointer preservation. Exact b215 final green `15ddaf0cd3c14c1680af4bbf6f05965f` passes all four. Latest red/final test bytes are identical.

Canonical coordinator ledger/report digests, retained execution-log hashes, every immutable case-source digest and red ancestry independently verify. Earlier original and remediation assertion history remains preserved, without exemption, regression relabel or weakened assertions. TaskResult was observed binding b215/base ec1/current pair. Ownership remains the blocker despite genuine execution evidence.

Exact evidence paths:

- `work/revising-workbench/inner-loop/results/RWB-103.json`
- `work/revising-workbench/traceability/runs/0a35488281d041d9ad7814e67a4c2070/results.json`
- `work/revising-workbench/traceability/runs/15ddaf0cd3c14c1680af4bbf6f05965f/results.json`

Machine input `work/revising-workbench/traceability/RWB-103-review-input-b215ab9.json` contains complete accepted-contract source/inventory and exact task/candidate bindings, all semantic decisions approved, `semantic_decision: APPROVED`, `boundary_decision: REJECTED`, `boundary_reason: glob_too_narrow` and overall `decision: REJECTED`. `review_errors` returns zero because that parser checks semantic/source bindings rather than the independent ownership gate. **Zero semantic parser errors do not authorize integration while ownership is rejected.** Obtain the narrow reviewed amendment/pin and a review bound to its resulting candidate/authority before proceeding.
