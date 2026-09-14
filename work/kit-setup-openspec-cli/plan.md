# Plan

## Specification

`specs/current/kit-setup-openspec-cli.md`

## Approach

Extract a TTY-free helper `_ask/scripts/ensure-openspec.sh` that reads the pin,
validates package/revision, checks `$HOME/.local/bin/openspec`, and optionally
runs npm with prefix `$HOME/.local` under a Python 120s kill. `setup.sh` stages
call it last (after issue-context). Help text and Build Spec §22.10 document
the stage. Overlay/install/self-install stay unchanged.

Tests stub `npm`/`node` and use a temp `HOME`. Do not run the TTY wizard.

## Work breakdown

1. Helper `ensure-openspec.sh` + `_ask/tests/test-ensure-openspec.sh`
2. Wire `setup.sh` OpenSpec stage; `--help` and `./ask` usage; non-TTY test
   that the helper is not invoked
3. Build Spec §22.10, ADR-0018, README setup row
4. `./ask verify` (or the new tests plus existing setup tests)

## Risks

- Real `HOME/.local` must never be the test prefix.
- npm `EEXIST` on an existing bin stub; helper must replace that path first.
- Cursor-first `node` on PATH: `--prefix "$HOME/.local"` still isolates the
  install.

## Verification approach

`_ask/tests/test-ensure-openspec.sh`, existing `test-setup-human-only.sh`
extended so non-TTY does not run a logging `npm`, grep that `setup.sh` calls
the helper, `test-ask.sh` help still passes.

## Out of scope for this plan

`askit` overlay/self-install install. `./ask openspec`. Gate fail-closed
changes. GNU-only `timeout`.
