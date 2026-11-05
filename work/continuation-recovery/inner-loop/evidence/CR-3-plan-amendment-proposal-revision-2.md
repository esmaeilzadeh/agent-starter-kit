# CR-3 amendment decision proposal — revision 2

**Status:** proposal only; the task remains interrupted. This document does
not amend the accepted plan, authorize implementation, or approve a TaskResult.
It replaces the incomplete proposal in `CR-3-plan-amendment-proposal.md` for
the next decision. The original proposal and execution evidence remain
unchanged.

## Decision requested

Approve a narrowly scoped CR-3 plan amendment and the preparation of its
reviewed enforcement and bootstrap path. This changes how TDD evidence is
recognized for one mapped case and adds verifier behavior, mapped tests, and
CR-3 ownership. It does not change product What/Why or the approved intent.
The approved `intent.md` must remain byte-identical. Declining leaves CR-3
interrupted under accepted plan digest
`a8c13188a26489e67173333ca4f69ac572f00836a3f32e77929ee82a1ff99025`.

## Proposed contract and graph amendments

1. **CR-T12:** change only its `change_kind` from `new` to `regression`. The
   registered run `b50dd24e0ef04a2aacff4c4a26db4dd5` shows the assertion passing
   at test-only candidate `3196a59` while production under
   `_ask/scripts/inner_loop` matched task base `2c508ff`. Keep failed run
   `6a96d09a0d4c4394951b47fa33a14dd7` recorded as `final_green`.
2. **CR-T13:** keep `new`, its current selector, criteria, type, and assertions;
   extend the scenario/assertions to cover a second interrupt and reopen with
   distinct attempt IDs, immutable history for consumed receipts, refusal of a
   stale newly submitted request, and an authentic Red for the added behavior.
3. **CR-T21:** keep `new` and retain every mapped assertion. Its lineage and
   lack of valid Red are stated in
   `CR-3-t21-provenance-correction.md`. The exact contract statement is:

   > CR-T21 remains new; historical Red is unavailable; only CR-T21 receives
   > the approved exception; no Red-to-Green claim is made; exact-candidate
   > Green and independent semantic review remain mandatory at task and
   > workstream completion.

4. Add `_ask/scripts/inner_loop/attempts.py` to CR-3 ownership while retaining
   CR-2 as predecessor and preserving serialized task execution. Add ownership
   for the traceability contract, plan-validation, review, report-selection,
   and completion modules that implement T21 exception and historical
   continuity enforcement, plus their dedicated test module. Exact paths and
   selectors must be listed in the revised graph and test plan before review;
   no implicit ownership expansion is authorized.

## Required T21 exception enforcement

Introduce one explicit, named exemption kind (proposed identifier:
`historical-red-unavailable`) with semantics limited to CR-T21. It is valid
only when all of these checks pass:

- The case is CR-T21, `change_kind` remains `new`, and the current accepted
  plan explicitly declares this exemption for that case. No task or aggregate
  reviewer may infer it from prose or a generic case flag.
- The plan-review record includes the human decision artifact identity and
  digest, the provenance limitation, and the exact contract/spec/plan/graph
  digests. `accept-plan` rejects the exemption if that authorization binding
  is missing or mismatched.
- Both task and workstream completion/review paths recognize the same
  case-scoped exemption. They still require registered Green at the exact
  candidate and independent semantic review. Reports state that Red is
  unavailable and do not state or derive a Red-to-Green transition.
- Any other case using this exemption, any T21 Green or review mismatch, or an
  unaccepted/stale plan fails closed. Existing exemption kinds and all other
  TDD obligations retain their current semantics.

Add mapped tests for contract validation, acceptance binding, task review,
aggregate review, completion reporting, and negative controls proving another
case cannot use the exception. These tests must use exact selectors and source
paths in the revised `test-plan.json`; the verifier changes are not authorized
until those mappings and CR-3 ownership are reviewed and accepted.

## Cross-plan Red continuity

The amendment must make retained Red usable only through a plan-declared,
verifiable continuity record. For each carried case, the new contract names
the original accepted contract SHA/ref and spec/plan digests, immutable run ID,
candidate SHA, raw report hash, ledger identity/hash, and mapped case identity.
The verifier then checks the original accepted-plan chain and report/ledger
integrity; verifies the original run was a genuine failed `red` with a
`behavior_assertion` for that case; verifies the candidate is in the current
task lineage; and compares the old and current case contract fields
(case/task/criteria/type/runner/selector/scenario/assertions/source paths).
Semantic review must bind a per-case continuity assessment, including relevant
assertion-source identity and source digests. A changed assertion is not
covered merely because its case ID is unchanged; it needs its own Red or a
separately authorized classification.

