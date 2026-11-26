# Intent: Repair the check-workstream guidance test fixture

## What

Copy `client_ignores.py` into the temporary repository fixture used by `test-check-workstream-guidance.sh` so the test reaches its intended guidance assertion.

## Why

The test currently errors during module import before it can check the existing `check-workstream` behavior.

## Non-goals

Change no production behavior or other tests.

## Known assumptions

The missing module is the fixture's only missing dependency for this test.

## Open questions

None.

## Human decisions

The user authorized a separate focused bug-fix workstream.

## E2E

Applicability: `not_applicable`

Reason: this repair makes an existing shell regression fixture self-contained; its focused test is sufficient.
