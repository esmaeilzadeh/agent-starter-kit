## Why

The kit independently maintains specification proposals, accepted
specifications, plans, lifecycle status, and runtime projections. OpenSpec
has a more mature artifact engine for those responsibilities. This change
wires a pinned OpenSpec CLI behind the existing kit command surface for
marked pilots, without replacing kit governance, Git safety, Review,
verification, provenance, or Accept.

## What Changes

- Pin `@fission-ai/openspec@1.13.0` and invoke it through kit gates only.
- Treat `Engine: openspec` in `work/<id>/intent.md` as the pilot marker.
- Own specification and planning for a marked pilot under
  `openspec/changes/<work-id>/`. Kit `plan.md` and optional `specs/` files
  for that id become non-normative pointers.
- `check-workstream`, `status`, and `verify` gain marked-pilot behavior.
  Non-pilots keep today's behavior.
- Add kit-mediated `./ask openspec-archive` after Accept, and detect
  out-of-order direct archive.

## Capabilities

### New Capabilities
- `kit-openspec-engine`: pinned OpenSpec as the spec/plan engine for marked
  kit pilots; kit remains the promoted command surface and owns governance.

### Modified Capabilities

## Impact

`_ask/scripts/check-workstream.sh`, `status.sh`, `verify.sh`, `ask`,
`ask-complete.sh`, `_ask/OWNED-PATHS.md`, new ADR-0018, `_ask/openspec-pin.yaml`,
`_ask/scripts/openspec_cli.py`, `_ask/scripts/openspec-archive.sh`, tests.

## Legacy source

Copied from `specs/current/openspec-governance-integration.md` (kit CURRENT
before this cutover). Destination:
`openspec/changes/openspec-governance-integration/specs/kit-openspec-engine/spec.md`.
No other `specs/current/` documents are migrated.
