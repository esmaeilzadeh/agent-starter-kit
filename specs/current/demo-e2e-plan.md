# Specification: end-to-end demo plan document

## Status

CURRENT

## Goal

A facilitator-ready demo walks Path A (clear intent) and optional Path B (Explore) using a tiny `kit-status` vehicle. The demo is documentation only.

## Non-goals

Implementing `demo-kit-status` / `scripts/kit-status.sh` in this workstream. Phase 3 / CI.

## Behavior

- Demo lives at `_ask/docs/demo/end-to-end-plan.md` (moved with kit-author docs).
- Root `README.md` and `AGENTS.md` link to it.
- Path B must not claim `start-work` seeds `explore-map.md`.

## Acceptance criteria

- Demo file exists and covers Path A, Path B, interrupts, checklist.
- `AGENTS.md` / README point at it.
- Path B tells the agent to create the explore-map from the template.
- `./ask verify` passes.

## Source intent

`work/demo-e2e-plan/intent.md`
