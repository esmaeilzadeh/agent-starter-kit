# CR-3 amendment decision proposal — revision 5

**Review status:** historical-evidence amendments prepared for reviewer
review; no human approval is requested yet. CR-3 remains interrupted. This
revision supplements and supersedes the historical-evidence portions of
revision 4. Its read-only preflight, P0/P1 ordering, T10 observer correction,
and receipt lifecycle sequence remain in force. No accepted plan, state,
receipt, historical report, or ledger record is changed by this proposal.

## Historical Red must pass through coordinator finalization

The current `_execution_row` path calls `load_accepted` against the live P1
pin and demands the report's plan digest match that live plan. It therefore
rejects an original-plan or P0 Red before `_checkpoint_run_locked` can attach
it. P1 must explicitly authorize a narrow historical-Red branch shared by
preflight, report selection/completion, and coordinator `checkpoint-run`.
Do not change `load_accepted` globally, rewrite the historical run, or treat
old authority as current authority.

For every task-scoped Red being carried into P1, its P1 continuity row names:

- exact `run_id`, original Red phase, task/scope, candidate SHA, report-file
  SHA-256, report's canonical digest, and canonical ledger-row SHA-256;
- original accepted-authority commit SHA, accepted-document digest, original
  contract SHA, spec digest and plan digest;
- original mapped test ID/case ID and the contract fields at that original
  revision (criteria, type, runner/selector, scenario, assertions and source
  paths);
- original assertion identity and the exact assertion continuity assessment
  against the P1 test. Bind the source file digest at the original candidate
  and at P1, plus a stable assertion fingerprint/AST digest for the specific
  assertion statements. A semantic reviewer separately approves that mapping.
  A changed or newly added assertion is excluded even when the case ID and
  source filename are unchanged.

P1's independent review and accepted document authorize the set of these
exact run rows. The coordinator validates the current P1 accepted authority
separately from each original run's authority. For an historical Red only,
it then loads the exact original accepted document named in the P1 row,
verifies that document and its contract chain, confirms the old candidate
contains that original accepted document, validates the report against that
original spec/plan and pinned runner, and checks the report and canonical
ledger row against the P1 row. The original accepted commit must be an
ancestor of the P1 accepted-authority commit; the original contract SHA must
be an ancestor of the old run candidate; and the old candidate must be an
ancestor of the active CR-3 attempt lineage. The current P1 acceptance remains
the authority for present work; historical authority is consulted only for
the exact explicitly listed Red.

The historical branch is permitted only when the report phase is `red`, the
run ID and all original identities exactly match one P1 continuity row, and
the declared case has unchanged contract/assertion continuity. It validates
only failed mapped cases with `outcome=failed` and
`failure_kind=behavior_assertion`; passing cases included in the same failed
runner report gain no Red. It cannot admit `final_green`, another task, another
case, an undeclared run, or an altered report/ledger/source. Current Green
continues through the normal P1 path: its candidate must contain the current
P1 acceptance document, match current P1 contract digests, and equal the exact
candidate being reviewed.

After validation, `checkpoint-run` records the original run summary unchanged:
original run ID, phase, candidate SHA, report digest, spec digest and plan
digest. It does not rewrite a P0/original digest to P1. The same shared
validation helper is used by read-only preflight and completion report
selection, so all three surfaces apply the same allow-list and per-case
continuity rules. Existing full active-base, runner, candidate-lineage,
recovery-safety and checkpoint CAS checks remain mandatory after reopen.

## P1 continuity inventory must include original T10 and T19 Red

P1 must list the original retained Red evidence needed by its current CR-3
cases, as well as eligible P0 Reds for newly added verifier/bootstrap cases.
At minimum, the reviewed inventory includes:

| Current case | Original Red run | Original candidate | Original plan digest | Admissible assertion scope |
| --- | --- | --- | --- | --- |
| CR-T10 | `b50dd24e0ef04a2aacff4c4a26db4dd5` | `3196a591e2ee0c75ee0bda1539a9319555273662` | `2ddca16503e68dc640b51b9a4d5ddb8dab79e75b16fd1eec04bc9de012958aa0` | Only the original run-finalization assertion that failed in this run; the later `afc7ab2` post-report-publication observer correction is not covered. |
| CR-T19 | `f21a95f6b4c4499aacf37a3ffd27a77d` | `94458d8376a75f052adbf2c4737f4f3c18cef4b6` | `2ddca16503e68dc640b51b9a4d5ddb8dab79e75b16fd1eec04bc9de012958aa0` | Only the exact nested-verifier assertion recorded as `behavior_assertion` Red in this run. |
| CR-T20, if retained unchanged in P1 | `b50dd24e0ef04a2aacff4c4a26db4dd5` | `3196a591e2ee0c75ee0bda1539a9319555273662` | `2ddca16503e68dc640b51b9a4d5ddb8dab79e75b16fd1eec04bc9de012958aa0` | Only the CR-T20 assertion recorded as `behavior_assertion` Red in this run. |

