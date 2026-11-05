# Make inner-loop tests fast enough for frequent feedback

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `continuation-recovery`
- **Start later:** new session, `./ask start-work fast-inner-loop-tests`
- **First stage:** 00 Explore
- **Tags:** testing, test-performance, refactoring
- **Attribution:** CR-3 verification candidate `7b78d049c8741a0effeee19e665a0da3d40ac738`; recovery/reliability/traceability test timings
- **Affected responsibilities:** inner-loop unit, integration, and end-to-end verification suites
- **Publication status:** draft

## Why

The current tests called as a unit suite exercise many integration boundaries:
they create temporary Git repositories, commit and clone branches, run fresh
CLI/Python processes, execute the trusted verifier, and inject process crashes.
At candidate `7b78d04`, the combined 53-test recovery and reliability run took
about 134 seconds. Canonical verification separately reported 24 recovery tests
in 91 seconds, 29 reliability tests in 56 seconds, and 29 traceability tests in
56 seconds. This makes routine feedback too slow for the programming inner loop.

Some mapped tests also call other test methods directly, repeating their setup
and integration work instead of sharing focused fixture helpers.

## Proposed What (unapproved)

Investigate and implement a layered test workflow that gives fast feedback while
preserving the existing integration and recovery guarantees:

- Add a fast unit tier for pure state rules, validators, and transitions, using
  in-memory data or narrow fakes where that does not hide Git/process behavior.
- Keep focused process/Git integration tests for checkpoint, clone, and crash
  boundaries; factor shared setup into helpers so test methods do not invoke one
  another and repeat expensive work.
- Keep the full shell, traceability, and end-to-end verification suite as a
  broader acceptance tier, with documented commands for each tier.
- Profile per-test duration and define practical time budgets for the fast and
  focused tiers. Do not weaken required coverage or make slow acceptance checks
  appear to have passed when they were skipped.

When this parked job is later initialized, ask the human to choose its branch
base at that time (current branch, `develop`, or `main`) before creating its
workstream.

## Note

This card records an investigation and implementation proposal only. It does
not authorize starting the workstream or changing verification policy now.
