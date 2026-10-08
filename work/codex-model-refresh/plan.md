# Plan

## Specification

`specs/current/codex-model-refresh.md`; criterion contract `specs/current/codex-model-refresh.json`.

## Approach

Update only the Codex runtime role/pool/picker table. Keep the portable stage-to-role map unchanged. Adjust the existing sync test's Codex expectation and run `./ask sync` to regenerate agents.

## Work breakdown

1. Record current official guidance and the local catalog, prepare and independently challenge the exact review-only contract, then pin it.
2. Change Codex runtime pins and the existing shell assertion; sync projections and commit.
3. Independently review the committed candidate, execute the existing sync check and full `./ask verify`, and record evidence. Prepare Accept without fabricating the human's acceptance.

## Risks

Same GPT-family review provides context independence, not cross-family diversity. Codex may cache agent configurations for an active session; future spawns must use verified explicit current model overrides if cached roles still reference retired models. Model availability varies by account; today's local catalog verifies the three selected picker entries.

## Verification approach

Existing `_ask/tests/test-sync-runtime-agents.sh` exercises actual generation, risk selection and overrides. Full mandatory CheckPlan via `./ask verify`. No new mirror tests for model-name strings.

## Out of scope for this plan

Engineering Model/UI implementation, global Codex settings, benchmarking, reasoning-effort changes, other runtime model changes, pushes and merges.

## E2E

Run the existing shell sync journey, which executes public scripts and restores default output. The structured completion contract uses independently approved review-only criteria for this nonbehavioral configuration change; existing repository checks still execute.

