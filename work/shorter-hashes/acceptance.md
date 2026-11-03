# Acceptance — 2026-11-03

**ACCEPTED directly at 95% confidence.**

## Workstream and specification

`shorter-hashes`: compact numeric workflow references, exact dependency and
integrity preservation, and the authorized selective projection redesign.
Specification: `specs/current/shorter-hashes.json`, revision 7 (SH-01–SH-18).
Approved intent SHA-256 remains
`8784f3748505fe0ac51ccb9a7dfe78de0c04f79cd26dac58689fdee10cb084e6`.

## Authority and accepted source

The user instructed: “review and accept if more than 90 percent are you certain”.
Coordinator `/root` records that the condition is met. AskIt's highest-priority
self-development rule keeps the kit disabled and permits direct work without its
stage gates. This acceptance uses that rule and actual independent reviews; it
does not manufacture normal kit completion, review authority, or Red history.

Accepted candidate: `36b06f3bfa846e6d168a74ebb57aaf8c9fa62a95`.
Following commits retain evidence and this decision.

## Evidence

- `review.md`: independent standards/correctness approval at 95% and specification
  approval at 96%, both for the accepted candidate.
- `direct-acceptance.json`: candidate, reports, execution identities, counts,
  exact broad-to-final source difference, and preserved historical-result digest.
- Final isolated reference execution: **47 methods passed, 14 runners exited 0**.
  Its 49 raw rows include two legacy `unsupported_subtest` diagnostics.
- **39 mandatory broad checks passed** on `18997d2`; final source changes only
  test import setup. Full raw output and its failing formal-completion result are
  retained under `acceptance-evidence/`.
- `benchmark/results/direct-acceptance/report.json`: fresh accepted-candidate
  replay; all three frozen journeys preserve equivalent evidence. Agent-input
  tokens **16,598 → 14,178**; JSON metadata bytes **195,626 → 154,054**. All 60
  fresh output files match the retained raw archive exactly. Non-JSON bytes
  **43,219 → 53,532** are reported separately and do not offset either threshold.

## Residual risks and procedural limits

Markdown/YAML projection targets the repository's supported table and TaskGraph
forms. This review does not claim generic YAML or Markdown parsing.

The legacy adapter cannot represent the existing successful waiver subtests as
accepted cases. Formal completion also requires candidate-bound semantic records
and legacy task state. The broad command refused completion after HEAD advanced
by the fixture-only correction; its failed outcome is preserved. The earlier
`result.json` stays byte-identical. These disabled workflow gates are not claimed
as passed, and historical task states are not relabeled.

## Context-engineering review

The frozen evidence-equivalence replay and independent source/specification
reviews support this direct decision. A separate kit-stage context audit was not
run while the kit was disabled.

## Acceptance decision

Accepted under the user's delegated confidence condition and self-development
rule. Implementation and direct review are complete. Integration into another
branch is a separate action.
