# Plan

## Specification

`specs/current/skip-explore.md` — Explore gate: real skip vs required 00.

## Approach

Align the three texts agents actually read (AGENTS, workflow policy, 00 contract) and stop `start-work` from seeding a stock map. Add a small start-work test. Sync Cursor projections.

## Work breakdown

1. **Handoff + intent + spec** — this commit set.
2. **Texts** — `AGENTS.md` item 1; `workflow.md` carve-out; `00-explore.md` kit emphasis; guide one paragraph; ADR 0014; workflow-guidance rule.
3. **start-work** — drop `explore-map.md` seed. 00 contract: create from template if missing when Explore runs.
4. **Tests** — `test-start-work-no-explore-map.sh`; fix smoke test to create the map as 00 would.
5. **Sync** — `./ask sync`.
6. **Verify** — `./ask verify`; `record-result`.

## Risks

- Smoke test assumed a seeded map — update it to simulate 00 creating the file.
- Humans expect a map on every work-id — status already ignores stock; docs must say omit is intentional.

## Verification approach

- New test: start-work on a clean temp repo does not create `explore-map.md`.
- Existing smoke: after start-work, copy template then fill handoff.
- `./ask verify`.

## Out of scope for this plan

- Skill pins. Later-inbox product. `./ask fog`. Merging to `main` (needs explicit ask).
