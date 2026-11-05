# CR-3 reviewer decision and stop record

Reviewed production/assertion candidate: `0a50776d7a3c62d64ed45e73e13d1a909120ba24`.
Task base: `2c508ff4248f16a3e3121d33a0fae7297c9b378e`.
Retained checkpoint: `b5d1e6ee121b75ad3dac135df1d3fd28901aa77c`.

Reviewer: `/root`, explicitly assigned by the human: "do it yourself as reviewer and stop".
This is a scoped forensic review of the completion blockers. This coordinator
participated in preceding implementation work; this document does not claim a
new independent implementation approval or replace the earlier delegated reviews.

## Decision

**CR-3 completion: REJECTED. Corrective direction: APPROVED. Confidence: 98%.**
No human product or design choice is needed to determine the corrections below.
The previous broad amend-and-reconcile question is superseded by this review.
Stop after committing this record; do not integrate CR-3, admit CR-4, re-pin the
contract, or change checkpoint authority during this review-only instruction.

The five original findings have implementation/assertion corrections in the
current candidate and prior delegated reviews reported no remaining local gaps.
That does not establish task completion: canonical verification has 38/38
passing checks but a failing spec-to-test completion gate.

## Findings and required correction

### CR3-G01 / P1 — later verification invalidates historical carry-forward

`_ask/scripts/inner_loop/recovery.py:204` reads the shared current
`traceability/completion.json` when validating an earlier checkpointed receipt.
`_scope_compatible_result` then passes that result into the checkpoint-wide
comparison (`recovery.py:310`); the comparator refuses changed retained files
and most additional artifact categories (`recovery.py:475–498`). Consequently,
normal later verification can prevent the coordinator from recording the new
run needed to advance the task.

Observed at this candidate: CR-1 and CR-2 TaskResults are byte-identical to their
checkpoint copies. The ledger grew from 37 to 45 entries with the original 37
as an unchanged prefix. The only changed checkpointed traceability files are
`completion.json` and that append-only ledger. Nevertheless, coordinator
preflight reports a CR-1 contract mismatch and differing runtime traceability.
The latest canonical verification replaced the derived completion projection;
this is insufficient evidence of TaskResult corruption.

Correct historical validation to use evidence bound to the historical task and
candidate while preserving exact report/log/source checks. Distinguish current
derived projections and ordinary new verifier/review artifacts from rewrites
of historical evidence. Add a focused regression for integrated CR-1, a later
CR-3 verification (including a failed completion result), and subsequent run
finalization. Preserve all existing attempts, reports, authority, and TaskResult
bytes. A blanket checkpoint overwrite or deletion of the recovery checks is
not an approved correction. This remains an existing-spec CR-3 behavior fix.

### CR3-G02 / P2 — baseline-green coverage is being required to become Red

A fresh disposable probe ran the final CR-T11 and CR-T14 assertions against
production at the CR-3 task base; both passed. The two final test files were
explicitly overlaid into that disposable checkout. This establishes a useful
behavioral baseline comparison; it is not a coordinator-registered immutable
execution and must not be presented as one.

CR-T11 wraps the pre-existing stale-review assertion helper, whose AST is
unchanged from the accepted contract revision. CR-T14 adds clone/CLI assertions
that also pass against task-base production. Both mapped wrapper methods are
new relative to the accepted contract, so reclassifying these new tests of
existing behavior as `regression` does not reclassify a previously changed
mapped method. Approve a narrow plan amendment for CR-T11 and CR-T14 only,
retaining their selectors, assertions, criteria, and required test types.
Validate the amended plan, obtain a review bound to its exact digest, and
re-pin through the normal coordinator operation before claiming completion.
An artifact-only amendment does not require another human What/Why decision.

CR-T12, CR-T13, and CR-T21 are different: their behavioral fixes still need valid
immutable failure evidence under the accepted execution rules. Do not classify
them as baseline regressions merely to clear the gate, deliberately damage
working production to manufacture a failure, or relabel old execution phases.
Use an honest retained pre-fix assertion/implementation lineage where available;
otherwise record the evidence limitation explicitly and resolve it through the
protocol without claiming a Red→Green history that did not occur.

### CR3-G03 / P2 — previous Red claims contradict the retained reports

Run `6a96d09a0d4c4394951b47fa33a14dd7` contains a CR-T12 behavior-assertion
failure, but its execution and cases are `final_green`; it is a failed Green
attempt, not recognized Red. The structured semantic review describes it as
Red and must be corrected without editing the retained execution report.

Run `517f864631a845e082f9a73fa888ef30`, recorded at immutable `01abc53`, has
phase `red` but exit code 0 and all eight cases passing. The earlier statement
that it captured a valid historical CR-T21 Red was incorrect. The failing
CR-T21 diagnostic probe overlaid newer tests onto older production; that overlay
was absent from the immutable historical run. Preserve both observations and
their distinct provenance. This run cannot satisfy a Red obligation.

## Evidence and endpoint

- `CR-3-reviewer-gate-audit-0a50776.json`: checkpoint/ledger comparisons, exact
  report outcomes, baseline helper comparisons, canonical result and digest.
- `CR-3-reviewer-baseline-probe-0a50776.log`: fresh two-case baseline probe,
  including its explicit overlay/provenance limitation.
- Existing canonical run: 38/38 checks pass; aggregate result fails on missing
  recognized Red/Green evidence. This review did not repeat the full suite.

Production/assertion source, accepted intent/spec/plan, checkpoint ref, and task
state are unchanged by this review. No completion, integration, or acceptance
was recorded. The next coding action is the bounded corrections above, not a
new user approval chooser. Per the human's instruction, this reviewer stops.
