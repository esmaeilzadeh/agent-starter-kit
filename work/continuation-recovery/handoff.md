# CR-3 continuation handoff

Updated: 2026-10-24. Workstream: `continuation-recovery`, task `CR-3`.

## User direction

Continue the existing CR-3 workstream from its current authorized stage until
its loop is complete. Keep the work within CR-3; do not ask to expand scope.
The user asked to preserve this conversation in a handoff note, commit it, and
push the branch.

## Current repository state

- Branch: `agent/continuation-recovery`.
- Source HEAD before this handoff: `16baab34a8ed8892df5f7846e907b469e11bbc73`.
- Tracked worktree was clean; `./ask check-clean` passed.
- CR-3 coordinator state is revision 29, `interrupted`, with three interrupted
  attempts. CR-4 remains pending.
- Accepted P0 plan digest: `bd07e997c4532b686ca09bbb8c32ca4b243b75ef832382e666789b670c6855ec`.
- Candidate `16baab3` has a registered P0 Green run
  `6d36ea28edae44768e7e01e175a91d8a` with 12/12 mapped cases passing.
- The attempt-2-to-3 reconciliation receipt has already been consumed. Do not
  reuse it. A new attempt-3-to-4 receipt is required after the remaining P1
  gates.
- P1 has not been prepared or accepted. The T21 exception is not active until
  the exact declaration is included in independently reviewed and accepted P1.
- The independent source review approved `16baab3` as coordinator/verifier
  source. The required exact-candidate test/semantic review record is still
  absent: `./ask traceability check-completion` reports the missing
  `traceability/reviews/16baab34a8ed8892df5f7846e907b469e11bbc73.json`.

## Latest continuation state (2026-10-24)

- The exact coordinator/verifier source review is committed and pushed in
  `31c83a6`; its artifact approves source commit `16baab3`.
- P1 is drafted but not yet accepted. Its test-plan digest is
  `cc23aca958fc519cf63b867e58b37a3c9c721ae943b59f198d38ecb61e93c7db`; it
  contains 15 exact historical Red continuity rows and the T21 exception
  declaration bound to the approved decision record.
- Historical authority commits from attempts 1–3 are retained under exact
  `refs/ask/accepted-tests-history/continuation-recovery/<commit>` refs and
  inventoried in `cr3-authority-retention.json`.
- CR-T13 is documented as **cannot reproduce as mapped**. P1 changes its
  scenario to the single cycle its test actually executes and keeps that as a
  regression guard; it has no historical Red continuity row and no fix claim.
  CR-T60 remains the reproduced consumed-receipt defect.
- Remaining: independent review/acceptance of the exact P1 plan, P1 Green and
  read-only preflight, fresh attempt-3-to-4 receipt/reopen, checkpoint, exact
  candidate semantic review, and normal integration.

## Corrected per-case Red inventory

Correction to the previous handoff: I incorrectly treated setup/runtime errors
in sibling cases as invalidating behavior Red for the entire run. The harness
stores outcomes per case. A registered Red report with complete collection and
the target case recorded as `failed` / `behavior_assertion` is valid Red for
that case; sibling cases recorded as setup/runtime errors do not erase it.
Those sibling cases themselves do not receive Red. This matches
`unittest_runner.py`'s per-case `failure_kind` and `completion.py`'s per-case
Red selection.

