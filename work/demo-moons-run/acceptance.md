# Acceptance

## Workstream

`demo-moons-run`

## Specification

Canonical: `openspec/changes/demo-moons-run/`.
Kit pointers: `specs/current/demo-moons-run.md`.

## Evidence

- `./ask verify --work-id demo-moons-run` pass at
  `f97f5a96f30fa98b15fa8d3bd2684fcb02ddf2f0` (OpenSpec preflight +
  `validate --strict`; all `_ask/tests/test-*.sh`).
- Registry: `moons-narrow` accuracy `0.8333…` at
  `214394a5a9f39c43afb79536fcb06bfddbc7901f`; `moons-wide` accuracy
  `0.9833…` at `e1c04484b2c3a95a2bb62fbcfb17c63b66127b36`.
- Review: ACCEPT WITH RATIONALE (RV-001 Path A dirty-tree; RV-002 4.1).
- `./ask openspec-archive demo-moons-run` refused before Accept SHA.

## Residual risks

- Literal Path A A5 still trains then record-run; extra commit of
  `train_output.json` is required. Not fixed in this workstream.
- `./ask start-work` forks from `main`; this branch was created from
  OpenSpec HEAD.
- `./ask prepare` hung cloning an already-prepared skill.

## Acceptance decision

HUMAN_APPROVAL_REQUIRED. Waiting for the second on-path confirm.

## Accepted commit SHA
