# CR-3 amendment decision proposal — revision 4

**Review status:** sequence corrections prepared for reviewer review; no human
approval is requested yet. CR-3 remains interrupted. This revision addresses
only the two sequence gaps identified in `CR-3-review-revision-3.md`; the
supported T10 observer correction and worker-publication/post-reopen
checkpoint design remain as stated in revision 3. No accepted plan, state,
receipt, historical report, or ledger record is changed by this proposal.

## Gap 1: pre-reopen validation with no active task base

Interruption clears `task.base_sha`, so existing `checkpoint-run` and
`_execution_row` cannot fully validate the worker-published Red/Green records
before reopen. Do not synthesize a running task or pass an arbitrary base to
the existing validator. Add a coordinator-owned, read-only
`preflight-run` operation that shares the report/ledger validation logic with
post-reopen `checkpoint-run` but derives a prospective base from retained
coordinator authority.

The operation accepts only work ID, task ID, and run ID. It derives every
other identity itself and refuses unless:

- the on-disk state exactly equals the retained checkpoint; CR-3 is
  `interrupted`; the latest history entry is attempt 2; and the checkpoint
  revision, prior attempt ID, interrupted candidate and expected next attempt
  ID are internally consistent;
- `coordinator_sha` from that retained state is the prospective attempt-3
  base. The candidate in the run report is its descendant, is an ancestor of
  the current clean source postimage, and contains the generated acceptance
  document for the accepted contract named in the report;
- the accepted ref/digest are read from the live coordinator pin and match the
  report contract digests. A report from the initial implementation contract
  is admissible only when the final accepted plan explicitly declares the
  unchanged per-case continuity it relies on;
- the report and existing ledger row match byte-for-byte by canonical
  identity/digest, including run ID, phase, task scope, candidate SHA,
  runner/capability identity, executions, case inventory, case/assertion
  identities, source digests, output paths and output hashes;
- the report's runner adapter digest equals the `unittest_runner.py` digest
  pinned at the prospective base (`coordinator_sha`). The CLI's executing
  runner digest is not assumed to be base-pinned merely because worker mode
  was used;
- the report has the required phase shape: a genuine mapped
  `behavior_assertion` for Red, or all selected CR-3 cases passed for Green.

Preflight returns a canonical JSON assessment and its digest on stdout. It
does not write a ledger row, checkpoint, task milestone, state field, receipt,
or source file. The reviewer packet may retain that exact stdout and digest as
review evidence; the command itself remains read-only. Inputs such as a
prospective base, attempt ID, accepted digest, candidate identity, or runner
digest are never accepted from the caller.

Add a mapped CR-3 preflight case (proposed CR-T61) with exact selectors and
source ownership for the coordinator preflight module and tests. Its Red and
Green tests must cover: valid preflight while interrupted; refusal when the
retained checkpoint differs from state; refusal when any derived attempt,
accepted-plan, candidate, runner, report, ledger, source, or output identity
is stale; and proof that all refusals leave state, checkpoint, ledger, and
reports byte-identical. Add CR-T61's implementation, test file, CLI surface,
and documentation paths to CR-3 ownership. Preserve the existing post-reopen
`checkpoint-run` as the final authority; preflight cannot authorize reopen or
record task evidence.

The proposed CR-3 mappings reserve CR-T58 for T21 exception enforcement,
CR-T59 for historical Red continuity, CR-T60 for receipt lifecycle, and CR-T61
for this preflight. The independent review must bind each exact selector and
its production/test source paths in the accepted graph and test plan; these
IDs are proposals until contract validation confirms they are available.

## Gap 2: complete implementation and phase order

The amendment needs two accepted contract revisions so test authorization,
implemented behavior, and activation of the T21 exception are not conflated.
The human's eventual approval of the scoped amendment covers this exact staged
sequence; the reviewer verdict requested now does not approve that scope.

**P0 — implementation/test contract, accepted before code changes.** While
CR-3 is interrupted, prepare and independently review a first revised plan,
test plan and graph. It includes exact CR-3 ownership and mapped tests for:
receipt lifecycle/bootstrap, preflight, T21 exception enforcement,
cross-plan Red continuity, and the T10 observer sensitivity check. T12 is
classified narrowly as `regression`; T13 remains `new`; T21 remains `new` and
has no active TDD exemption in P0. P0's review states that the human-authorized
T21 exception is proposed but not yet recognized by completion semantics.
Accept P0 using the current supported contract acceptance path. This pins the
implementation and test scope only; it does not claim task completion, waive
T21 Red, or activate an exception.

**P0 Red.** Add the mapped assertions as a test-only commit descended from the
coordinator base and after the P0 accepted document is present in the
candidate. Execute the actual traceability CLI with `ASK_INNER_LOOP_ROLE=worker`,
`--scope task --task-id CR-3 --phase red`, against the real coordinator root.
The CLI runs tests in its detached candidate worktree and writes the immutable
report and ledger entry to the real workstream runtime. Require genuine
behavior assertion failures from the new receipt, preflight, exception and
continuity behavior tests that are not implemented yet; the T10 sensitivity
negative control remains a passing test assertion and is never treated as
product Red. Test methods and callable seams must exist before this run; Red
must be a failing behavior assertion, never an import, setup, missing-selector,
or unsupported-subtest error. Preserve the runner digest and exact
run/report/ledger identities.

