# CR-3 amendment decision proposal — revision 3

**Review status:** revised for reviewer review; no approval is requested yet.
CR-3 remains interrupted. This proposal leaves the accepted plan, coordinator
state, historical execution reports, and prior reconciliation receipt
unchanged. It refines revision 2's T10 requirement and makes the bootstrap
evidence/authority sequence explicit. Revision 2 remains preserved.

## T10: correct the observer without manufacturing a product failure

CR-T10 remains `new` and keeps its current mapped selector, criteria, type,
and behavior assertions. Its registered Red/Green history continues to cover
the assertion contract that existed at those candidates. The one-line change
in `afc7ab2` reloads the execution ledger after the child exits at
`after_report_publication`; it corrects a stale test snapshot. The implementation
already leaves the run uninserted at that boundary. Requiring the corrected
observer to fail against that correct behavior would manufacture a product
failure, so no new Red is required for this observer correction and no run is
to be relabeled or fabricated.

The amended test mapping and review must call out this narrow **observer
correction**, distinct from a behavior change or generic TDD exemption. Its
evidence is:

- preserve the existing registered CR-T10 Red/Green reports exactly as they
  are, with their original digests and assertion scope;
- run the corrected test on the exact candidate and require passing Green;
- exercise a test-only negative control using a disposable ledger fixture with
  the same run ID already inserted. The corrected post-exit assertion must
  reject that fixture, proving it observes the publication boundary. This is
  a test-sensitivity check, not product Red, not a registered Red-phase run,
  and not a substitute for any other CR-T10 obligation;
- require independent semantic review to bind the old assertion-source
  identity, corrected source digest, negative-control fixture/result digest,
  exact-candidate Green report, and the conclusion that the production
  behavior was already correct.

No failure is induced in production, and the negative-control result is never
recorded as a behavior failure. If reviewers find the negative control cannot
distinguish the stale-snapshot implementation from the corrected assertion,
stop and revise the test oracle; do not make production behavior fail to obtain
Red. The existing `CR-T10` mapped behavior and every other TDD obligation stay
unchanged.

## Bootstrap: exact evidence and authority sequence

The current fixed receipt is stale for attempt 2 → attempt 3. The proposed
`attempts.py` correction must distinguish consumed receipt history from a new
transition request, preserve the old receipt bytes/digest and both attempt
records, and reject a stale or edited new request before state/checkpoint
mutation. The sequence below is part of the proposed acceptance contract;
steps 1–8 do not run until the scoped amendment is approved.

1. **Accept the reviewed plan while still interrupted.** Commit mutually
   consistent plan, graph, and test mapping; obtain independent `APPROVED`
   plan-review JSON binding exact contract SHA plus canonical spec/plan/graph
   digests, prior accepted digest, human decision reference, reviewer identity,
   T21 exception, T10 observer correction, continuity declarations, and this
   bootstrap sequence. Validate and accept through the normal coordinator
   `traceability validate-plan` / `accept-plan` operations. Read back the
   accepted ref/seal and verify it differs from attempt 2. Do not reopen.

2. **Create an authentic test-only Red for the bootstrap regression.** The
   revised graph/test plan must map the new T13 repeat-transition assertion to
   an exact CR-3 selector (and exact source ownership). Commit only the test
   change on the coordinator branch as a descendant of the recorded
   coordinator base. Run the official traceability CLI against the real
   coordinator root and that committed candidate, with
   `ASK_INNER_LOOP_ROLE=worker`, task scope, CR-3, and phase `red`. The
   traceability adapter executes the candidate in its normal detached Git
   worktree, while publishing `results.json`, execution logs, and the
   append-only ledger entry under the real
   `work/continuation-recovery/traceability/` runtime. Worker mode suppresses
   only automatic `checkpoint-run`; it does not bypass report creation,
   runner pinning, contract digests, source digests, or ledger validation.
   Capture the CLI run ID, report digest, ledger row, candidate SHA, runner
   identity, and exact failing `behavior_assertion`. If there is no genuine
   mapped assertion failure, or the CLI cannot produce a complete report and
   ledger row, stop. Do not hand-write either artifact.

   Example command shape (the values are filled from the committed plan and
   candidate at execution time):

   ```sh
   ASK_INNER_LOOP_ROLE=worker ./ask traceability run continuation-recovery \
     --candidate-sha <test-only-candidate> --anchor-sha <accepted-contract-anchor> \
     --scope task --task-id CR-3 --phase red
   ```

3. **Implement and capture exact Green the same way.** Implement only the
   reviewed receipt lifecycle correction in `attempts.py` plus its mapped
   tests. Commit the candidate. Run the same real-root CLI with
   `ASK_INNER_LOOP_ROLE=worker`, exact candidate, task scope CR-3, and
   `final_green`. It must pass every CR-3 case selected by the accepted task
   scope. Capture the generated run ID, report digest, ledger row, logs,
   candidate and source digests. Do not rewrite the Red report or ledger row.

