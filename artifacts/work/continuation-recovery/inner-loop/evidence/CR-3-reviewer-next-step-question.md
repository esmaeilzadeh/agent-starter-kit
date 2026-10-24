# Reviewer question: next authorized step for CR-3

Date: 2026-10-23.

Please review the unresolved CR-3 evidence and plan proposal, then advise what
the coordinator should do next. Do not modify task state, rewrite historical
reports, or treat a passing run as Red.

## Current state

- Workstream: `agent/continuation-recovery`.
- Coordinator state: revision 27; coordinator SHA
  `2c508ff4248f16a3e3121d33a0fae7297c9b378e`.
- CR-3 attempt 2 remains interrupted at candidate
  `08339eb5bf9802cf815819bf3168f13c5296d9bd`, under accepted plan digest
  `a8c13188a26489e67173333ca4f69ac572f00836a3f32e77929ee82a1ff99025`.
- After interruption, the T10 ledger-snapshot assertion correction was
  committed as `afc7ab2`. It has not been run in a reopened attempt and is not
  part of a reviewed candidate or TaskResult. A reviewed source reconciliation
  is required before reopening.
- The fixed `reconciliation-CR-3.json` receipt still names the earlier
  attempt-1-to-attempt-2 transition. The R2 review finding says it conflicts
  with the current state and blocks another reopen.

## Evidence audit

The case ledger is in `CR-3-red-provenance-audit.md`. Its conclusions are:

- T10 has valid earlier Red for its original assertion. The added R3
  post-crash ledger check is not yet executed.
- T11's `regression` classification was narrowly approved in the current
  plan review.
- T12's assertion passed against unchanged task-base production in the first
  registered Red-phase run. A later failing `final_green` run remains in that
  phase and is not Red.
- T13's existing assertions passed at the initial test-only candidate. The
  newly exposed repeated interrupt/reopen lifecycle still needs a real Red.
- T21's implementation changes predate its assertion source. Its purported
  Red-phase run passed all eight cases. No valid Red is retained.

The concrete plan proposal is in `CR-3-plan-amendment-proposal.md`. It proposes
adding `attempts.py` to CR-3 ownership, narrowly classifying T12 as a regression,
extending T13 with the second interrupt/reopen and stale-receipt checks, and a
T21-only exception that explicitly makes no Red-to-Green claim.

## Questions for the reviewer

1. Is the T21-only TDD exception acceptable given the immutable provenance, or
   should CR-3 remain stopped under the current Red requirement? If it is not
   acceptable, identify a valid evidence path that uses existing immutable
   assertions and implementation lineage without manufacturing a failure,
   overlaying newer tests onto older production as if it were a registered
   run, or relabeling a phase.
2. Is the narrow T12 regression classification supported by the task-base
   source comparison and registered run `b50dd24e0ef04a2aacff4c4a26db4dd5`?
3. Does adding `attempts.py` to CR-3 ownership and extending T13 as proposed
   correctly route the consumed-receipt fix through the accepted-plan path?
4. If the amendment is supportable, specify the exact review and
   `traceability accept-plan` evidence required before reopening. Preserve both
   interrupted attempts and their original plan-bound reports.

Please return a clear verdict (`APPROVE`, `REQUEST CHANGES`, or `NO VALID
RESOLUTION`) with the reasoning and any exact amendment required. Until then,
leave the accepted plan and inner-loop state unchanged. The note commit is
documentation only; `afc7ab2` remains unreviewed post-interruption source.