For this amendment, review the established candidates and run identities for
CR-T10 (`b50dd24e0ef04a2aacff4c4a26db4dd5`, candidate `3196a591…`) and CR-T19
(`f21a95f6b4c4499aacf37a3ffd27a77d`, candidate `94458d8376a75f052adbf2c4737f4f3c18cef4b6`)
against both accepted plan revisions. Carry only assertions whose mapped
contract and source continuity is demonstrated. T10's later report-publication
assertion from `afc7ab2` is new and receives its own fresh Red. Preserve every
old report and ledger digest byte-for-byte; do not copy old evidence into a
new-digest run or manufacture a failure.

Map this verifier behavior to dedicated exact-selector tests (proposed unused
case IDs CR-T58 and CR-T59, subject to graph/contract validation): one tests
accepted historical Red continuity and altered-contract/source rejection; the
other tests integrity, ancestry, and report/ledger tampering rejection. Both
belong to CR-3 and have exact source ownership.

## Receipt bootstrap before reopen

The current fixed `reconciliation-CR-3.json` blocks another reopen. The
amendment must authorize a narrowly scoped correction in `attempts.py` and a
pre-reopen test path; acceptance of the revised plan alone is insufficient.
The proposed behavior is:

- Keep the existing receipt bytes and digest immutable and record its identity
  under the attempt transition that consumed it. A new transition uses a
  separate receipt bound to `(previous_attempt_id, new_attempt_id)`.
- On reopen, validate the request against the latest interrupted attempt and
  the proposed next ID. A previously consumed receipt is accepted only as
  history when its bytes match the recorded identity; it cannot satisfy or
  replace the new request. A stale or edited new request fails before state or
  checkpoint mutation.
- The pre-reopen test runs in a disposable repository fixture through the real
  coordinator/attempt code and trusted traceability runner. The revised plan
  must map this bootstrap behavior to an exact CR-3 case and document the
  isolated runtime/ledger paths so it produces genuine registered Red and
  Green without mutating the interrupted coordinator ledger. First capture
  Red on the test-only candidate; then implement the minimal production
  correction, run exact Green, and obtain independent review. If the harness
  cannot produce accepted registered evidence without touching the interrupted
  ledger, stop and return with the exact blocker; do not hand-edit ledger,
  state, receipt, or report files.
- Before the actual attempt-2-to-attempt-3 reopen, create a new reviewed
  source-reconciliation receipt for that exact transition. It binds checkpoint
  SHA/revision, accepted plan ref/digest, interrupted candidate, coordinator
  base, clean descendant candidate, and hashes for every overlapping source
  postimage, including `afc7ab2`'s `_ask/tests/inner_loop_recovery.py` change.
  `recorded_by` and independent reviewer must be distinct. The review binds
  candidate SHA and canonical payload hash and is refreshed after any
  intervening source commit. Preserve attempt-1 and attempt-2 histories and
  prior receipt identities unchanged.

The revised independent plan review must inspect this sequence against
`attempts.py`, current state, fixed receipt, checkpoint and source history. It
must identify the exact fixture setup, test/run IDs, artifact digests, and
authority boundary before any bootstrap edit or reopen.

## R3 correction and execution boundary

Commit `afc7ab2` reloads the ledger after the child exits at
`after_report_publication`; this is source-reviewed only. The amended CR-T10
case must demonstrate that the test detects an incorrect publication boundary
(negative control), then run real Red for the newly added assertion, exact
Green, and independent semantic review. The existing old Red may cover only
the unchanged original assertion.

After the human submits approval, the amended `plan.md`, `test-plan.json`, and
`inner-loop/tasks.yaml` must agree. Commit them, obtain independent `APPROVED`
plan-review JSON binding exact committed contract SHA, canonical spec/plan/
graph digests, reviewer identity, previous accepted digest, human-decision
reference, corrected provenance, continuity rules, and bootstrap test/design
identities. Validate and accept via the normal traceability operation. Read
back and verify the accepted ref and seal; both ref and digest must differ from
attempt 2. Only then perform the independently reviewed bootstrap, reopen, and
run CR-T13 plus corrected CR-T10 through Red → Green → Refactor. Obtain fresh
exact-candidate task/workstream review and applicable checks. Integration and
CR-4 remain gated.

## Proposed selectable decision

- **Approve scoped amendment (Recommended):** authorize only the CR-T12,
  CR-T13, CR-T21 exception-enforcement, cross-plan continuity, ownership, and
  receipt-bootstrap preparation described above. No task reopens until the
  amended plan is independently reviewed and accepted and bootstrap evidence
  is reviewed.
- **Keep current TDD rule:** make no contract, verifier, bootstrap, or task-state
  change; CR-3 stays interrupted. Add free text with any direction.
- **Request changes:** return this proposal for revision. Add free text naming
  the requested change.

