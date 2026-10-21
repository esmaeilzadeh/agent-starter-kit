# Task 2 regression-aware TDD gate amendment

## Current contract

Task 2 owns identity, immutable storage and codec behavior. The TaskResult gate
requires every Red command to exit nonzero, even when all assigned cases are
classified as regressions and therefore correctly pass at baseline.

## Proposed plan change

Keep product What/Why, specification criteria, and all existing Task 2 cases
unchanged. Extend Task 2 with a focused gate correction and case `2/10`:

- permit a passing Red result only when the TaskResult names the exact accepted
  task-scoped test IDs and every one is classified `regression` in the accepted
  test plan;
- keep rejecting a passing Red result if the task contains any `new` case, or
  the recorded IDs are missing, extra, or mismatched;
- add `evidence.py`, `driver.py`, the dedicated regression-gate test, and the
  TaskResult evidence guide to Task 2's owned paths;
- preserve the existing Task 2 regression classifications and all test behavior.

The gate defect appeared when Task 2's nine existing cases all passed at Red.
Final Green also passed, but the validator could not accept an honest TaskResult.
The proposed change aligns TaskResult validation with the accepted `new` versus
`regression` test classifications and preserves meaningful Red evidence.

## Impact and alternatives

Only the TaskGraph's Task 2 owned paths, Task 2 test scope, `test-plan.json`,
`plan.md`, this amendment record, and TaskResult validation/documentation are
affected. Deferring the fix leaves Task 2 unable to integrate. Fabricating a
failing assertion or misusing a non-behavioral exemption would make evidence
false. The narrow plan amendment is therefore the viable path to complete the
already authorized workstream.

## Decision

The user selected the recommended Task 2 scope amendment. Obtain exact-revision
independent plan review and renew accepted-tests authority before implementation.
No product acceptance criterion changes.
