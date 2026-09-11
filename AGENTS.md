# Agent instructions

This repository uses the AI Engineering Starter Kit (Cursor-first).

Protocol lives under `part-engineering/` (Guide, Build Spec, stage contracts, policies, skills manifest, templates). Do not treat Cursor config as the source of truth.

## Checklist

1. **Foggy destination?** Run kit **00 Explore** (not Cursor’s built-in Explore subagent) until `work/<work-id>/explore-map.md` has a non-empty `Handoff to Intent`.
2. **Prepare skills:** `part-engineering/skills/prepare-skills.sh` for pinned Community Skills (never vendor skill trees; never `revision: latest`).
3. **Sync Cursor binding:** `scripts/sync-cursor-binding.sh` so `.cursor/skills` and `.cursor/commands` match protocol (+ `agents/*.local.md` overlays).
4. **Before pipeline work:** clean tree (`scripts/check-clean-worktree.sh`), dedicated branch (`scripts/start-work.sh <work-id>`), accepted spec, plan, read `part-engineering/policies/` (`delegation.md`, `risk.md`, `verification.md`).
5. **During work:** stay in scope; do not silently change What/Why or acceptance criteria; escalate per policy; commit meaningful states.
6. **Before claiming completion:** `scripts/verify.sh`; `scripts/record-result.sh --work-id … --commit-sha … --result …`; leave required artifacts.
