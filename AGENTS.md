# Agent instructions

This repository uses the AI Engineering Starter Kit (Cursor-first).

Protocol lives under `part-engineering/` (Guide, Build Spec, stage contracts, policies, skills manifest, templates). Do not treat Cursor config as the source of truth.

## Checklist

1. **Foggy destination?** Run kit **00 Explore** (not Cursor’s built-in Explore subagent) until `work/<work-id>/explore-map.md` has a non-empty `Handoff to Intent`.
2. **Prepare skills:** `./pek prepare` (never vendor skill trees; never `revision: latest`).
3. **Sync Cursor binding:** `./pek sync` so `.cursor/skills` and `.cursor/commands` match protocol (+ `agents/*.local.md` overlays).
4. **Clean worktree (hard gate):** never start labor on a dirty tree. Run `./pek check-clean`. If dirty, **grill the human** on each uncommitted/untracked path (commit / stash / discard / move) — do not stash or reset silently. See `part-engineering/policies/worktree.md`.
5. **One plan → one branch:** `./pek start-work <work-id>` (`agent/<work-id>`). Do not run multiple related branches that touch common files in parallel.
6. **Before pipeline work:** accepted spec, plan, read `part-engineering/policies/` (`delegation.md`, `risk.md`, `verification.md`, `worktree.md`).
7. **During work:** stay in scope; do not silently change What/Why or acceptance criteria; escalate per policy; **commit after each meaningful step** (do not wait until the plan finishes).
8. **Before claiming completion:** `./pek verify`; `./pek record-result --work-id … --commit-sha … --result …`; leave required artifacts.

`pek` is the Part Engineering Kit dispatcher. Implementation stays under `part-engineering/scripts/`.

## Demo

End-to-end facilitator script (clear intent + optional Explore): [`part-engineering/docs/demo/end-to-end-plan.md`](part-engineering/docs/demo/end-to-end-plan.md).

Human-oriented overview and doc index: root [`README.md`](README.md).
