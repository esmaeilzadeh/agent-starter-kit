# CR-3 revision 4 review

Verdict: **REQUEST CHANGES**. Date: 2026-10-23.
Reviewed proposal/questions: commit `9acf728`.
Reviewer: `/root`, with independent read-only assessment by
`/root/policy_review`. This is proposal review, not human scope approval,
accepted-plan approval, TaskResult approval, or authority to reopen.

## Previous findings addressed

The proposed read-only preflight derives prospective identity from retained
coordinator state instead of injecting an active base. Its explicit inputs,
no-write boundary, runner equality check and negative cases address the design
gap. It remains proposed behavior requiring implementation and tests.

P0 now authorizes and tests receipt, preflight, exception and continuity
implementation before demanding full selected-case Green. P1 activates the
T21 exception only after the updated acceptance binding and independently
reviewed human-decision reference are available. This addresses the prior
phase-order gap. Passing P0 execution is correctly distinguished from task
completion. T10's observer treatment and T12's narrow classification remain
supported. Exact paths/selectors and final authorization bindings still belong
in the subsequent concrete contract review.

## Remaining findings

1. **P1 — existing checkpoint finalization cannot admit P0 reports under P1.**
   Revision 4 extends preflight and report selection, then promises the existing
   `checkpoint-run` will attach P0 Red after reopening. In
   `_ask/scripts/inner_loop/evidence.py:183`, `_execution_row` calls
   `load_accepted(root, work_id, candidate, candidate)`. That loader compares
   the acceptance document in the P0 candidate against the live P1 authority
   (`.agents/ask/verification/traceability/evidence.py:73-77`), and also requires
   current contract ancestry and equality. The subsequent report comparison
   in `_execution_row:185-187` independently requires matching plan digests.
   Reopening restores an active base; it does not remove these mismatches.

   **Exact amendment:** explicitly include coordinator run finalization in
   the shared historical-evidence validation change. Keep the existing command
   and its full checks, but provide a narrowly authorized historical-Red branch:
   validate current P1 authorization separately from the original run's accepted
   authority and candidate contract, then enforce the exact per-case continuity
   declaration. Preserve original report/ledger IDs, phases, digests and summary
   identities. Current Green must still match P1 and the exact candidate.
   Do not weaken `load_accepted` globally or make historical authority current.
   Map a test that publishes P0 Red, accepts P1, preflights, reopens and checkpoints
   that original run, plus refusals for undeclared/changed historical evidence.
   Include this implementation before the P1 bootstrap relies on it.

2. **P1 — “only P0 historical Red” excludes required older evidence.**
   Revision 4's P1 exact-Green paragraph limits recognition to P0 historical
   Red. T10's original Red and T19's retained Red predate P0; the proposal's
   preservation language does not make them admissible under P1. P0 runs of
   already-correct behavior cannot replace those original failures.

   **Exact amendment:** enumerate P1 continuity declarations for each retained
   original assertion/run being carried, including T10 and T19, as well as P0
   Red for new slices. Bind each to its own original accepted authority object,
   contract, candidate, report and ledger-row digest. Apply the same explicit
   admission rules in completion, preflight and coordinator finalization where
   the run is attached. Preserve per-case limits: T10's corrected observer is
   not retroactively part of its old Red; passing cases in a failed report do
   not acquire Red. Verify actual assertion continuity before listing a run.
   Do not rewrite reports or claim they executed under P0/P1.

## Coordinator handoff

Revise these two historical-evidence admission gaps; retain the supported
preflight and P0/P1 design. No additional deferred-finalization command is
required by this finding: the existing finalizer needs an explicitly scoped,
tested historical-admission path. Keep CR-3 interrupted until the separate human
scope decision, exact plan review/acceptance and reviewed bootstrap gates pass.

Confirmed from current code: worker publication defers automatic checkpointing;
post-reopen finalization validates active base and immutable run identities;
current acceptance checks reject a historical candidate under a newer pin.
Proposed, not executed or approved: preflight, P0/P1 exception activation,
cross-contract continuity and historical checkpoint admission.

Validation: clean worktree at review entry, source inspection and staged
whitespace check. No behavior tests, acceptance operations, runtime transitions
or aggregate verification were run. State, accepted contracts/refs, reports,
ledger and reconciliation receipts were hash-checked for preservation before
this documentation-only commit. This is not workstream completion.

Standards/authority: one blocking historical-finalization mismatch.
Spec/evidence coverage: one blocking omission of pre-P0 Red provenance.
