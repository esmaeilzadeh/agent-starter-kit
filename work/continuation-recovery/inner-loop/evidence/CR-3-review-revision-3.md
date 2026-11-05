# CR-3 revision 3 review

Verdict: **REQUEST CHANGES**. Date: 2026-10-23.
Review target: proposal and questions committed at `625d07a`.
Reviewers: `/root`, with independent read-only implementation/policy assessment
from `/root/policy_review`. This is proposal review, not human scope approval,
accepted-plan review, TaskResult approval, or authorization to reopen.

## Supported conclusions

- T10's observer correction is appropriate in principle. Preserve the old
  assertion scope and registered history; require corrected exact-candidate
  Green and a negative control that distinguishes the stale snapshot from the
  corrected observer. The negative control is sensitivity evidence, not Red.
  The amended continuity implementation and semantic review must enforce that
  distinction; existing code does not acquire those semantics from this note.
- Worker-role `traceability run` really does publish coordinator-root reports
  and ledger entries while skipping automatic checkpoint finalization
  (`.agents/ask/verification/traceability/cli.py:101-125`, `adapters.py:21-83`).
  The case execution is detached; these are actual workstream runtime records,
  not fixture reports imported into the ledger.
- Subsequent `checkpoint-run` can recognize a preexisting run after reopening:
  it validates the report and compares its canonical ledger row, then records
  the original summary (`_ask/scripts/inner_loop/evidence.py:327-383`). There
  is no requirement that report creation occur after the attempt starts.
  Recognition remains conditional on accepted contract, candidate ancestry,
  source/output identities, active base and runner digest, and recovery checks.
  No end-to-end bootstrap has been executed by this review.
- The CLI hashes its executing `unittest_runner.py`; it does not automatically
  select that file from the task base. Finalization compares that digest with
  the base version (`evidence.py:194-203`). They are identical at this review's
  HEAD and `2c508ff`. Keep that equality explicit; worker mode is not itself
  evidence of base pinning. The candidate must also contain the current
  generated acceptance document, not merely use a valid CLI anchor.
- The proposed distinct receipt and exact transition bindings address the
  original lifecycle defect in design. The actual receipt-selection/history
  changes still need implementation, authentic Red/Green and independent review.
  T12 classification and corrected T21 provenance remain supported.

## Required changes

1. **P1: step 4 has no current pre-reopen validator.** It promises real
   coordinator validation while CR-3 remains interrupted. `_execution_row`
   loads live task state and rejects an empty `base_sha`
   (`evidence.py:160-165`); interruption clears that field
   (`attempts.py:253`). Worker publication does not bypass or satisfy this
   requirement. Do not inject temporary running state.

   Specify a minimal coordinator-owned, read-only preflight sharing the run
   validation logic. It must derive the prospective base from the retained
   coordinator and bind checkpoint/revision, interrupted attempt, next attempt,
   accepted authority, and clean candidate; arbitrary caller-supplied identity
   must not become authority. Add exact ownership, mappings and negative tests.
   Preflight must not record a milestone, alter the ledger, or mutate state.
   Keep normal post-reopen checkpoint validation mandatory. An alternative is
   to explicitly limit pre-reopen checks and defer full validation until after
   reopen, but then revise the claimed gate and obtain review of that changed
   sequence; do not claim existing full validation works while interrupted.

2. **P1: step 3 requires full Green before scheduling the verifier work.**
   It permits only the receipt correction and mapped tests, yet requires all
   amended CR-3 cases to pass. The same plan adds T21 exception-enforcement and
   historical-continuity cases, with production changes missing from the
   ordered sequence. Add explicit authorized Red/Green implementation steps
   for those behaviors (and the preflight, if selected) before requiring full
   task Green. Explain which verifier revision executes and enforces each
   phase, including initial plan acceptance versus later exception validation.
   Alternatively define a separately reviewed bootstrap scope with an explicit
   route to the complete contract. Do not drop mapped cases, accept absent
   assertions, or describe a partial run as full task Green.

## Next handoff

Revise these two sequence gaps only; preserve the supported worker-publication
and post-reopen finalization design. No new deferred *finalization* operation
is shown necessary by the current code; the missing operation is the promised
pre-reopen read-only validation. Keep CR-3 interrupted and prepare the concrete
sequence for review before requesting the human's scoped amendment decision.
T21 exception enforcement and historical continuity remain proposed changes,
not confirmed existing behavior. This review does not approve their final
contract or implementation.

Read-only checks: clean worktree at entry, source inspection, and an empty
runner-file diff between `2c508ff` and review HEAD. No behavioral runs or
coordinator mutations were executed. Before committing this note, verify that
state, accepted contracts/refs, receipts, original reports and ledger retain
their prior identities. This documentation commit is not workstream completion.

Standards: one blocking gap in the promised pre-reopen validation gate.
Spec/execution sequence: one blocking gap in the full-Green prerequisite order.