4. **Validate both run records before reopening.** Use the real coordinator
   code to read each report and ledger row and verify schema, run identity,
   report digest, exact accepted spec/plan digests, candidate SHA, runner
   identity pinned at the task base, case inventory, source digests, phase,
   and outputs. The Red must contain the mapped T13 behavior failure; Green
   must contain all selected CR-3 cases passing at its exact candidate. Record
   these identities in the bootstrap evidence packet. This read-only
   validation does not add them to interrupted task state.

5. **Prepare the exact new reconciliation request.** With source committed and
   clean, construct a distinct attempt-2 → attempt-3 receipt binding the live
   checkpoint SHA and revision, attempt-2 ID and interrupted candidate,
   expected attempt-3 ID, new accepted plan ref/digest, coordinator base,
   candidate SHA, and canonical hashes for every post-interruption source
   change (including `afc7ab2`'s test edit). It also references the Red and
   Green run IDs and their report/ledger digests without embedding or changing
   those artifacts. The reviewer verifies the canonical receipt payload and
   candidate. `recorded_by` must differ from the independent reviewer. Preserve
   the old attempt-1 → attempt-2 receipt unchanged as consumed history.

6. **Reopen only through the real coordinator.** After the reviewed receipt
   passes `reopen` validation, call the coordinator's normal `reopen` command.
   The fixed prior receipt must be recognized only as history; the new request
   must match the exact next-attempt identity. Capture the resulting attempt-3
   ID, checkpoint revision, and coordinator SHA. Any mismatch aborts before
   proceeding.

7. **Have the real coordinator recognize the isolated execution records.**
   Now that CR-3 is running, call its normal `checkpoint-run` command once for
   each previously published Red and Green run ID. Do not copy reports from a
   fixture, edit the ledger, or write task state directly. The coordinator
   revalidates each exact report and canonical ledger row against the active
   task base, task lineage, accepted contract, base-pinned runner, run paths,
   report digest, case/assertion identities, and source digests, then folds the
   immutable run summary into the checkpoint. Red and Green must both be
   present with their original run IDs, phases, candidates, and digests after
   this step. If either run does not validate or the candidate is outside the
   task lineage, do not synthesize a replacement record; stop and submit the
   exact rejection for review.

8. **Review completion.** Obtain a fresh independent semantic review bound to
   the final source candidate, the checkpoint containing both runs, the
   T10 observer-correction evidence, T21's approved exception and exact Green,
   and all applicable verification receipts. Continue CR-3 only within the
   amended contract. CR-4 and integration remain gated.

This sequence uses the supported traceability behavior deliberately: the CLI
normally finalizes a task-scoped run immediately only when it is operating as
coordinator against a runtime root that has inner-loop state/ref. The explicit
worker-role Red/Green invocation writes authentic runs into the actual
workstream traceability runtime but defers task-state finalization while CR-3
is interrupted. The later `checkpoint-run` calls are the authority boundary:
only the real coordinator can attach those runs to the reopened attempt, and
it revalidates all identities rather than trusting the worker's assertion.
If implementation review determines that worker-role runs cannot satisfy the
real coordinator's validation after reopen, the proposal must add and test a
coordinator-owned deferred-finalization operation; do not transfer artifacts
or weaken validation as a workaround.

## Other proposed amendments retained from revision 2

- CR-T12 becomes `regression` narrowly, supported by run
  `b50dd24e0ef04a2aacff4c4a26db4dd5` at test-only candidate `3196a59`, where
  production under `_ask/scripts/inner_loop` matched task base `2c508ff`.
  Failed run `6a96d09a0d4c4394951b47fa33a14dd7` remains `final_green`.
- CR-T13 stays `new`; preserve its existing selector, criteria, type and
  assertions while adding the real repeated interrupt/reopen, immutable
  consumed receipt, and stale new-request refusal behavior. The new behavior
  receives genuine Red and exact Green as described above.
- CR-T21 stays `new`, with all assertions retained and the explicit, executable
  CR-T21-only exception, exact-candidate Green, and independent semantic review
  specified in revision 2. The corrected lineage is in
  `CR-3-t21-provenance-correction.md`; no historical Red is claimed.
- Add `attempts.py`, the exact traceability verifier modules, and dedicated
  tests to CR-3 ownership. Keep CR-2 → CR-3 serialized. Add mapped exact tests
  for T21 exception enforcement, cross-plan immutable Red continuity, and the
  bootstrap path; the graph, test plan and plan must name the exact selectors
  and source paths before independent review.
- Historical cross-plan Red is admitted only from plan-declared original
  accepted identities with validated immutable report/ledger digest, case
  contract and assertion continuity, candidate ancestry, and independent
  per-case assessment. T10's corrected observer assertion is not backdated to
  the old report. Preserve all reports and run phases byte-for-byte.

## Authority and preservation

This proposal does not itself authorize changes. Until a submitted approval of
the complete scoped amendment, do not edit accepted plan/contracts, task graph,
test plan, verifier code, `attempts.py`, task state, receipts, or run ledger.
The accepted plan remains
`a8c13188a26489e67173333ca4f69ac572f00836a3f32e77929ee82a1ff99025`; CR-3
remains interrupted. Existing reports, their digests and phases, both attempt
records, and the consumed reconciliation receipt remain immutable.
