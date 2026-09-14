# Acceptance

## Workstream

`kit-setup-openspec-cli`

## Specification

`specs/current/kit-setup-openspec-cli.md`

## Evidence

- `./ask verify --work-id kit-setup-openspec-cli` pass at
  `296db0c94a995781bd78dae96f262cd599c41d02` (all `_ask/tests/test-*.sh`).
- Review BLOCK then 08: non-scalar pin exit 2, pin identity on warnings,
  empty revision / symlink / timeout-reap tests.
- `./ask record-result` at `7226a839bf0998b2757b05e79cee9b567ae7a639`.

## Residual risks

- No pseudo-TTY end-to-end of the wizard.
- Verification SHA `296db0c` vs later evidence commits (same known drift).
- Marked-pilot gates still fail closed if `~/.local/bin/openspec` is missing
  or not `1.13.0` after a setup skip.

## Acceptance decision

ACCEPTED. Human confirmed 2026-09-14. Push after Accept.

## Accepted commit SHA

7226a839bf0998b2757b05e79cee9b567ae7a639
