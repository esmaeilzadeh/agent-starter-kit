# Plan

## Specification

This workstream delivers documentation only: `docs/demo/end-to-end-plan.md` (no product spec under `specs/current/` required).

## Approach

Author a single facilitator guide covering prerequisites, Path A (Grill→Accept), Path B (Explore on-ramp), interrupts, checklist, and optional install-kit encore.

## Work breakdown

1. Write `docs/demo/end-to-end-plan.md`
2. Record intent for this docs workstream
3. Point `AGENTS.md` or `part-engineering/README.md` at the demo (light link)
4. Verify clean tree / no broken links to kit paths

## Risks

Demo feature name (`demo-kit-status`) might be confused with this docs work-id (`demo-e2e-plan`) — call out explicitly in the doc.

## Verification approach

- Paths referenced in the demo exist in-repo
- `scripts/check-clean-worktree.sh` still passes after commits

## Out of scope for this plan

Implementing `scripts/kit-status.sh` (separate workstream when someone runs the demo for real).
