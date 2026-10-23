# CR-3 recovery decision: stop restarting the evidence review

Date: 2026-10-23. Source checkout: `f0288ac`.
Human direction: investigate and break the CR-3 review/implementation loop by
checking the main specification and task. This document consolidates the
coordinator's diagnosis and supersedes the procedural next-step instructions
in `inner-loop/evidence/CR-3-review-revision-{3,4,5}.md`. Those reports remain
historical evidence. It does not change the accepted contract or grant a TDD
exception. The runtime repair is not complete.

## Decision

Stop requesting further narrative amendment revisions. Proceed to one concrete
contract/implementation work package using the bounded corrections below.
The historical-evidence design in revisions 4–5 is supportable with these
corrections. Exact contract review and the unsubmitted human exception decision
remain distinct gates; this document is not a machine `accept-plan` receipt.

The review process partially recreated the bug being repaired. It repeatedly
reassessed implemented behavior as if its evidence had to start again, then
added machinery to satisfy that reassessment. Some implementation defects were
real, but a new prose proposal at every finding did not advance the first
unmet milestone. The coordinator reviewer accepts responsibility for this.

## Authoritative requirements and corrections

| Source | Required behavior | Effect on CR-3 |
| --- | --- | --- |
| CR-04 | Preserve separate milestones; resume the first unmet valid one | Keep actual old Red and implementation history; renew stale review/Green where needed. |
| CR-05 | Changed contracts require explicit reconciliation; do not infer milestones | An amendment does not erase history or automatically make it applicable. Validate applicability explicitly. |
| CR-06 | Attribute missing milestones honestly and renew only stale evidence | T21's missing Red remains an explicit exception decision, not a reason to restart every case. |
| CR-07 | Deliberate reopening preserves the earlier attempt and identifies the new one | Fix consumed-receipt handling without deleting or replacing either interrupted attempt. |
| TT-006 in `specs/current/spec-test-traceability.json` | “Review assesses assertion continuity when test code changed; existing policy controls explicit exemptions.” | Statement/AST equality is not the definition of continuity. Independent review assesses the same behavior across changed tests. |
| TT-008 | Normal completion entrypoints share validation | Test the actual coordinator integration path, including its pinned verifier. |

**Withdrawn gate: identical assertion fingerprints.** Revision 5 introduced
this as a proposed mechanism; the canonical specification does not require
it. The absence of T10's old callable-check statement is a true source fact,
but does not by itself invalidate its historical milestone. Use immutable
old/current source identities plus an exact, independently reviewed behavioral
continuity assessment. A fingerprint can help locate statements; it cannot
replace that assessment or become an additional acceptance criterion.

T10's original failure proved the checkpoint entrypoint was unavailable.
Current process-exit tests exercise the resulting finalization behavior more
directly. Review that evolution under TT-006. Preserve the limited meaning of
the original failure; do not claim it executed later publication assertions.
The `afc7ab2` observer correction needs current Green and a sensitivity check.
A fresh manufactured product failure is not required solely because that
observer was corrected or a stronger test replaced an API-presence check.

**Withdrawn gate: authority-to-authority Git ancestry.** Acceptance commits
parent their own contract commit; previous authority is used for CAS only.
Validate exact old authority/contract/candidate bindings and explicit current
permission to use that evidence. Keep actual source ancestry checks and object
retention. Do not add merges or change history to satisfy an invented chain.

These withdrawals correct requirements introduced during review. They do not
waive required behavioral Red, review, current Green, or coordinator integration.

## Reproduced blockers and complete case disposition

A read-only call to `_reviewed_reconciliation` on state revision 27 returned:
`attempt reconciliation identity is stale or conflicts with coordinator state`.
The existing receipt describes the consumed attempt-1 → attempt-2 transition.

A read-only execution-ledger inspection found these registered failure records:

- `b50dd24e0ef04a2aacff4c4a26db4dd5`: T10 and T20 failed.
- `f21a95f6b4c4499aacf37a3ffd27a77d`: T19 failed.
- `dab908b39596441086d57106b8c816ec`: T19 failed in attempt 2.

