# RF-01 check-plan ordering conflict and recovery

The original RF-01 candidate `9bd14251fa2c391433cbfd4788133dfc4026f208`
passed all shell checks but failed the mandatory traceability entrypoint case
because the canonical Grill/continuation changes had not yet been projected to
the generated stage bundles owned by RF-03 in the original graph. This is an
ordering conflict, not an implementation defect. The exact failure is retained
under `verify-k6v7dh0_` and `verify-saxt9thy`.

The plan amendment at `7ee9881eef11c46f040fba1f6520cde053bbec77` moves stage
projections to RF-01 and is independently approved. `RF-01` runtime state is
being reopened at the new accepted-plan candidate after the obsolete first
attempt is retained here. No Git source history is reset or discarded.

Coordinator recovery used the state transaction API after `accept-plan` advanced
at the approved amendment. It archived the canceled first attempt, reset only
RF-01's runtime status to pending, and re-anchored coordinator SHA to
`a2ad10ee607e2c750c770aaf5afed0ec9059e16a`. This preserves the failed check
record and all Git commits while letting the amended, independently reviewed
graph run from its accepted contract.
