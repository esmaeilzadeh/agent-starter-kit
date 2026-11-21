# CR-3 semantic test review

- Reviewed candidate: `516e47cf21939aa7675472f40df0c0208827e610`
- Reviewer: `/root/cr3_g01_independent_review`
- Decision: **REJECTED**

The reviewer ran the eight CR-3 mapped tests successfully in a disposable
fixture (8 tests, 55.740s), but found scenario-to-assertion gaps:

- **CR-T11** (`test_stale_review_preserves_execution`): the mapped wrapper only
  exercised a rejected review and candidate change. It did not prove that a
  valid approved review becomes unusable when its bound result changes.
- **CR-T12** (`test_crash_after_verification_or_ff`): the mapped method covered
  checkpoint-publication and post-fast-forward crashes, but not interruption
  after verification and before fast-forward.
- **CR-T13** (`test_guard_rollback_and_explicit_attempts`): its reopen assertions
  used synthetic Red ledger rows rather than archiving the same real Green
  already shown to resist generic rollback.

The reviewer also confirmed that CR-T12, CR-T13, and CR-T21 still have no
recognized immutable Red evidence. Run `6a96d09a…` is a failed `final_green`
attempt; run `517f8646…` has phase `red` but all cases pass; neither satisfies
Red. The reviewer advised resolving this limitation through the protocol and
not claiming a Red-to-Green history that is absent.

Other mapped-case assessments and the criterion/type coverage assessment are
preserved in the reviewer's response in the conversation. No state-mutating
coordinator operation was run for this review.
