# Plan

## Specification

`specs/current/codex-model-refresh.md`; criterion contract `specs/current/codex-model-refresh.json`.

## Approach

Update the Codex runtime role/pool/picker table and document existing per-workstream complexity overrides. Keep the portable stage-to-role map unchanged. Adjust the existing sync test's Codex expectation and run `./ask sync` to regenerate agents.

## Work breakdown

1. Record current official guidance and the local catalog, prepare and independently challenge the exact review-only contract, then pin it.
2. Change Codex runtime pins and the existing shell assertion; sync projections and commit.
3. Independently review the committed candidate, execute the existing sync check and full `./ask verify`, and record evidence. Prepare Accept without fabricating the human's acceptance.

## Risks

Same GPT-family review provides context independence, not cross-family diversity. Codex may cache agent configurations for an active session; future spawns must use verified explicit current model overrides if cached roles still reference retired models. Model availability varies by account; today's local catalog verifies the three selected picker entries.

## Verification approach

Existing `_ask/tests/test-sync-runtime-agents.sh` exercises actual generation, risk selection and overrides. Full mandatory CheckPlan via `./ask verify`. No new mirror tests for model-name strings.

## Out of scope for this plan

Engineering Model/UI implementation (resumed after this prerequisite), global Codex settings, benchmarking, other runtime model changes, pushes and merges to main/develop.

## Authorized effort extension (revision 3)

The human authorized the task-fit effort proposal on 2026-10-08. Independently challenge and pin the amended CM-004 contract. Commit five public-generator cases before production changes and record actual assertion red. Add optional effort resolution to Codex generation only, validating all assignments before output writes. Configure known-model defaults plus Verify low; document effort overlays and complex Sol/high promotion. Regenerate, commit, independently review, run full Verify, and archive exact-revision evidence. Then return to the existing main workstream branch.

Tests cover the end-to-end default generation journey, risk escalation, complete override precedence, inheritance/unknown-model compatibility, and invalid-input non-mutation. All invoke the generator against isolated consumer directories; no test changes global Codex settings.

## E2E

Run the existing shell sync journey, which executes public scripts and restores default output. The structured completion contract uses independently approved review-only criteria for this nonbehavioral configuration change; existing repository checks still execute.
