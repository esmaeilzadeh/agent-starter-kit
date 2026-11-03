# CR-3 T21 provenance correction

This note corrects the T21 assertion lineage in
`CR-3-red-provenance-audit.md` and `CR-3-plan-amendment-proposal.md`. Those
historical notes remain unchanged so the correction is attributable. No run
report, ledger entry, accepted plan, or task state is rewritten here.

The mapped T21 test method first appeared in test-only commit `3196a59` with
the pinned-runner byte assertion. Commit `5969c3e` added assertions for actual
old-runner execution, the completion receipt, finalization, and malformed
schema handling. The relevant production changes preceded those latter
assertions: `fc43143` and `c2262d1`. Commit `37847b0` seeded verifier
configuration. Commit `ae31e20` added fixture semantic-review prerequisites;
it did not introduce the mapped T21 assertions.

Registered Red-phase run `517f864631a845e082f9a73fa888ef30` passed all eight
mapped cases. The other cited Red-phase runs also report T21 passed. Diagnostic
overlays are not immutable registered executions. The reviewed evidence
therefore establishes no valid T21 Red. Retain the reports and phases as
recorded; do not infer Red from implementation chronology or relabel a run.

The only proposed resolution is an explicitly approved and executable
CR-T21-specific exception. CR-T21 remains `new`; its assertions remain
mandatory; exact-candidate Green and independent semantic review remain
mandatory; and no Red-to-Green claim is made.