| Test | Valid Red evidence | Current P0 Green | Disposition |
| --- | --- | --- | --- |
| CR-T10 | `b50dd24e0ef04a2aacff4c4a26db4dd5` on `3196a591e2ee0c75ee0bda1539a9319555273662` | Pass in `6d36ea28edae44768e7e01e175a91d8a` on `16baab34a8ed8892df5f7846e907b469e11bbc73` | Valid behavior Red; retain continuity evidence. |
| CR-T11 | `b5e4fc3b34c14e5a93312d2744be9adf` on `ad716fec75e1aae27b198073b6fc6a5442d71780` | Pass in `6d36ea28edae44768e7e01e175a91d8a` | Valid behavior Red. Sibling setup/runtime errors do not invalidate this case's recorded assertion failure. |
| CR-T12 | `b5e4fc3b34c14e5a93312d2744be9adf` on `ad716fec75e1aae27b198073b6fc6a5442d71780` | Pass in `6d36ea28edae44768e7e01e175a91d8a` | Valid behavior Red. Also preserve the separate failed `final_green` outcome in `6a96d09a0d4c4394951b47fa33a14dd7`; that run is not Red. |
| CR-T13 | None. It is a setup/runtime error in `b5e4fc3b34c14e5a93312d2744be9adf`; its case outcome is `passed` in Red-phase run `f8207e36d1794b499e043ba263cacb32`. | Pass in `6d36ea28edae44768e7e01e175a91d8a` | **Cannot reproduce as mapped.** The accepted scenario said two reopen cycles; `test_guard_rollback_and_explicit_attempts` invokes one. P1 changes the scenario to that one cycle and keeps it only as a regression guard; no two-cycle fix or Red is claimed. The actual receipt-selection defect remains CR-T60. |
| CR-T14 | `b5e4fc3b34c14e5a93312d2744be9adf` on `ad716fec75e1aae27b198073b6fc6a5442d71780` | Pass in `6d36ea28edae44768e7e01e175a91d8a` | Valid behavior Red. Sibling setup/runtime errors do not invalidate this case's recorded assertion failure. |
| CR-T19 | `f21a95f6b4c4499aacf37a3ffd27a77d` on `94458d8376a75f052adbf2c4737f4f3c18cef4b6`; `dab908b39596441086d57106b8c816ec` on `8e61c14f6deafb334d3d4cbb8230abfde9358d5f`; also `b5e4fc3b34c14e5a93312d2744be9adf` | Pass in `6d36ea28edae44768e7e01e175a91d8a` | Valid behavior Red; retain original report/ledger identities and assess plan continuity. |
| CR-T20 | `b50dd24e0ef04a2aacff4c4a26db4dd5` on `3196a591e2ee0c75ee0bda1539a9319555273662` | Pass in `6d36ea28edae44768e7e01e175a91d8a` | Valid behavior Red. Its later setup/runtime error does not erase the earlier case-level Red. |
| CR-T21 | None. The case is a setup/runtime error in `b5e4fc3b34c14e5a93312d2744be9adf` and passes in other Red-phase reports. | Pass in `6d36ea28edae44768e7e01e175a91d8a` | Approved narrow historical-Red-unavailable exception; remains inactive until independently reviewed P1 is accepted. All behavior checks and current Green remain mandatory. |
| CR-T58 | `e2a9dc4b3d5e41789117fae0b9623e93` on `5acba992f8cf928007f077451d5c23b1017d5eaa`; `f8207e36d1794b499e043ba263cacb32` | Pass in `6d36ea28edae44768e7e01e175a91d8a` | Valid behavior Red. |
| CR-T59 | `f8207e36d1794b499e043ba263cacb32` on `fb1a0fc5735f3764d5ad5cf28a8beec22f22cc04` | Pass in `6d36ea28edae44768e7e01e175a91d8a` | Valid behavior Red. |
| CR-T60 | `e2a9dc4b3d5e41789117fae0b9623e93` on `5acba992f8cf928007f077451d5c23b1017d5eaa`; `f8207e36d1794b499e043ba263cacb32` on `fb1a0fc5735f3764d5ad5cf28a8beec22f22cc04` | Pass in `6d36ea28edae44768e7e01e175a91d8a` | Valid behavior Red for consumed-receipt selection/atomicity. Keep distinct from T13's one-cycle mapped test. |
| CR-T61 | `e2a9dc4b3d5e41789117fae0b9623e93` on `5acba992f8cf928007f077451d5c23b1017d5eaa`; `f8207e36d1794b499e043ba263cacb32` | Pass in `6d36ea28edae44768e7e01e175a91d8a` | Valid behavior Red. |

The full P0 task Green report `6d36ea28edae44768e7e01e175a91d8a` records 12/12
planned cases passing on candidate `16baab34a8ed8892df5f7846e907b469e11bbc73`.
That is case execution evidence, not task completion: exact-candidate semantic
review is still missing, P1 is not accepted, and the live attempt remains
interrupted.

## Exact next work

Continue the accepted CR-3 loop. Review and accept the exact P1 package. CR-T13's unsupported two-cycle claim
is recorded as “cannot reproduce as mapped”; P1 retains only its one-cycle
regression guard and excludes it from historical Red continuity. CR-T60 keeps
the actual receipt-selection Red and Green. Then complete independent P1 review/acceptance, P1 current Green and
read-only preflight, a fresh exact-candidate review, a new reviewed
attempt-3-to-4 receipt, real reopen/checkpoint, and integration evidence.
CR-4 remains pending until CR-3 completes.

Evidence rule: ledger rows bind the report, phase, and candidate; each test's
phase/outcome/failure kind comes from its own `results.json` entry. A target
case is Red only when the registered Red report has complete collection and
that case is a behavior assertion failure. An error in another case does not
invalidate this case. Never count a setup/runtime failure as Red. A new case
with no valid Red follows the cannot-reproduce/exception disposition; do not
invent a Red or silently fix behavior that has not failed.

No tests were run for this documentation-only handoff update.
