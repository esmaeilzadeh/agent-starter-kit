# CR-1 integration scope amendment

## Current specification

The accepted recovery contract remains CR-01–CR-08 in
`specs/current/continuation-recovery.json`. The sealed plan assigns CR-1 its
new immutable recovery fixture and assertions, while listing the existing
inner-loop reliability suite as a required integration check without assigning
its assertion source to CR-1.

The failed CR-1 integration run showed that the recovery guard currently rejects
valid setups and legacy result cases exercised by that suite. The failure occurs
before several existing assertions execute, so changing only CR-1's new tests
would leave required integration evidence red.

## Proposed change

Expand CR-1 ownership to include `_ask/tests/inner_loop_reliability.py` and bind
that source in the CR-1 cases in `test-plan.json`. CR-1 may update its disposable
fixtures and exception expectations where the new recovery contract deliberately
changes the reported failure classification. Preserve the suite's behavior
assertions: it must continue to prove that invalid integration is refused,
valid integration succeeds, and concurrency/interruption guarantees hold.
Production behavior remains governed by CR-01–CR-08. Do not alter expected
outcomes merely to make the tests pass.

Update the CR-1 row and required integration checks in `plan.md`; update only
CR-1 `owned_paths` in `inner-loop/tasks.yaml`; bind the reliability assertion
source in all CR-1 test cases in `test-plan.json`. Leave the accepted spec,
intent, CR-2–CR-4 ownership, task order, and product workstream unchanged.

## Why the change is needed

The normal CR-1 integration gate executes `_ask/tests/test-inner-loop-reliability.sh`.
Its tests use the existing public state and integration APIs. CR-1 changes the
recovery admission boundary those APIs now enforce, so the regression suite is
part of the task's compatibility outcome and must be inside its reviewable
source boundary.

## Impact

- CR-1 gains one owned assertion module; no accepted requirement changes.
- The test-plan source binding changes and therefore requires fresh independent
  plan review and accepted-pin registration before CR-1 resumes.
- Existing aggregate checks stay mandatory. They are not replaced by a relaxed
  or task-specific verifier.
- CR-1 Red/Green evidence and candidate review must be renewed after amendment.

## Decision

Approved by the user on 2026-10-22 with “expand”, selecting expansion of CR-1
scope after the integration failure was presented. The accepted CR-01–CR-08
contract and previously approved intent remain byte-identical.
