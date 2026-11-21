# Independent review: Task 9 attempt 1 preservation

Decision: **APPROVED** at 98% confidence.

Reviewer: `/root/review_task9_amendment` (Codex). Reviewed exact proposal
commit `557039f2d25dedcf8cfdfde41508591eaa6477bd`; proposal SHA-256
`c0140883f1b1a27531b434d384ba7478a2a980ff2935639ad54aeaa678ca2467`.

The reviewer verified all four archived files against their live sources,
and confirmed run `cf5d501d1a904f4a9c53a238f272de64`, execution
`b5ca8fdf66fb4841aae28dc9908ca5e6`, and candidate/source
`9e381599cc11fabe26b8a0a3a8d92d076dcfd9d2` agree across report, execution,
log, and ledger. Collection succeeded and execution exited 1. Actual outcomes
are: 9/1 and 9/5 passed; 9/3 failed as a `behavior_assertion` with
`comparison_incomplete`; 9/2 and 9/4 ended with `setup_or_runtime_error`.
These outcomes remain unchanged; the failed Green is neither Red nor passing
completion evidence. The ledger's canonical report digest is
`89d59fa6db8973bc5bc82b7ebf37b54d4c20d8d451c0dac91b3e91472a1e1168`, and
the process waiver binding matches
`5b75b36681cf78fc41a6e2646271db974fc93479feed9a4642994f27f2d1bded`.

Before recovery, preserve the waiver and execution ledger in the new
checkpoint, explicitly link the archive files and failed run from interrupted
attempt history, and recheck preimages under the state lock. Keep the exact
TaskResult bytes, including its now-stale pending-Green note; add truthful
linkage around it rather than rewriting it. Archive/remove only the live
obstructing TaskResult path, checkpoint coherent state, then use supported
interruption. Preserve original base, candidate, authority, attempt identity,
and evidence. Reopening under the amended graph must create attempt 2.

No behavioral tests or runtime mutations were performed as part of this
review. Approval covers only the preservation proposal; runtime consistency,
registration, implementation, and verification remain outstanding.
