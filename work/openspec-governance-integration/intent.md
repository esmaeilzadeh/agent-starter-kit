# Intent: OpenSpec as an Internal Kit Engine

Risk: HIGH

Engine: openspec

## What

Integrate a pinned OpenSpec CLI behind the existing kit command surface for the
parts where OpenSpec is stronger: change proposals, behavioral specifications
and deltas, design, tasks, structural validation, synchronization, and archive.

OpenSpec remains directly accessible for troubleshooting and advanced use, but
the kit does not promote or generate a second user-facing OpenSpec command
surface. Kit commands remain the documented default.

Run the integration first as a two- or three-change pilot. Each pilot workstream
uses one shared work ID for its `agent/<work-id>` branch, OpenSpec change, and
kit evidence records.

## Why

The current kit independently maintains specification proposals, accepted
specifications, plans, lifecycle status, and runtime projections. OpenSpec has a
more mature artifact engine for those responsibilities. Reusing it should reduce
custom machinery and improve structural validation without discarding the kit's
distinct governance, Git safety, independent review, verification, provenance,
and acceptance model.

## Non-goals

- Replacing the complete kit workflow with OpenSpec.
- Promoting `/opsx-*` commands as an alternative default workflow.
- Treating OpenSpec validation or archive as semantic review, deterministic
  verification, or human acceptance.
- Migrating every historical kit specification before the pilot.
- Designing a custom OpenSpec schema before the later evaluation workstream
  decides.
- Blocking this workstream's Accept on two or three future evaluation pilots.

## Known assumptions

- Explore skipped: destination already clear.
- OpenSpec is pinned to an explicit supported version; automated update checks
  do not silently change the project dependency or generated files.
- Initial setup creates the OpenSpec structure without generating tool-specific
  commands or skills.
- OpenSpec is the sole specification and planning source of truth for each pilot
  change; the pilot does not duplicate those artifacts under the kit's existing
  `specs/` layout.
- Existing specifications remain available as legacy history. Only
  specifications needed by a pilot change are copied into OpenSpec.
- The kit continues to own intent, worktree and commit policy, risk and
  delegation policy, independent Review and finding disposition, project
  verification, commit-linked results, and Accept.
- Kit-mediated openspec-archive occurs after kit Accept; direct CLI archive is
  detected after the fact.
- This work-id is a marked dogfood pilot. Kit `plan.md` and `specs/` copies
  become pointers after cutover.

## Open questions

- Which OpenSpec release should be pinned when implementation begins?
- Name the later evaluation workstream and its two or three representative
  changes when that workstream starts.

## Human decisions

- Use one visible kit command surface and OpenSpec as an accessible but
  unpromoted internal engine.
- Approve the proposed OpenSpec/kit responsibility split and pilot.
- Copy only specifications needed by pilot changes; do not migrate all existing
  specifications.
- Stopped after 02 Spec in the first session; resumed 03+ on 2026-09-14.
- Spec Challenge ESCALATE. Spec Change confirmed: intent marker, pointer
  duplicates, this work-id is a pilot, checkout-scoped status CLI,
  kit-mediated openspec-archive plus detection, Accept on machinery plus
  baseline with evaluation later.
