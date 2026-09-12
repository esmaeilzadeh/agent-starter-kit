# Plan

## Specification

Kit addition: `./ask status` as computed inventory. No separate spec file — contract is `_ask/spec/04-scripts-and-git.md` §23.4.

## Approach

1. `status.sh` inspects `agent/*` refs and default-branch `work/*`.
2. Infer furthest filled artifact; `--work-id` / `--json`.
3. Wire dispatcher, tests, README / worktree policy.

## Work breakdown

- Script + isolated git test
- Docs + `./ask` help

## Risks

False “seeded” vs filled if templates gain default body text.

## Verification approach

`_ask/tests/test-status.sh` plus `./ask verify`.

## Out of scope for this plan

Remote-only branches. Committed INDEX.
