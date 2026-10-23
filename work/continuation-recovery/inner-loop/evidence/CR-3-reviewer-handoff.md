# CR-3 reviewer decision and coordinator handoff

Date: 2026-10-23. Verdict: **REQUEST CHANGES**.
Reviewed packet: `6e84d22`; source correction: `afc7ab2`; last interrupted
candidate: `08339eb5bf9802cf815819bf3168f13c5296d9bd`.
Scope: answer `CR-3-reviewer-next-step-question.md`, not approve a TaskResult.
Independent read-only reviews: `/root/policy_review` (Standards) and
`/root/evidence_review` (Spec/provenance); coordinator reviewer: `/root`.

CR-3 remains interrupted at revision 27, coordinator `2c508ff`, under plan
`a8c13188a26489e67173333ca4f69ac572f00836a3f32e77929ee82a1ff99025`.
This note does not authorize reopening, implementation, or integration.

## Standards review

1. **P1 — T21 exception lacks an executable completion path.** A one-case
   exception is reasonable to propose to the human given the honest provenance
   limitation, but the reviewer cannot waive the current Red requirement.
   `.agents/ask/task-loop.md` requires actual behavioral Red, and
   `_ask/policies/delegation.md` requires escalation for changed acceptance
   criteria. The proposal correctly acknowledges that human decision; it does
   not yet define a supported representation through task and aggregate
   completion. `contracts.py:12` enumerates supported exemption kinds;
   `evidence.py:227-244` validates them. The existing `baseline-regression`
   exemption is task-only and requires every mapped source file to be identical
   to the accepted contract revision. T13's future edits touch T21's mapped
   test file, and workstream review cannot use that exemption anyway.
   `accept-plan` pins contracts; it does not implement new exemption semantics.
   Do not disguise T21 as documentation/configuration or reclassify it as a
   regression. Any required verifier/policy change needs its own explicit
   scope, ownership, tests, and approval before use.

2. **P1 — retained Red is not automatically usable under the next digest.**
   `service.py:91-118` selects registered executions by exact spec/plan digests;
   `completion.py:140-145` still requires Red for non-exempt new cases. The
   proposal must explain how valid historical evidence for unchanged cases
   such as T10's original assertion and T19 will be recognized after amendment.
   Preserving an old report is necessary but does not make the current checker
   accept it under a different plan. Demonstrate a supported continuity path,
   or explicitly scope a reviewed change that validates immutable original
   run identities, lineage, and per-case contract/assertion continuity. Never
   rewrite old report digests or rerun passing implementation to manufacture Red.

## Spec and provenance review

1. **T12 classification is supported, narrowly.** Registered run
   `b50dd24e0ef04a2aacff4c4a26db4dd5` reports T12 passed at test-only candidate
   `3196a59`; comparison with task base `2c508ff` shows no production changes
   under `_ask/scripts/inner_loop`. This supports `regression` for that mapped
   assertion, with selector, assertions, criteria and type preserved. Keep
   failed run `6a96d09a0d4c4394951b47fa33a14dd7` as `final_green`.

2. **P2 — correct T21 assertion lineage; no valid retained Red is established.**
   The audit/proposal misattribute assertion introduction to `ae31e20`.
   `3196a59` introduced the mapped method with a pinned-runner byte assertion;
   `5969c3e` added actual old-runner execution, completion receipt, finalization
   and malformed-schema assertions, after production commits `fc43143` and
   `c2262d1`. `37847b0` seeded verifier configuration; `ae31e20` added fixture
   semantic-review prerequisites. Prepare an attributed correction to the
   provenance account without rewriting historical execution reports.
   Registered Red-phase run
   `517f864631a845e082f9a73fa888ef30` passed all eight cases. Neither it nor
   diagnostic overlays establish Red. No valid historical Red path was found
   in this packet. Under the current requirement CR-3 remains stopped; this
   does not mean an explicitly authorized, enforceable exception is impossible.

3. **Ownership and T13 direction are supported; bootstrap is incomplete.**
   Add `attempts.py` to CR-3 ownership while retaining the serialized CR-2 →
   CR-3 dependency. Keep T13 `new`, retain its existing assertions, and require
   real Red for repeated interrupt/reopen, immutable consumed receipts, and
   stale newly submitted request refusal. But `attempts.py:48-87,268-274`
   validates the old fixed receipt before reopening. Merely accepting the plan
   cannot unblock it. Specify and independently review the exact bootstrap
   operation before claiming the sequence is executable. It must preserve the
   original receipt bytes/digest and both interrupted attempts, distinguish
   consumed history from a new request, and reconcile all post-interruption
   overlapping source. If a pre-reopen repair is necessary, explicitly scope
   its authority and authentic Red evidence path; do not silently implement
   it while the task is interrupted or overwrite/delete accepted evidence.

