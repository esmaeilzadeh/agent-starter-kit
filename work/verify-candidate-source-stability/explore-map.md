# Explore Map: Verify candidate source stability

## Destination

Identify the source mutation recorded in the later card and establish whether current source still needs a fix.

## Notes

- Selected by the human: "init and fix that"; access restored with "access granted".
- Use kit Explore, diagnosing-bugs, and writing-for-agents. No additional skills that change What/Why are proposed.
- Prepared pinned skills with `./ask prepare`; required skills installed successfully. Optional frontend-design installation failed because the installer treats its SHA as a remote branch. No manifest changes.
- `./ask sync` succeeded and left tracked source unchanged.
- Shared stage intake was attempted with the selected later card; it cannot load an engineering-model.json for this unadopted new workstream. No subject association is inferred or created.

## Decisions so far

- Historical reproduction: detached checkout f76170981496d14d7d1512705e1f0d61aa8000ea; run `bash _ask/tests/test-sync-runtime-agents.sh` with ASK_ROOT pointing to that checkout. The check exits 0 but leaves tracked `.codex/agents/kit-05-plan.toml`, `kit-06-implement.toml`, `kit-07-review.toml`, and `kit-08-refactor.toml` modified.
- Cause: the test regenerates runtime agent projections in its own source checkout without restoring their original bytes.
- Current source already includes fixes 5f84bb9 and 7156135: snapshot all four runtime agent directories and restore them through an EXIT trap.
- The same check on current source exits 0 and leaves tracked source unchanged. Forced failure via ASK_SYNC_TEST_FORCE_FAILURE=1 exits 97 and also leaves source unchanged.
- Existing regression `EntrypointTests.test_I09_runtime_agent_sync_preserves_candidate_tree` covers exact snapshots and clean Git status on success and failure, plus related fixture checks.

## Not yet specified

- No unresolved technical questions: full CheckPlan passed all 37 checks at 8c5d8d019bdef67587a052fe9df7eeb9508df2ca in a detached candidate checkout, and Git status including untracked files remained clean. This is investigation evidence, not final workstream completion evidence.

## Out of scope

- Weakening the candidate source-stability guard, changing model routing, repairing skill installation, or introducing Engineering Model adoption solely to unblock intake.

## Handoff to Intent

The historical cause is reproduced and existing current fixes address the direct trigger. Own the remaining work as validation and inbox reconciliation: verify all static checks preserve committed source, run existing cleanup regressions, retain evidence and historical fix provenance, and resolve the parked card only when the evidence supports it. If another source mutation appears, fix its cause within this scope. Human confirmation of the complete intent remains required before implementation or inbox edits.