The current whole-plan digest filter selects only the last of those reports.
It excludes retained evidence for unaffected cases after the T11/T14 amendment.
That is an applicability/reconciliation problem, not proof that no Red occurred.

| Case | Next required treatment |
| --- | --- |
| T10 | Retain original Red with its exact scope; independently assess test evolution; current Green and observer sensitivity evidence. |
| T11, T14 | Keep already accepted regression classifications. |
| T12 | Prepare the already-supported narrow regression reclassification; preserve its failed `final_green` phase. |
| T13 | Retain prior passing history; capture real Red for the newly discovered repeated-reopen/receipt defect before fixing that behavior. |
| T19 | Retain applicable original/attempt-2 Red and review source continuity; use current Green. |
| T20 | Retain its original Red with applicable mapped behavior and current Green. |
| T21 | No valid retained Red for the expanded behavior. Keep `new`, all behavioral checks, and disclose the gap. The narrow exception still requires a submitted human decision. |

This inventory resolves the treatment of all eight CR-3 cases; subsequent
review must not restart their classification without contrary evidence.

## Immediate next action

Prepare the exact scoped decision and contract drafts using the runbook below.
Resolve the known old-base verifier incompatibility in that same package before
requesting approval or representing the live recovery sequence as executable.
The next human decision covers T21's explicit evidence limitation and the
bounded enforcement/bootstrap work. The next technical feedback comes from
one disposable scenario reaching real coordinator integration.

A reviewer may block on a concrete contradiction with an accepted requirement,
missing real evidence, or a reproduced failing check. Optional fingerprints,
renaming or stronger paperwork do not restart the task. Resolve implementation
findings in the same candidate cycle.

## Execution runbook for the coder

### A. Establish authority before changing anything

Read this document first. Use proposal revision 4 for P0/P1 staging and revision
5 for the original-run inventory only where they agree with this document.
This document supersedes their identical-AST and authority-ancestry rules.
Canonical CR-01–CR-08 and TT-001–TT-011 take precedence over all proposal prose.

At the start of the coder turn, run `./ask check-clean`, inspect branch/HEAD,
state and retained authority, and record the following observed baseline:

| Item | Last observed identity; reread before use |
| --- | --- |
| Branch | `agent/continuation-recovery` |
| State revision | `27` |
| Coordinator/task base | `2c508ff4248f16a3e3121d33a0fae7297c9b378e` |
| CR-3 | interrupted; two retained interrupted attempts |
| Last interrupted candidate | `08339eb5bf9802cf815819bf3168f13c5296d9bd` |
| Current accepted plan digest | `a8c13188a26489e67173333ca4f69ac572f00836a3f32e77929ee82a1ff99025` |
| Later source correction | `afc7ab2`, post-crash ledger reload; requires reconciliation |
| CR-1 / CR-2 / CR-4 | integrated / integrated / pending |

Use the live checkpoint/ref values when preparing receipts. Never copy an
old revision, HEAD or checkpoint SHA from this note into a new receipt without
checking it. If the baseline changed, reconcile the actual delta before work;
retain completed work and existing approvals that remain applicable.

**Before the scoped human decision**, permitted work is read-only diagnosis,
contract drafts in separate proposal files, exact diff/ownership preparation,
and documentation. Keep active `plan.md`, `test-plan.json`, `tasks.yaml`,
accepted refs, source, receipts, state and runtime ledger unchanged. A draft
can be complete without becoming the active contract. Do not interpret the
request to improve this note as approval of T21's exception.

The single human decision package must contain the complete concrete proposal:
T12 reclassification; T13 receipt regression; historical evidence applicability;
T21's one-case exception at both task and workstream completion; preflight and
bootstrap work while interrupted; exact additional ownership; and any required
trusted-verifier compatibility/migration. T10 semantic continuity is assessed
under TT-006, not presented as a new exemption. State the evidence limitation
and behavior that remain mandatory. Record the submitted choice and bind its
artifact/digest in the accepted contracts. An unsubmitted or preselected option
is not authorization. Request changes/decline blocks only dependent work.

### B. Define one shared evidence decision

Implement an eligibility decision that separates these inputs:

- **Original truth:** immutable run/report, original candidate/source/runner,
  original contract, original authority and original ledger row.
