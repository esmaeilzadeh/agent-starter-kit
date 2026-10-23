# Independent P0 plan review

Decision: **REQUEST CHANGES**
Reviewer: `/root/review_cr3_p0`
Reviewed candidate: `fff72663f723ac177eabc7cef4761bcce62b8c99`

## Bound identities

- Spec digest: `02dcf36a73bbaf4c100e413854e823518f14d3dcbed34fe47a333d8e65790cf1`
- Test-plan digest: `22bd36b5bc41f89038e26bcfcd11685987b410dbb94d71aac805f33d47d77cbe`
- Task-graph digest: `d7f6819c4990f4e416f693ff3a274e92c2b57b7ca78ef04c1c2e58d622d979f5`

All design-file byte digests in `plan-review-p0-request.md` match the reviewed
candidate. The P0 contract validators and graph checks pass. This review is
planning evidence only; it did not run behavior tests, accept P0, or mutate
runtime state.

## Finding

The P0 verifier selection is not authorized under the approved migration
proposal's requirement that migration authorization be validated by coordinator
code pinned at original base `2c508ff`. At that immutable base,
`_ask/scripts/inner_loop/evidence.py::verify_candidate` unconditionally passes
`identity['base_sha']` to `snapshot_runner`; it has no migration-record branch
or alternate verifier selection. P0 instead proposes changing
`verify_candidate` to validate P1 migration metadata and choose the verifier,
without explaining how that changed selector becomes trusted while preserving
the original-base restriction.

An independently reviewed verifier source commit bound later in P1 is
insufficient by itself: the selecting coordinator upgrade also needs an
explicit trust and authorization path. The original task base and historical
runner identities must remain unchanged.

## Supported elements

- T12's narrow regression reclassification retains its failed `final_green`;
  T11 and T14 retain their accepted classifications.
- T13 repeated attempt-history behavior and T60 receipt-request atomicity are
  distinct mapped outcomes.
- T58 keeps the exception inactive in P0 and confines P1 to the exact approved
  work/task/case, with current Green and behavior checks mandatory.
- T59 requires historical applicability, current Green, real `checkpoint-run`
  and normal integration; its migration assertion remains conditional on
  resolving the finding above.
- T61 is read-only, state-derived and uses the shared evidence validator.
- Selectors, task scopes, criteria, and exact source-path mappings are unique
  and coherent.

Deferring the verifier source commit identity until the P0 implementation
candidate exists is acceptable if P1 binds that exact commit/tree and review
before activation. This does not resolve the coordinator selector bootstrap.

## Required correction

Either identify an existing original-base capability that can authorize and
select this migration, or obtain a narrowly scoped human decision authorizing
an independently reviewed coordinator upgrade while preserving the original
task base and historical runner identities. Do not alter the base or infer
authorization from a candidate commit alone.
