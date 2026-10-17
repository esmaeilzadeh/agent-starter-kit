# Workbench unblock validation

Code candidate: `e514444977dcfd09cfff6114ac2e45251378018e`.
Original missing-evidence block resolved; RWB-108 readmitted at unchanged base,
coordinator revision 66. RWB-109 remains pending formal integration of RWB-108.

## Historical evidence

The original ignored execution ledger was recovered from commit
`d21dfcc2cca1ebbacee5c7de4025b0d85e4e518a`, before Git stopped tracking it.
The restored bytes, WB-003 report, and log hashes match their original records.
No execution entry or approval was invented. The provenance and recovery
instructions are in `inner-loop/evidence/RWB-108-ledger-recovery.md`.

`python3 -m unittest _ask.tests.test_revising_pilot -v`: all 12 tests passed.
The earlier conclusion that the missing ledger was unrecoverable was incorrect;
Git history contained it. The historical task's valid review/integration remains
independent of the later failed workstream completion.

## Browser correction

The original detached navigation failure selected `ask-status`. Explicit model
selection exposed a second failure: Workstream rerun reset Source after the
client value assertion. The final helper waits for the server rerun to finish,
then selects the working-tree snapshot used by the admitted benchmark projection.
The original assertions and admission checks remain in force.

Detached navigation: passed, 1 test in 14.999 seconds.
Narrow independent review: APPROVED in
`inner-loop/evidence/unblock-review-e514444.md`.

The required `./ask verify` was started on this candidate with the pinned UI
Python and Chrome. All five substantive browser journeys passed in run
`ee266f84491543d3b51d6d8231077572`, including keyboard/accessibility and genuine
WB-003 evidence. Completed instrumented cases had no failures when the human
requested stopping. The verifier was interrupted during the benchmark (exit 130),
and its candidate worktree/processes were cleaned up.

Ignored runtime logs: `traceability/rwb109/unblock-nav-red.log`,
`unblock-nav-rerun-barrier.log`, and `unblock-verify.log`.
No completed benchmark or final verification verdict is claimed for this
candidate. Earlier benchmark JSON belongs to earlier candidates.

## Remaining

Formal TaskResults/integration, completed RWB-109 benchmark, full independent
workstream review, final Verify, actual human comprehension, and Accept remain.
The narrow review approves only these technical fixes. Work stopped at the
human's request after resolving the original blockers.
