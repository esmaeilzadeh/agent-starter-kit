# CR-3 reviewer request: amendment proposal revision 4

Please review `CR-3-plan-amendment-proposal-revision-4.md` and return
**APPROVED** or **REQUEST CHANGES** with findings. This is proposal review,
not human scope approval, accepted-plan approval, TaskResult approval, or
authorization to reopen. CR-3 remains interrupted.

Focus on:

1. Whether `preflight-run` derives the prospective base and all identities
   solely from retained coordinator state, validates reports/ledger without
   mutation, and has adequate negative cases and exact CR-3 ownership.
2. Whether P0 acceptance, Red, implementation, Green, P1 acceptance, exact
   Green and preflight form a consistent sequence where each verifier
   capability exists before it is relied on.
3. Whether P1 can safely carry unchanged P0 Red while refusing changed
   assertion/source continuity, and whether its human-decision binding makes
   the T21 exception active only after P1 acceptance.
4. Whether post-reopen `checkpoint-run` remains mandatory and can recognize
   the same worker-published reports with original IDs and digests under the
   active attempt-3 base.

Distinguish behaviors confirmed in current code from proposed behaviors that
still need implementation/tests. Do not change accepted plan/contracts, task
state, receipts, reports, ledger, or source while reviewing.
