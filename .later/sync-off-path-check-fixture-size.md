# Keep the off-path test fixture small

- **Status:** parked (not live; no `agent/*`)
- **Found during:** client-workflow-hooks merged-main verification
- **Start later:** new session, `./ask start-work sync-off-path-check-fixture-size`
- **First stage:** 01 Grill
- **Tags:** testing
- **Attribution:** verification failure at `main` commit `c61ebc7b53a94ab52d3a09641084c6e830ee9db3`; `_ask/tests/test-sync-off-path-command.sh`
- **Affected responsibilities:** static-check fixture setup and cleanup
- **Publication status:** draft

## Why

The test copies the entire `_ask` tree into a temporary Git repository. In the current checkout this includes a local `.venv` of about 594 MB, making `git add` and cleanup exceed the verification run window and fail the check.

## Proposed What (unapproved)

Make the disposable fixture include only tracked kit files, excluding local environments and other ignored runtime data, while keeping the `/off-path` projection assertions unchanged.

## Note

Reproduce the timing and cleanup failure before changing the test. Do not treat the printed PASS line as success if the exit trap returns nonzero.
