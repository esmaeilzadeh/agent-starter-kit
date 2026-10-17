# Independent RWB-101 remediation review

**Verdict: REJECTED. Boundary: APPROVED.**

Reviewer `/root/review_revising_plan`, gpt-6.1-sol / high, Codex. Exact candidate `7345a2f6836d27c60bb18da1701963c22bea6619`; accepted contract base `f563e619c5c809cdb39072941fab4c2626284f64`. Original rejected review remains preserved. No source changes, commits, refs or state mutations by reviewer.

## Resolved findings

- F1: Coverage now compares declared Test path with qualified source work, source plan work ID, exact digest and unique case. Contradictory other-plan path/product identity is rejected; valid explicit reviewed cross-work mapping remains covered by a separate positive assertion.
- F2: Local mapping case IDs require nonempty text and unique local lookup; external selectors require exact slug/digest/case shape. Original malformed-list mapping repro now diagnoses.
- G1: Assigned qualified-ID case now checks tracker/later metadata cannot infer execution, explicit pair alone joins, reference input remains unchanged, and declared done creates no execution/verification evidence fields. These are bounded unit checks, not a new model metadata schema.

## Remaining blocker: F3b

The event-list crash is repaired, but historical_option_ids iterates historical options before checking the container is a list. Known event plus options null/bool/int and nonempty resolution still raises TypeError. Same malformed-history diagnostic obligation remains incomplete.

Reproduced in a temporary Git archive of this exact SHA, isolating the parallel writer. An open v2 decision can have valid node options and this retained history entry:

```json
{"event":"resolved","actor":"a","rationale":"r","timestamp":"2026-10-16T00:00:00Z","options":null,"resolution":{"option_id":"a","actor":"a","rationale":"r","timestamp":"2026-10-16T00:00:00Z"}}
```

`validate` raises `TypeError: NoneType object is not iterable`; `options: false`, `true`, `0` and `1` do likewise. The helper records an options diagnostic but then iterates the invalid container. A 180 single-field JSON-shape matrix and 144 options/resolution cross-product isolate this remaining class; no other throw class appeared in that bounded matrix. Guard the container before iteration and retain typed negative assertions for the malformed-history class.

## Evidence and continuity

Verified canonical ledger/report digest, retained log byte digests and source digests for complete test-only red fc4ada5a75a0d754980e8754afbdcc033947e4f1 / run119605e866364b99af2eca6931ae4844 and final candidate green ef814a0daffc4e809da5dab191b3a768. Red has three behavior assertion failures/eight baseline passes; final green passes all11. New test/fixture source is byte-identical red→green. Strengthened tests preserve the preceding graph/identity/flow assertions. The green record does not override F3b.

The v1 validator body is preserved; shared decision helper gains scalar type checks instead of weakening original allowed options/history/resolution semantics. Eight task regressions remain unchanged and pass fresh green.

## Structured scope and boundary

Machine input contains exact task scope, six selected criteria and assigned required types, all11 per-case assertion/counterexample/continuity decisions, canonical source digests and accepted-base Python inventory. EM001/EM014 unit and RWB-V2-GRAPH are rejected for F3b; remaining task decisions are approved. No unmapped changed test methods or exclusions. Boundary remains approved: all task source changes use owned RWB101 paths; coordinator state bootstrap is explicitly permitted. Future passage/intake/migration/browser/human obligations are not claimed.

Required: test-only assertion red for the malformed-history container matrix, source correction, final green at corrected SHA, and fresh independent review. Do not integrate this candidate.