- **Current permission:** exact current accepted contract and an independently
  reviewed per-case continuity or exception decision.
- **Current success:** full required Green at the reviewed current candidate,
  current semantic/candidate review and required verification/integration.

For historical Red, validate the original bytes/digests against the original
contract. Validate its applicability separately against the current decision.
Read original authority by exact object identity and verify its bindings;
source/contract ancestry still matters, authority-commit ancestry does not.
A mere path to a JSON file, present Git object or matching case ID is insufficient.

The current decision binds work/task/case IDs, original run/authority/candidate,
original and current contract identities, old/current assertion source digests,
reviewer identity, behavioral continuity assessment and explicit accepted scope.
The assessment explains what the original failure demonstrated, how current
assertions test that behavior, and which additions are not historical evidence.
Actual changes to behavioral obligations receive their own required evidence;
source refactoring or a stronger observer does not automatically reset history.

Return accepted evidence per case, with the original run identity retained.
A failing report can contain passing cases: only the actual eligible failing
cases receive Red. T10 and T20 may reference the same run, but finalize that run
once and retain each case's separate applicability. Reject undeclared runs,
wrong task/scope, unsupported records, missing/altered outputs and stale review.
Current Green must use the current contract and exact reviewed candidate.

Use this decision consistently in report selection, semantic/completion checks,
preflight and checkpoint finalization. Extend source ownership for each touched
module before implementation. Candidate modules likely include
`inner_loop/attempts.py`, `inner_loop/evidence.py`, the coordinator CLI, and
traceability `service.py`, `completion.py`, `evidence.py`, `contracts.py` and
`coverage.py` under their existing `_ask/scripts` / `.agents/ask/verification`
roots. This is an inventory to resolve into exact approved paths, not automatic
permission to edit all of them. Identify new helper/test paths explicitly.

The exception mechanism must activate only for the exact approved
`continuation-recovery` / `CR-3` / `CR-T21` declaration. Reject attempts to use
that approval for another workstream, task or case. P0 cannot activate it.
P1 requires its exact human authorization and independent review, then still
requires current Green. Report `historical Red unavailable / approved exception`,
never a fabricated Red-to-Green transition. Keep the other exemption kinds'
existing semantics. Use a data-driven authorized declaration rather than
silently hardcoding a global T21 bypass.

### C. Resolve the trusted-verifier compatibility boundary early

The verifier from `2c508ff` contains only these exemption kinds:
`documentation-only`, `generated-projections`, `non-behavioral-config`,
`baseline-regression`. Its report selection requires equal spec/plan digests.
These are inspected facts, not a claim that an end-to-end execution was run.
The existing baseline exemption does not solve the proposed aggregate exception.

Determine and document how the normal integration verifier will enforce the
approved new semantics. The concrete package must identify the verifier source
revision, how that revision is authorized, which component selects it, and
how its output binds the unchanged task base/candidate/contract. Current-source
unit tests or `check-completion` success are insufficient for this boundary.

If existing trusted interfaces can express the repair, demonstrate that path.
If they cannot, present the minimal explicit compatibility/migration change as
part of the same scoped decision before using it. An authorized migration must
preserve historical bases and runner identities and retain the normal static,
semantic, candidate and integration checks. Arbitrarily selecting candidate
verifier code, changing `base_sha`, altering old reports or ignoring a failed
pinned-verifier receipt is forbidden. Do not accept P1 or begin the live reopen
sequence while this integration path remains an unexplained assumption.

### D. Execute the phases in this order after authorization

