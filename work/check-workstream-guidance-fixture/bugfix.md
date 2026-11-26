# Bug fix: self-contained check-workstream guidance fixture

## Existing expectation

`test-check-workstream-guidance.sh` runs `check-workstream` in a temporary Git repository and verifies that a missing spec produces guidance rather than a hard lock.

## Reproduction

Run `_ask/tests/test-check-workstream-guidance.sh` on the CWH base commit `86ea1616da99fbc44d5b5c57e42163c227d4b536`.

## Observed

The fixture copies `inner_loop` but omits `_ask/scripts/client_ignores.py`. `inner_loop.local_verifier` imports that module and exits with `ModuleNotFoundError` before the intended assertion.

## Expected

The fixture includes all modules required by `check-workstream`, and the test reaches and passes its guidance assertions.

## Focused change

Copy `client_ignores.py` into the temporary repository alongside `inner_loop`.

## Verification

`_ask/tests/test-check-workstream-guidance.sh` passes on the reproducing base after the fixture copies `client_ignores.py`.