**P0 implementation and Green.** Implement the receipt lifecycle and
preflight path plus the T21 exception, continuity, and review/completion
enforcement in their mapped CR-3-owned modules. This includes a testable
`accept-plan` binding that will later require the exact human decision
reference for the T21 exception. Run the mapped selectors through Red → Green
for each behavior, using the previously recorded P0 Red where the exact
assertion is unchanged. Corrected T10 gets exact-candidate Green and its
negative-control evidence, without Red. Then run a full selected-case
`final_green` against P0 and capture the real worker-published run as described
in revision 3. This is a full passing execution of P0's selected CR-3 tests;
it is not yet TaskResult approval or aggregate completion, because P0
deliberately has no T21 exemption.

**P1 — final semantic contract.** While still interrupted and after P0
implementation tests pass, prepare the final contract revision. It keeps all
P0 selectors, criteria, and ownership; adds only the explicit CR-T21-specific
`historical-red-unavailable` declaration and plan-declared immutable Red
continuity identities/assessments. The proposed CR-T21 contract field is a
`tdd_exception` object containing exactly the exception kind, human decision
artifact path, and human decision artifact SHA-256; P0 has no such object.
Each P1 continuity row names the case ID, source accepted ref and plan digest,
original run ID, report digest, canonical ledger-row digest, original case
contract digest, assertion-source path/digest, and candidate SHA. No unlisted
run or assertion is eligible. Independent plan review checks that these
declarations exactly match the human decision artifact, provenance audit,
P0 reports, unchanged case/assertion/source identities, and implemented
verifier behavior. The updated `accept-plan` implementation validates and
binds that exact field to the human decision artifact identity and digest; the
coordinator accepts P1 while CR-3 remains interrupted. P1 is the first
accepted contract under which the exception can be recognized. T21 stays
`new`; no Red is claimed;
exact-candidate Green and independent semantic review remain mandatory at task
and workstream completion.

**P1 exact Green and preflight.** With the accepted P1 document included in a
clean committed candidate, run the full selected CR-3 `final_green` using the
actual traceability CLI in worker mode. The amended report-selection logic
must recognize only P0 historical Red explicitly carried by P1 after
validating its original acceptance chain, report/ledger identity, ancestry,
and per-case continuity. It must not carry the corrected T10 observer
assertion as historical Red. Require P1's exact-candidate Green for all
selected CR-3 cases. Run the new coordinator `preflight-run` for each
P0-origin Red and P1-origin Green while state is still interrupted; retain the
stdout assessments and hashes in the independent review packet. Any failed or
ambiguous preflight blocks receipt creation and reopen.

This staging assigns each verifier behavior to an executable contract:

| Step | Accepted contract and verifier authority | Evidence allowed |
| --- | --- | --- |
| P0 acceptance | Existing coordinator accepts the reviewed implementation/test scope; T21 exception is not active | Plan/spec/graph digests and P0 acceptance seal |
| P0 Red | P0's pinned traceability runner publishes real-root reports/ledger; no task-state checkpoint while interrupted | Mapped behavior Red only; no T10 negative-control Red |
| P0 Green | Implemented candidate runs P0 cases; no claim that P0 aggregate completion passes | Exact candidate Green and mapped semantic test outcomes |
| P1 acceptance | Updated coordinator validates human authorization and exact case-scoped exception/continuity declarations | P1 acceptance seal bound to human decision and independent plan review |
| P1 completion check | Updated service/completion verifier applies continuity and T21 exception rules | P1 exact Green, valid carried Red for unchanged assertions, independent semantic review |
| Post-reopen checkpoint | Real coordinator validates each previously published run against active attempt-3 base/lineage and records its original summary | Existing run IDs/reports/ledger rows and exact checkpoint evidence |

## Reopen receipt and coordinator checkpoint sequence

After P1 Green and successful read-only preflight, prepare a distinct
attempt-2 → attempt-3 reconciliation request. Bind the live checkpoint SHA and
revision, attempt-2 ID and interrupted candidate, expected attempt-3 ID, P1
accepted ref/digest, coordinator base, exact clean source candidate, and
canonical hashes for every overlapping post-interruption source change
(including `afc7ab2`'s test edit). Include the preflight assessment digests,
P0 Red and P1 Green run IDs, and their original report/ledger digests without
rewriting or embedding those artifacts. Require an independent reviewer to
bind the exact candidate and canonical payload digest; `recorded_by` must be
different from that reviewer. Keep the consumed attempt-1 → attempt-2 receipt
and both prior attempt records unchanged.

Only the real coordinator may reopen. It must recognize the consumed receipt
as immutable history, validate the new receipt against the exact next
transition, and refuse stale or edited requests before state/checkpoint
mutation. After a successful reopen, call the existing `checkpoint-run` for
each P0 Red and P1 Green run ID. This post-reopen path performs full validation
against the now-active task base and lineage and stores the original summaries
with original phases, candidate SHAs and report digests. Both preflight and
post-reopen validation are mandatory; neither substitutes for the other.

Finally obtain fresh exact-candidate semantic review, TaskResult review and
applicable checks under P1. CR-4 remains gated until CR-3 integrates. No
integration or completion claim is part of this proposal.

## Preserved proposal terms

The T10 observer correction and negative-control distinction remain as in
revision 3. The T12 evidence remains narrow; T12's failed `final_green` run
stays `final_green`. T13 stays `new`. T21's corrected lineage remains in
`CR-3-t21-provenance-correction.md`; its historical Red remains unavailable.
All original execution reports, ledger rows, attempt records, accepted
authority, and consumed receipt remain byte-for-byte unchanged.

## Reviewer response requested

Please review the P0/P1 sequence, prospective-base derivation and read-only
preflight authority, phase-to-verifier table, P0-to-P1 continuity, and the
post-reopen coordinator validation. Return **APPROVED** or **REQUEST CHANGES**
with any remaining executable or authority gaps. This is not the human's
scoped amendment approval. Until that approval is separately submitted, make
no plan, code, verifier, task-state, receipt, report, or ledger changes.
