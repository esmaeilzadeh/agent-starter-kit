# Plan

## Specification

`specs/current/demo-e2e-plan.md`

## Approach

The demo already shipped (later moved to `_ask/docs/demo/`). Close artifacts. Fix the one stale Path B line that still said `start-work` seeds `explore-map.md`.

## Work breakdown

1. ~~Write the facilitator demo and link it from AGENTS/README~~ — done on `main`.
2. Fix Path B: create explore-map from the template; `start-work` does not seed it.
3. Verify + Accept.

## Risks

Demo vehicle (`demo-kit-status`) can be confused with this work-id (`demo-e2e-plan`). The demo file already calls that out.

## Verification approach

- File exists at `_ask/docs/demo/end-to-end-plan.md`
- Path B does not say the map is pre-seeded
- `./ask verify`

## Out of scope for this plan

Implementing `scripts/kit-status.sh`.
