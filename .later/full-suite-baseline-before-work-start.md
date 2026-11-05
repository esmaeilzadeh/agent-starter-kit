# Require a fresh full-suite baseline before starting work from unverified source

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `continuation-recovery` side conversation, 2026-10-22
- **Start later:** new session, `./ask start-work full-suite-baseline-before-work-start`
- **First stage:** 01 Grill; destination is clear
- **Tags:** workflow, testing, git-flow, continuation
- **Attribution:** user-reported gap in work-start verification
- **Affected responsibilities:** workstream intake, branch creation, verification evidence, interrupted work
- **Publication status:** draft

## Why

A new workstream can start from a commit containing source changes made after the latest recorded full-suite green result. The relevant task tests may pass while unrelated failures already exist, making later regressions difficult to distinguish. This can happen when a new job is requested during another workstream's implementation, before that implementation has earned a full-suite green result.

## Proposed What (unapproved)

- Bind each full-suite green result to the exact source commit (and verification plan) it tested; make that evidence discoverable by work-start intake.
- Before creating a work branch, compare its proposed base with the latest full-suite-green commit. If intervening commits change source or test files, rerun the required full suite on the proposed base and record the result before allowing the new branch to start.
- If a second job is requested while the current workstream is in implementation and its source changes are not yet covered by a full-suite green result, park the second job in `.later/` and keep the active workstream intact. Do not create a new work branch from that unverified implementation state.
- Once the active candidate has a recorded full-suite green result, allow the queued job to start from that tested commit, subject to the normal clean-worktree and workstream gates.
- Treat changes limited to non-source files according to an explicit path classification; do not silently assume they invalidate or preserve the baseline.
- Add intake regressions covering an unchanged tested base, source changes since the latest green commit, a new-job request during unverified implementation, and resumption after a fresh full-suite green result.

## Note

This card records a proposed intake and baseline-verification rule. It does not authorize changing the active `continuation-recovery` workstream or starting a second workstream in this session.
