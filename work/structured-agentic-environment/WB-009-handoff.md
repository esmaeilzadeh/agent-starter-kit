# WB-009 cross-machine checkpoint

Checkpoint requested by the human on 2026-10-10: commit and push the current
project, including the review report, to continue on another computer.
This is unfinished work, not an approved implementation or a passing result.

## Resume here

Branch: `agent/structured-agentic-environment`.
Work: `structured-agentic-environment`. Active task: `WB-009`.
The runtime state remains `running`; that describes the task assignment, not a
live worker on the other computer. Check for existing workers before taking over.
The current machine's implementation writer was told to stop editing for this
checkpoint. Do not run concurrent writers against this branch.

Read `plan.md`, `test-plan.json`, `inner-loop/tasks.yaml`, the current JSON spec,
`inner-loop/evidence/WB-009-draft-review.md`, and
`inner-loop/evidence/session-evidence-correction.md` before continuing.
The old `implementation-handoff.md` describes the planning boundary and is
superseded by this checkpoint for current execution status.

After cloning, or from a clean existing checkout:

```sh
git fetch origin
git switch agent/structured-agentic-environment
git fetch origin refs/ask/accepted-tests/structured-agentic-environment:refs/ask/accepted-tests/structured-agentic-environment
./ask inner-loop status structured-agentic-environment
./ask check-clean
```

The accepted-contract authority ref is
`0efcd91680fb8f4bc3d7c57e3bd43efe5413f92c`; ordinary branch fetching does not
install this custom ref. Do not silently replace a conflicting local authority.
The accepted contract revision is
`1898b635e67d50056cb7006d27037dfc84358970`, pinned by commit `d0dc1b0`.

## Current implementation and evidence

- WB-001 through WB-008 are recorded integrated, but the correction report
  withdraws earlier false independent-review and red/green claims for WB-006
  through WB-008. Their statuses do not establish semantic completion.
- AppTest migration commit `f75b434` collected ten tests: two passed and eight
  failed assertions without app exceptions. This is actual execution history,
  not a final green result or valid red history for the two passing cases.
- Current checkpoint includes incomplete browser/performance tests,
  `benchmark_workbench.py`, and an unwired production helper
  `workbench_loading.py`. The drafts have passed Python syntax checks only.
  No all-case red or final-green run has been executed for these drafts.
  Committing the helper for transfer does not establish test-first history.
- The independent draft review identifies missing assertions, invalid browser
  interactions, weak cache checks, and incorrect benchmark measurements.
  Repair those tests without dropping the accepted sixteen WB-009 obligations.
- Next: finish executable test design, capture genuine assertion failures at
  committed revisions where possible, repair the reviewed UI/projection paths,
  run actual browser and latency checks, obtain independent candidate review,
  then run `./ask verify` and record the honest result. Missing genuine historical
  red evidence remains unresolved; never manufacture it or claim a full pass.

The previous full Verify attempt at `f761709` passed 37 static checks but failed
behavior checks and the isolated candidate-source stability guard. The separate
verification stability issue is parked on develop; it is not WB-009 repair scope.
The captured evidence is retained for inspection, including rejected attempts.
The checkpoint explicitly archives the normally ignored traceability records and
model publications so another machine can inspect the same history. Raw logs are
preserved byte-for-byte, including one historical trailing-whitespace line; their
contents are not new approvals. Transient lock files are excluded.

## Environment and sequencing

Use the pinned Streamlit 1.59.2 and Playwright 1.63.0 requirements. Chromium was
installed on this machine; install it on the new machine if needed. Local UI
processes and browser binaries are not transferred through Git. Launch the UI
with `./ask ui` after installing the documented environment.

Implementation uses the human-selected Luna model; independent review uses
the generated kit reviewer (GPT-6.1 Sol, high). Keep one committing writer.

Finish the active task through its real gates before taking unrelated work.
Dark mode, defaulting to dark, is queued on `develop` in
`.later/workbench-dark-mode-default.md` (commit `71ee6ed`). The verification
stability issue is `.later/verify-candidate-source-stability.md` (`6d6fd35`).
Neither later task has started. Do not merge or change acceptance criteria as
part of this transfer.