| Phase | Preconditions | Work/output | Exit condition |
| --- | --- | --- | --- |
| P0 prepare/accept | Submitted scoped human decision; exact draft artifacts ready | Commit consistent active plan/graph/test mapping; independent review of exact canonical digests; coordinator `accept-plan`; commit generated pin/seal | Read-back authority equals reviewed P0; no active T21 exception; CR-3 still interrupted |
| New-slice Red | Accepted P0 and committed test-only candidate containing its pin | Real assertions for new receipt, continuity, preflight and exception behavior; callable seams exist; official task-scoped worker execution | Complete registered reports identify real behavior failures; setup/import/collection errors do not satisfy Red |
| P0 implementation | Applicable genuine new-slice Red; approved ownership | Implement the mapped slices, shared validation and authorized verifier compatibility; retain original behavior evidence | Full selected-case P0 Green plus Refactor outcome; passing execution is not yet CR-3 completion |
| P1 prepare/accept | P0 implementation demonstrated; concrete historical rows and T21 authorization ready | Independently review exact final contract; validate/bind human decision; coordinator accepts P1 and commits pin/seal | P1 read-back matches reviewed contract; exception is now eligible under its declared terms |
| P1 current Green | Clean exact P1 candidate; reviewed verifier path available | Full selected-case current Green and read-only historical/current preflight | Required Green and all applicability checks pass; no state transition yet |
| Receipt/reopen | Demonstrated full disposable lifecycle; exact source postimage and preflight evidence | Distinct reviewed attempt-2 → attempt-3 receipt; real coordinator `reopen` | State/checkpoint agree on new attempt; old attempts/receipt unchanged |
| Finalize/review/integrate | Running attempt 3; original reports/ledger intact | Coordinator checkpointing; fresh exact-candidate semantic and TaskResult review; normal verification/integration | Actual passing receipts and integrated checkpoint; only then CR-4 becomes eligible |

P0 tests may create a P1-like contract in disposable fixture repositories to
exercise the future behavior. That does not activate P1 or T21 in the real
workstream. Each fixture owns its own state, refs, ledger and authority.

The accepted test plan must map every new selector to an existing CR criterion,
task and exact source paths. CR-T58–61 are proposed IDs, not already accepted
cases. Resolve overlap between extended T13 and any added receipt case before
acceptance: each selector has one case/task mapping; distinct additional cases
must test distinct required outcomes. Test filtering cannot silently omit
mapped cases to obtain a passing full-scope run.

### E. Command and environment discipline

The following are command shapes, not instructions to run before their gates.
Replace angle-bracket placeholders with recorded exact values; never execute
placeholders literally. The anchor must be a source commit that contains the
generated accepted document, not the accepted-authority commit's special tree.

```sh
./ask traceability validate-plan continuation-recovery --revision <contract-sha>
./ask traceability accept-plan continuation-recovery \
  --revision <contract-sha> --reviewer <independent-reviewer> \
  --recorded-by <coordinator> --evidence <exact-review-json>

ASK_INNER_LOOP_ROLE=worker ./ask traceability run continuation-recovery \
  --candidate-sha <immutable-candidate-sha> --anchor-sha <source-pin-anchor> \
  --scope task --task-id CR-3 --phase red

ASK_INNER_LOOP_ROLE=worker ./ask traceability run continuation-recovery \
  --candidate-sha <immutable-candidate-sha> --anchor-sha <source-pin-anchor> \
  --scope task --task-id CR-3 --phase final_green

./ask inner-loop reopen continuation-recovery CR-3 --reason <recorded-reason>
./ask inner-loop checkpoint-run continuation-recovery CR-3 --run-id <run-id>
```

Worker mode is per-command, never a persistent session role. Confirm the real
repository/runtime root and inherited environment before each invocation.
Worker mode defers coordinator finalization; it still writes real reports and
append-only ledger entries, so it is authorized bootstrap work, not read-only
review. Nested fixtures must not accidentally write into the parent workstream
via inherited runtime-root variables. Verify the executing runner digest against
the intended pinned runner; the role flag itself proves no runner identity.

`preflight-run` is proposed functionality and does not exist in the reviewed
baseline. Its accepted interface must derive identity from retained state,
accept only work/task/run selection, remain read-only, and use the same evidence
validation as finalization. A preflight result is never a task milestone.

Use `reopen`, not `resume`, for this interrupted task. The existing `resume`
command is described as aborting back to `coordinator_sha`; it is not a substitute
for reconciliation. Do not reset, rebase, reinitialize or silently roll back the
candidate to make the repair queue appear fresh.

### F. Reconciliation receipt and freshness rules

