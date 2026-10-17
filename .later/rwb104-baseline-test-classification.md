# Correct baseline coverage classification for RWB-104 historical source test

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `revising-workbench`
- **Start later:** new session, `./ask start-work <new-work-id>`
- **First stage:** 00 Explore if dest is foggy; else 01 Grill

## Why

RWB-104's accepted test plan maps `RWB-HISTORICAL` to the newly added
`ProjectionTests.test_live_archive_foreign_and_historical_revisions_are_read_only`
and marks it `change_kind: new`. The test passes on every recorded red candidate,
including the initial RWB-104 red, because it exercises `workbench_sources`
behavior already present in the accepted base. Existing
`_ask/tests/test_engineering_workbench_sources.py::WorkbenchTests.test_cross_branch_snapshot_is_consistent_and_read_only`
already checks a committed historical snapshot and verifies unchanged HEAD,
refs, source bytes, and `editable=False`.

The TDD completion gate therefore refuses RWB-104 with missing behavior-red
records for EM-009, EM-017, and EM-018. The task has genuine red evidence for its
new projection behavior, but no genuine red can be produced for the unchanged
historical source helper without introducing a fabricated failure or changing
accepted scope. EM-017 also has assigned migration/pilot coverage in RWB-108.

## Proposed What (unapproved)

Correct the accepted task-scoped test mapping through the repository's reviewed
contract-amendment flow: bind RWB-HISTORICAL to the existing unchanged
cross-branch snapshot test as baseline regression evidence, and leave EM-017
coverage with RWB-108's migration/pilot tests. Rebind RWB-104 to the amended
accepted test contract, rerun its exact candidate green suite and formal review,
then run the required inner-loop verification and integration gates. Preserve
all existing failed attempts and review history.

## Note

Observed 2026-10-17 while integrating RWB-104 candidate
`e7ed1101b6bd1ef8016cf5a6470e4392420d4e6a` on `agent/revising-workbench`.
All five assigned candidate final-green cases pass. The independent semantic
review and formal traceability review are approved. Full static verification
passes, but the inner-loop gate refuses integration only because the new
historical helper test has no behavior-red evidence. No accepted plan, task graph,
source, or authority pin was changed while investigating this discovery.
