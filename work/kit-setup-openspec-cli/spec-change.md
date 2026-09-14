# Specification Change Proposal

## Current specification

`specs/current/kit-setup-openspec-cli.md` (b4eb675)

## Proposed change

Apply Spec Challenge PASS clarifications. Grill Q1–Q3 unchanged.

- OpenSpec skip/warn does not force setup non-zero; remaining stages do.
- Stage order: after tracker, MCP, and issue-context; before finish notes.
- `node`/`npm` means `command -v` finds them.
- Pin: non-empty `package` and `revision`; `revision` not `latest`.
- Version checks use `$HOME/.local/bin/openspec` only; compare trimmed stdout.
- Overwrite may replace a conflicting `$HOME/.local/bin/openspec`; prefix stays
  `$HOME/.local`.
- 120s bound kills and reaps npm (portable timer; not GNU `timeout` only).
- Helper `_ask/scripts/ensure-openspec.sh`: 0 success, 1 skip/warn, 2 bad pin.
  Wizard warns on 1 or 2 and continues.
- Tests cover helper cases plus wizard wiring (`setup.sh` invokes the helper).

## Why the change is needed

Challenge PASS found ambiguities and an overwrite/npm `EEXIST` conflict. Product
decisions are unchanged.

## Impacted artifacts

`specs/current/kit-setup-openspec-cli.md`, `specs/proposals/kit-setup-openspec-cli.md`

## Impacted workstreams

`kit-setup-openspec-cli` only.

## Migration / transition notes

None.

## Acceptance criteria for the change

CURRENT spec includes every clarification listed above.

## Decision

Accepted 2026-09-14. Challenge verdict PASS: technical clarifications only;
defaults-OK Grill decisions stand.
