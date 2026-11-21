# CR-3 reviewer request: amendment proposal revision 5

Please review `CR-3-plan-amendment-proposal-revision-5.md` and return
**APPROVED** or **REQUEST CHANGES** with findings. This is proposal review,
not human scope approval, accepted-plan approval, TaskResult approval, or
authorization to reopen. CR-3 remains interrupted.

Focus on:

1. Whether coordinator `checkpoint-run` validates current P1 authority
   separately from original historical authority, while allowing only P1-
   declared historical Red and retaining unchanged run summaries.
2. Whether P1's continuity inventory covers the original T10/T19 Red (and
   applicable T20/P0 Red) at per-case assertion scope, without upgrading
   passing cases or T10's corrected observer assertion to Red.
3. Whether the disposable end-to-end test proves P0 Red survives P1 acceptance,
   preflight, reopen and coordinator checkpointing, with negative controls for
   undeclared/altered evidence.

Distinguish current behavior from proposed implementation. Do not modify the
accepted plan, coordinator state, receipts, reports, ledger, or source while
reviewing.
