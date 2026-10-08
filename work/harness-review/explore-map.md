# Explore Map: Harness reliability

## Destination

Confirm and repair R1/R2 against current main without expanding the harness into a security sandbox or an evaluation platform.

## Notes

The user authorized committing the handoff, continuing the work, merging main into develop while preserving the inbox, and proceeding without further permission requests. Local merge ed6fa62 preserves both inboxes; all 35 mandatory baseline checks passed. Pinned skills prepared and bindings synced. No extra skills needed.

## Decisions so far

- Current source: integration/state/verification code is unchanged from 9602217d6e0f7d63dc9251ba8bd1673eb7d8f694. TaskResult producers are runtime agents and fixtures; no other executed-evidence gate exists.
- Evidence boundary: cooperative coordinator owns review records and executes the committed CheckPlan in a detached candidate worktree using coordinator-owned runner code. Worker reports remain TDD history. Local writable repository access is not an authentication boundary.
- Candidate identity: full work/task/base/candidate identity plus a digest of the result and review artifact prevents accidental reuse. Record review through a coordinator operation, never infer authority from worker reviewer_ack alone.
- Concurrency: local POSIX processes serialize initialization, CAS and state invariants with flock; write complete same-directory temporary files and replace atomically. Integration holds the same lock through verification, Git FF and state fold; cancellation cannot interleave.
- Fast-forward produces the exact verified commit/tree, so a redundant second check run is unnecessary. Detect source/check mutations and ref drift before advancing.
- Tests: public state operations and coordinator run/review/integration operations, with real subprocess contention and disposable Git repositories.

## Not yet specified

None blocking implementation under the user's instruction to proceed autonomously. Limitations are explicit in the spec.

## Out of scope

R3 interactive decision pilot, R4 artifact-depth pilot, R5 comparative evaluation, multi-host locks, hostile worker isolation, changes to outer Verify/Accept authority. Companion decision-review-harness-note.md was not found in this checkout.

## Handoff to Intent

Implement R1/R2 as one agent/harness-review workstream. Preserve E2E, single writer, FF-only integration, and commit/result lineage. Use coordinator-controlled verification and review records; atomic file-backed state for local cooperative processes. See specs/current/harness-review.md for acceptance checks and work/harness-review/plan.md for sequence.
