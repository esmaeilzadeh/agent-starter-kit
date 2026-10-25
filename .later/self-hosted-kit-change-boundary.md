# Keep the kit able to change its own workflow safely

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `continuation-recovery`
- **Start later:** new session, `./ask start-work self-hosted-kit-change-boundary`
- **First stage:** 00 Explore (the trusted bootstrap and upgrade boundary need design)
- **Tags:** inner-loop, workflow, bootstrap, traceability, refactoring
- **Attribution:** user request during `continuation-recovery` attempt 5; no reviewer finding; candidate `50b92a07f6517cac82a400b2161085f576cc7d12`
- **Affected responsibilities:** self-hosting workflow changes, coordinator state transitions, test execution, evidence checkpointing, verifier upgrades
- **Publication status:** draft; publish through `develop` after the active TaskGraph has no writer or resumable candidate

## Why

Self-hosting is a requirement: the project uses the kit to build and change the
kit. The goal is to preserve that dogfooding while keeping the integrity of
verification and integration. When the kit changes its own workflow mechanisms,
the candidate can depend on the mechanism being changed to run tests, validate
evidence, checkpoint results, and authorize integration. This creates recursive
gates: a test run can pass while its wrapper fails because coordinator state or
the TaskResult is stale. Changes to the trust mechanism need a stable,
independent way to validate and adopt the new version.

## Proposed What (unapproved)

Explore and design a small, explicit self-change boundary that keeps the kit in
its own development loop without letting unvalidated candidate code certify
itself. Ordinary project work should continue using the kit. When changing the
coordinator, verifier, or other trust-critical workflow mechanism, validate the
candidate with a previously accepted, source-pinned mechanism (or an equally
small independently trusted bootstrap), then transfer trust only after the
candidate passes its checks and review. Define:

- a trusted bootstrap path for validating changes to the coordinator and
  verifier;
- how test execution reports are produced and then independently checkpointed
  against the exact candidate and coordinator state;
- the state transitions and concurrency rules needed for one coordinator to
  admit, review, and integrate parallel task results safely;
- how upgrades transfer trust from the previously accepted mechanism to the
  new candidate, including recovery after interruption;
- how the project continues dogfooding the newly accepted kit on subsequent
  changes without letting a candidate choose or bless its own verifier;
- which checks can use typed state transitions (such as Rust typestate) and
  which still require validation at persisted-data and Git boundaries.

Compare a minimal Rust coordinator core with a simplified implementation in the
current stack. Recommend the smallest design that preserves self-hosted
development, independent verification of trust-critical changes, auditable
evidence, and recovery. Do not select a language or implementation scope before
Explore and review.

## Note

This is separate from the active continuation-recovery bug fix and from the
parked proposal to reconsider mandatory Red evidence. It does not authorize
implementation or a repository-wide language migration.