Retain the original fixed receipt bytes/digest as consumed history. Implement
selection of a distinct new transition request. The new request must bind:
work/task, live checkpoint SHA/revision, prior attempt ID/interrupted candidate,
next attempt ID, accepted P1 ref/digest, original coordinator base, clean current
source candidate, every overlap required by the reconciliation validator, and
source postimage hashes. Review the complete post-interruption source diff,
including `afc7ab2`, separately from the validator's overlap subset.

Bind the exact preflight assessments and original run/ledger identities if the
accepted receipt schema includes them. Use distinct `recorded_by` and reviewer;
review the canonical payload hash and candidate. Any subsequent source/candidate,
authority or checkpoint change invalidates dependent bindings. Refresh only
those bindings; do not restart already valid Red or implementation.

A stale submitted request must fail before publication. A consumed receipt
must remain history and must not block a new request solely because its old
revision differs. Failed reopen/preflight leaves state/checkpoint unchanged;
successful reopen creates the next attempt through normal coordinator code.
Keep receipt artifacts in approved runtime/evidence paths so committing a
review document does not accidentally invalidate a source-candidate binding.

### G. Required demonstration and completion evidence

The disposable integration scenario must exercise the actual failure pattern:
two interrupted attempts and a consumed receipt; old and P0 failure records;
P1 authorization; current Green; read-only preflight; reviewed reopen;
historical/current checkpointing; independent candidate review; and normal
integration using the intended trusted verifier. An E2E that stops after
`checkpoint-run` has not proved the integration boundary.

Preserve exact original report bytes, phases, ledger rows, bases and attempt
history. Assert that undeclared/altered evidence, wrong task, stale receipt and
invalid authority are refused without accidental state publication. Check that
passing cases in a failed run receive no Red and that historical Green cannot
replace current Green. Exercise repeated invocation/recovery idempotently.
Test the T10 observer sensitivity in a disposable fixture; its deliberate
negative control is not a registered product Red.

Inventory consequences for CR-1/CR-2 historical evidence and final workstream
completion when the whole-plan digest changes. Reuse their existing supported
scope-compatible history; do not reopen integrated tasks or demand new Red
merely because CR-3 changed the plan. Final workstream verification still needs
its full current plan and semantic review; a CR-3 task pass is insufficient.

The final evidence index names immutable candidate/contract/runner identities,
original and new run IDs with per-case outcomes, continuity decisions, T21
approval, T10 sensitivity evidence, preflight digests, reviewed receipt,
post-reopen checkpoint, Refactor outcome, semantic/TaskResult review and actual
verification/integration receipts. A changed candidate renews its current
Green/review checks as required; it does not erase historical Red.

### H. Concrete stop conditions and recovery from failures

Stop dependent mutation when authorization is absent, authority/state diverge,
source is unexpectedly dirty, provenance cannot be validated, a behavioral
change lacks required Red, or the trusted verifier path is unresolved. Report
one precise blocker with the command, exit/status, relevant identities, violated
criterion and smallest correction. Continue independent authorized preparation.

A stale report/review binding calls for renewing that binding; a broken runtime
transition calls for its regression/fix; genuinely missing historical evidence
calls for an explicit disposition. None automatically means restart CR-3.
If independent semantic review finds T10 continuity inadequate, identify the
specific changed behavior and evidence gap, then update the same scoped
package. Do not silently extend the T21 exception to T10 or demand synthetic Red.

Once these finite gates pass, proceed through the authorized work. Do not ask
for another prose-proposal review solely because an implementation choice
changed within the accepted scope. New scope, trust-boundary changes or
contradictory evidence require explicit escalation with the concrete delta.

## Current boundary and validation

CR-3 remains interrupted at revision 27 and base `2c508ff`; no runtime repair
or scoped-amendment approval is claimed. This human request authorizes the
present diagnosis and review correction, not an implicit T21 waiver.

The diagnostic used the real receipt validator in read-only mode, inspected
all CR-3 Red-phase report outcomes and the exact digest-selection logic, and
checked the canonical specification against review-added gates. It also
inspected the task-base verifier snapshot path. No behavioral run, accepted
plan mutation or state transition was performed. Protected contract/runtime
files and authority refs were hash-checked before and after documentation edits.
