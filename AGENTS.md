# Agent instructions

This repository uses the AI Engineering Starter Kit (Cursor-first).

Protocol lives under `part-engineering/` (Guide, Build Spec, stage contracts, policies, skills manifest, templates). Do not treat Cursor config as the source of truth.

If the destination is foggy: run **00 Explore** (kit stage — not Cursor’s built-in Explore subagent) until `work/<work-id>/explore-map.md` has a non-empty `Handoff to Intent`.

Before Engineering Pipeline work:

- clean working tree
- dedicated branch
- identify `work-id` and accepted specification
- read relevant policies under `part-engineering/policies/` (`delegation.md`, `risk.md`, `verification.md`)
- prepare pinned Community Skills via `part-engineering/skills/prepare-skills.sh` (do not vendor skill trees)

During work: stay in assigned scope; do not silently change What/Why or acceptance criteria; escalate per policy; preserve workstream isolation; commit meaningful states.

Before claiming completion: run configured verification; record the exact commit SHA; leave required structured artifacts.
