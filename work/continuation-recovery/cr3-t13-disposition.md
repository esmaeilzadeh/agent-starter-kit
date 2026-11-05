# CR-T13 guard classification for P1

CR-T13 is a regression guard, not a bug-reproduction case. It has no Red
requirement. Run
`b5e4fc3b34c14e5a93312d2744be9adf` records the case as a setup/runtime error;
Red-phase run `f8207e36d1794b499e043ba263cacb32` records it as passed; and the
P0 Green run `6d36ea28edae44768e7e01e175a91d8a` also records it as passed.
None of those outcomes is a behavior assertion failure for CR-T13.

The P0 scenario text claimed two reopen cycles. Its mapped test,
`RecoveryTests.test_guard_rollback_and_explicit_attempts`, invokes the one-cycle
`test_interrupt_and_reopen_preserve_attempt_history` path once. It therefore
does not demonstrate a second transition. That mismatch does not establish a
bug: CR-T13 is a one-cycle guard for explicit reopen authorization and history
preservation. No two-cycle defect is claimed or assigned to CR-T13.

P1 retains the test only as a regression guard for the one reopen cycle it
actually runs, changes its scenario to match that behavior, and classifies it as
`regression`. It is not included in P1 historical Red continuity. The actual
consumed-receipt selection and stale-request atomicity defect remains CR-T60;
valid behavior Reds are recorded in `e2a9dc4b3d5e41789117fae0b9623e93` and
`f8207e36d1794b499e043ba263cacb32`, with P0 Green in
`6d36ea28edae44768e7e01e175a91d8a`.
