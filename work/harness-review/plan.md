# Plan

## Specification

specs/current/harness-review.md (CURRENT); one branch: agent/harness-review.

## Approach

Keep state persistence and candidate verification behind the inner-loop public operations. Extend future TaskResult to v2; old results stay archived. Use coordinator review records, a trusted runner over detached candidate code, and local flock transactions.

## Work breakdown

1. Commit Explore/Intent/spec and independently challenge the specification.
2. R2 vertical slice: reproduce competing CAS calls in real processes; serialize state updates, initialize idempotently and atomically replace files. Extend writer/reader/interruption/resume coverage. Commit passing slice.
3. R1 vertical slice: reproduce stale/bare evidence acceptance; implement identity/review and candidate verification. Add coordinator record-review CLI and update existing driver fixtures for v2. Cover failure and successful in-place/FF integration, mutation and recovery. Commit passing slice.
4. Update canonical contracts/docs for future results and local concurrency, sync generated bindings, independently review, fix confirmed findings, audit context and verify.
5. Record executed evidence and SHA, update the resume note and acceptance artifact. Keep R3–R5 explicit as follow-ups.

## Risks

Checks execute project code under coordinator authority, not a security sandbox. Local advisory locks do not coordinate multiple hosts or manual Git writers. Verification under lock may block another caller. Git and state are not one atomic store; retry revalidates after FF-before-fold interruption. Stricter future TaskResults intentionally reject incomplete v1 submissions.

## Verification approach

Public seams: state cas_init/cas_apply/spawn_writer/load_state and coordinator run/review/integrate/cancel/resume. Real subprocess contention with synchronized starts, disposable Git repos and a tiny committed CheckPlan. Capture red and green output. Run existing inner-loop checks and full ask-kit suite. No production data.

## Escalation / spec-change triggers

New security isolation, multi-host support, public workflow scope beyond this v2 migration, weakened mandatory checks, or changes to human semantic authority.

## Out of scope for this plan

R3–R5 pilots/evaluation. Companion decision-review-harness-note.md is absent; no contents inferred.

## E2E

not_applicable: kit CLI/Git journeys are covered by the mandatory shell preset; disposable fixtures provide isolation and reset.
