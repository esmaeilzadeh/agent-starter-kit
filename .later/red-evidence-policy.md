# Reconsider mandatory Red evidence for every test case

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `continuation-recovery`
- **Start later:** new session, `./ask start-work red-evidence-policy`
- **First stage:** 00 Explore (the desired evidence rule and its limits need discovery)
- **Tags:** testing, TDD, traceability, policy
- **Attribution:** user direction during `continuation-recovery` on 2026-10-25
- **Affected responsibilities:** test planning, traceability completion, task-loop workflow
- **Publication status:** parked; not published to `develop`

## Why

The mandatory Red rule can require a failing run even when a test expresses an
accepted specification and already passes. That creates pressure to manufacture
a failure or spend time proving an expected behavior is absent. Reconsider when
passing evidence is sufficient and how to preserve reproduction-first evidence
for actual bug reports.

## Proposed What (unapproved)

- Define when a specification-backed case may count as complete from an
  existing passing run without a corresponding Red.
- Preserve actual reproduction-first Red evidence for reported defects where a
  failing behavior can be reproduced.
- Keep setup/runtime errors distinct from assertion failures and never relabel
  a pass or an error as a Red.
- Update traceability and task-loop rules only after reviewing how the change
  affects task completion, historical evidence, and existing workstreams.

## Note

This is a repo-wide policy proposal, separate from the user-authorized
continuation-recovery bug fix. The user's direction to accept existing passing
tests applies to `continuation-recovery` only and does not authorize changing
global testing policy.
