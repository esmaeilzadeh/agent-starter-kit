# CR-3 reviewer request: amendment proposal revision 3

Please review `CR-3-plan-amendment-proposal-revision-3.md` and return
**APPROVED** or **REQUEST CHANGES** with findings. This is a review of the
proposed amendment and evidence path, not approval of the human scope decision,
not acceptance of a plan, and not a TaskResult review. CR-3 remains interrupted.

Please focus on these questions:

1. Does the T10 observer-correction treatment correctly preserve the old
   Red/Green scope, avoid a manufactured product failure, and use the negative
   control only as test-sensitivity evidence rather than TDD Red?
2. Is the proposed T13 bootstrap Red/Green sequence authentic and executable
   against the accepted amended contract while task state remains interrupted?
3. Does `ASK_INNER_LOOP_ROLE=worker` with the real coordinator root preserve
   sufficient run provenance, and will the real coordinator's later
   `checkpoint-run` validate and recognize those exact report/ledger records
   after reopen? If not, identify the smallest coordinator-owned mechanism
   needed. Do not recommend manual report/ledger/state edits or weakened
   identity checks.
4. Does the receipt sequence bind the exact attempt-2 → attempt-3 transition,
   preserve consumed receipt/attempt history, and prevent stale requests from
   mutating state?
5. Are T21's exception enforcement, cross-plan historical Red continuity,
   CR-T12 regression classification, exact ownership, and independent review
   bindings sufficiently bounded and testable?

Please distinguish confirmed behavior observed in the current implementation
from proposed behavior that still requires implementation and mapped tests.
Do not change accepted contracts, state, ledger, reports, receipts, or source
while reviewing.
