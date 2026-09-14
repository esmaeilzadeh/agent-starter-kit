# Acceptance

## Workstream

`openspec-governance-integration`

## Specification

Canonical: `openspec/changes/archive/2026-09-14-openspec-governance-integration/`.
Applied specs: `openspec/specs/kit-openspec-engine/spec.md`.

## Evidence

- `./ask verify --work-id openspec-governance-integration` pass at
  `240364e027680178ad73592f2a7aecb0e490bacd` (OpenSpec preflight +
  `validate --strict`; all `_ask/tests/test-*.sh`).
- Review: ACCEPT WITH RATIONALE (grok-4.6 after same-family warning).
  08 addressed archive detection on `verify`/`status`, pin copy on
  `upgrade-kit`, 04/Grill/intent marker docs, layout + workstream-scope
  globs.
- Baseline: `work/openspec-governance-integration/baseline.md`.
- Later evaluation parked: `.later/openspec-pilot-evaluation.md`.

## Residual risks

- Pin is exact `openspec --version` == `1.13.0`; schema/profile are not
  asserted against global `openspec config`.
- Marked-pilot gates fail closed without that binary. Specified.
- `openspec/specs/` stays empty until apply/openspec-archive.
- Later two-or-three-pilot adopt/revise/abandon is a separate workstream.
- Known verification SHA-vs-evidence-commit drift
  (`promote-kit-specs`) is unfixed.

## Acceptance decision

ACCEPTED. Human confirmed 2026-09-14. Machinery plus recorded baseline.

## Accepted commit SHA

6805eaaecfbfb4c054971c388d683e56b2373ae3
