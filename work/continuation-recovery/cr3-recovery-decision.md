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

## Bounded work package and next action

1. **Prepare the concrete contracts and decision once.** Consolidate the
   exact ownership, selectors, exception/continuity fields and P0/P1 staging
   already described in revisions 4–5, using the corrections in this document.
   Include `attempts.py`, the shared historical-run validation and completion
   paths, required traceability authority/review modules and their tests.
   Obtain the single scoped human decision for T21's evidence exception and
   this bounded enforcement/bootstrap work. Keep approved intent bytes and
   CR-01–CR-08 unchanged. Further narrative proposal rounds are unnecessary.
2. **Review and accept the exact implementation contract.** P0 authorizes
   mapped implementation and tests while CR-3 remains interrupted; no T21
   exception is active yet. Historical records stay immutable. Retain P0/P1
   staging only to separate implementation authority from activation of the
   explicitly authorized exception, not to restart prior behavioral slices.
3. **Use one disposable recovery scenario as the feedback loop.** Seed actual
   interrupted-attempt/consumed-receipt conditions, retained old failures and
   reviewed amended obligations. Exercise report publication, read-only
   preflight, repeated reopen, historical/current checkpointing, semantic
   review, candidate verification and integration through real coordinator
   entrypoints. Reject stale/altered records. Assert original run IDs, phases,
   summaries, attempts and receipt bytes survive. New behavior gets authentic
   Red; already established behavior keeps its existing evidence.
4. **Include the real verifier boundary in that scenario.**
   `_ask/scripts/inner_loop/evidence.py:456-465,514-515` snapshots the verifier
   from the task's original base; `verify_candidate` requires that verifier's
   completion receipt. A current-source completion pass alone cannot prove
   CR-3 integration. Exercise the old-base verifier with the amended contract
   and expose any supported compatibility/migration work in this same bounded
   repair. Preserve the base, trusted runner provenance and normal completion
   checks. Do not switch to candidate-controlled verifier code or reset the
   task base merely to get a pass. A needed trust-boundary change requires
   explicit review/authorization; report an exact reproduced incompatibility
   instead of initiating another speculative proposal cycle.
5. **Finish the implementation before final candidate review.** Implement the
   receipt fix and shared evidence-applicability checks under accepted ownership.
   Validate old evidence under its original authority and current applicability
   authorization; keep current Green/review exact. A read-only preflight can
   share this validator with finalization. Historical source hashes establish
   provenance, while reviewed semantic continuity establishes relevance.
   P1 activates only the approved T21 exception and explicit continuity records.
6. **Apply the demonstrated sequence to the live workstream.** Require reviewed
   exact source reconciliation covering `afc7ab2`, the receipt correction and
   other authorized edits. Reopen through the coordinator, attach validated
   runs, obtain current Green, Refactor outcome, independent semantic/candidate
   review and normal integration evidence. CR-4 stays dependent on CR-3.

A reviewer may block on a concrete contradiction with an accepted requirement,
missing real evidence, or a reproduced failing check. An optional algorithm,
renaming, new fingerprint format, or stronger paperwork requirement does not
restart the task. Resolve implementation findings in the same candidate cycle.

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
