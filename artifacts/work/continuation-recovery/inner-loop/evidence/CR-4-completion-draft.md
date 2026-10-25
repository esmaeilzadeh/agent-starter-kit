# CR-4 completion evidence draft

Implementation candidate: 622e89c879c1b09d4982b84b3327bcfcaa216059.
Independent reviewer: /root/final_review; APPROVED source, TaskResult and exact
proposal payload. The recorded task semantic review passed review_errors.

Implemented read-only legacy provenance audit/proposal CLI; task/result/run,
review and verifier provenance; exact preimage validation; honest missing and
checkout-only evidence; no product mutation or scheduling. Review correction
contains legacy checkout artifact reads within the repository, with traversal,
absolute-path and symlink regressions.

Pinned CR-4 report: 828faea9006a42c1b618d49f4906a79d; CR-T15 and CR-T16 pass.
All 32 recovery unittests pass in the broader run. Full verification pending.

Legacy adoption validation intentionally refuses recorded authority and task
state conflicts. That refusal is an audit finding, not repair test failure.
No product state, source branch, accepted-tests authority or schedule changed.
CR-4 ends at a reviewed proposal. Product integration/adoption is separate work.

The one-time CR-3/CR-4 kit exception is recorded in cr4-authorization.md. Preserve
canonical verification/completion output even when a mechanical historical-Red
or feature acceptance gate disagrees with that scoped human direction.