4. **R3 correction is source-reviewed only.** `afc7ab2` reloads the ledger after
   the child exits, addressing the stale-snapshot error. It has no registered
   execution in a reopened attempt and this note supplies no TaskResult approval.
   Retain the requirement to demonstrate detection of an incorrect publication
   boundary, then obtain exact-candidate Green and independent review.

## Required amendment and order of operations

1. Prepare a revised proposal correcting the T21 lineage and addressing its executable exception,
   cross-plan evidence continuity, and receipt bootstrap above. State explicitly:
   “CR-T21 remains new; historical Red is unavailable; only CR-T21 receives
   the approved exception; no Red-to-Green claim is made; exact-candidate Green
   and independent semantic review remain mandatory at task and workstream
   completion.” Define the actual enforcement path, not only this sentence.
   Keep other mapped obligations intact. Present the concrete acceptance change
   for the human's submitted decision under delegation policy. This review
   request is not that approval. Preserve approved intent bytes if What/Why and
   assumptions remain unchanged.
2. After the relevant authorization, prepare consistent `plan.md`,
   `test-plan.json`, and `inner-loop/tasks.yaml`. Include the narrow T12 change,
   T13 scenario/assertion extension and ownership addition. Obtain independent
   `APPROVED` plan-review JSON naming the exact committed contract SHA and
   canonical spec, plan, and graph digests, reviewer identity, previous accepted
   digest, human decision reference, provenance limitation, continuity handling,
   and bootstrap design/evidence identities. The machine checks spec/plan
   digests; explicitly review/bind the graph as well. This handoff is not that
   plan approval.
3. Validate the committed contracts, then have the coordinator (distinct from
   the reviewer, with no running task) execute:

   ```sh
   ./ask traceability validate-plan continuation-recovery --revision <contract-sha>
   ./ask traceability accept-plan continuation-recovery \
     --revision <contract-sha> --reviewer <independent-reviewer> \
     --recorded-by <coordinator> --evidence <approved-review-json>
   ```

   Read back `refs/ask/accepted-tests/continuation-recovery:accepted.json`;
   verify contract SHA, spec/plan/graph digests, review digest and identities
   against the reviewed artifacts. Commit the generated acceptance document
   and seal. Both accepted ref and plan digest must differ from attempt 2's.
4. Complete only the specifically authorized/reviewed bootstrap. Before reopen,
   provide exact source-reconciliation evidence: current checkpoint SHA and
   revision, attempt 2 → attempt 3 identities, interrupted candidate, new
   accepted ref/digest, original coordinator base, clean descendant candidate,
   and exact overlapping source postimage hashes including `afc7ab2`'s test
   change. Its independent review must bind candidate SHA and canonical payload
   hash with reviewer distinct from `recorded_by` (`attempts.py:65-154`). Refresh
   this review if intervening commits change the candidate. Preserve original
   attempt-1 and attempt-2 reports and receipt identities unchanged.
5. Only then reopen through the coordinator; execute the approved T13
   Red → Green → Refactor path and corrected T10 checks. Require fresh
   exact-candidate semantic review, TaskResult review and applicable checks.
   Integration remains gated; CR-4 remains pending until CR-3 integrates.

## Checks and boundary

Read-only `traceability validate-plan` passed for the current contract;
`git diff --check` passed. Historical reports, source lineage, acceptance and
reopen validators were inspected. No new behavioral run, aggregate verification,
result publication, acceptance operation or task transition was performed.
Those operations are outside this review-only request; this is not completion
of the workstream. The documentation-only note preserves the current authority,
state, execution ledger and original reports. The initial commit attempt was
blocked by read-only Git metadata; the human subsequently granted permission
to commit this note. That permission does not authorize the proposed amendment
or any task transition.

Review totals: Standards — two blocking findings (exception enforcement and
cross-plan continuity); Spec — two findings (blocking reopen bootstrap and inaccurate T21 lineage),
with T12 supported and T21's missing Red confirmed.