The original accepted authority for these runs is contract SHA
`588c6cd9f3585eeb77d8a745abfc8d1a96b73cb6`, accepted-authority commit
`14d8bbe20c5f3d24082c13ef98a29e80ac019b92`, and spec digest
`02dcf36a73bbaf4c100e413854e823518f14d3dcbed34fe47a333d8e65790cf1`. The
exact accepted-document digest, report-file digest, canonical report digest,
canonical ledger-row digest, case contract digest and assertion fingerprints
must be computed from the immutable source artifacts and included in P1; do
not copy the abbreviated table values as substitutes for those checks.

For run `b50dd24e0ef04a2aacff4c4a26db4dd5`, the existing ledger row names
report digest `9a504f6ceb1bdf13132b5b4ab55af767f791f3972ceeff1095ae8f894445cd2c`;
the report file SHA-256 is
`816a709d25d8804fa9084cddb668716670400e76989e8d81a81443f576760b91`. For
`f21a95f6b4c4499aacf37a3ffd27a77d`, the ledger report digest is
`8247cafd4ee6781ce3bdc73416d1106765611406f84f2ac9c9c9b789ca0b80be`; the
report file SHA-256 is
`c77282428ed992e31e086f9cf61ecb809d8ba575e002321b292461ece1f31d81`.
The canonical ledger-row SHA-256 and all source/assertion fingerprints are
separate values; compute and bind them exactly in the reviewed contract.

The same P1 inventory contains eligible P0 Red rows for the newly added
receipt lifecycle, preflight, T21 enforcement and continuity tests, each bound
to its own P0 accepted authority and mapped assertion. Do not let a P0 run
stand in for the original T10/T19 Red. Do not admit a report-level failure as
Red for every passing case in that report. Do not rewrite any report, ledger
row, phase or original accepted pin.

## Coordinator `checkpoint-run` behavior and required mapped test

Add the historical-Red branch to the shared run validator used by both
`_execution_row` and `_checkpoint_run_locked`. `checkpoint-run` keeps its
existing command and active task requirement. It first validates current P1
authority and the active attempt-3 base/lineage. For a P1 Green it uses the
normal P1 validation path. For a declared historical Red it applies the exact
P1 row and original-authority checks above, then writes the unchanged summary
into the checkpoint. No caller-supplied digest, base, plan, or authority may
select the historical branch; the current accepted P1 contract and its exact
continuity table select it.

The P0/P1 mapped tests must include an end-to-end disposable coordinator
scenario that performs these operations in order: publish a P0 Red into the
fixture's real traceability runtime; accept P1 with that exact run explicitly
declared; run preflight while the task is interrupted; reopen through the
coordinator; invoke `checkpoint-run` for that same original P0 run; and assert
that the retained checkpoint contains the original ID, `red` phase, candidate,
report digest and P0 contract digests unchanged. Use real coordinator code and
the normal immutable report/ledger formats. This is fixture-isolated test
evidence, not a copy into the live workstream ledger.

Negative controls must prove `checkpoint-run` and preflight refuse an
undeclared run, changed case/assertion fingerprint, changed report or ledger
digest, invalid original accepted commit, non-ancestor candidate, wrong task,
and any historical `final_green`. For T10, a P1 continuity entry must admit
only the original assertion and reject treating the `afc7ab2` observer
correction as historical Red. P1 current Green must still pass the ordinary
P1/current-candidate path. Map exact selectors/source paths and ownership for
the new finalization logic and tests under CR-3 before accepting P0; this
extends the proposed CR-T59 continuity coverage and keeps the CR-2 → CR-3
dependency serialized.

## Updated preflight, P1 Green, and reopen sequence

Revision 4's preflight and P0/P1 phase order remain, with these changes:

1. P1 continuity rows include CR-T10's original Red, CR-T19's original Red,
   CR-T20's original Red if its mapped contract remains unchanged, and each
   eligible P0 Red. Every row binds its own original accepted authority,
   contract, run, report, ledger, case and assertion identities.
2. P1 exact Green remains a current-P1 run on the exact candidate. P1
   completion report selection admits historical Red only through the
   explicit per-run/per-case table. P1 worker-mode Green publishes normally.
3. Read-only preflight validates all original/P0 Red rows through the same
   historical-aware helper that finalization will call, but does not mutate
   state or ledger. It validates P1 Green through the ordinary current-plan
   path.
4. After the reviewed attempt-2 → attempt-3 receipt and coordinator reopen,
   call the existing `checkpoint-run` for each declared original/P0 Red and
   the P1 Green. This is where historical P0/original reports are validated
   against current P1 authorization plus their own original authority, then
   attached with unchanged summaries. Preflight does not replace this check.

The final independent review binds the P1 contract, historical rows and
assertion fingerprints, P0/P1 run records, preflight assessments, exact
attempt-3 checkpoint, and semantic review. No aggregate completion or
integration is claimed before those checks pass.

## Reviewer response requested

Please review the historical `checkpoint-run` path and the explicit T10/T19
(and applicable T20/P0) continuity inventory. Confirm that current P1
authorization stays separate from original authority, original summaries
remain unchanged, and the end-to-end fixture covers P0 Red through P1
checkpoint. Return **APPROVED** or **REQUEST CHANGES** with remaining gaps.
This is not human scope approval. Until the separate scoped amendment choice
is submitted, make no plan, source, verifier, state, receipt, report, or ledger
changes.
