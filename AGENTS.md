# Agent instructions

This repository uses the AI Engineering Starter Kit (Cursor-first).

Protocol lives under `_ask/` (Guide, Build Spec, stage contracts, policies, skills manifest, templates). Do not treat Cursor config as the source of truth.

## Checklist

1. **Foggy destination?** Run kit **00 Explore** (not Cursor’s built-in Explore subagent) until `work/<work-id>/explore-map.md` has a non-empty `Handoff to Intent`.
2. **Prepare skills:** `./ask prepare` (never vendor skill trees; never `revision: latest`).
3. **Sync Cursor binding:** `./ask sync` so `.cursor/skills` and `.cursor/commands` match protocol (+ `agents/*.local.md` overlays).
4. **Clean worktree (hard gate):** never start labor on a dirty tree. Run `./ask check-clean`. If dirty, **grill the human** on each uncommitted/untracked path (commit / stash / discard / move) — do not stash or reset silently. See `_ask/policies/worktree.md`.
5. **One plan → one branch:** `./ask start-work <work-id>` (`agent/<work-id>`). Do not run multiple related branches that touch common files in parallel.
6. **Before pipeline work:** accepted spec, plan, read `_ask/policies/` (`delegation.md`, `risk.md`, `verification.md`, `worktree.md`).
7. **During work:** stay in scope; do not silently change What/Why or acceptance criteria; escalate per policy; **commit after each meaningful step on `agent/<work-id>` without waiting for the human to ask** (the work branch is the safety boundary — see `_ask/policies/worktree.md`). Do not defer commits until plan end.
8. **Before claiming completion:** `./ask verify`; `./ask record-result --work-id … --commit-sha … --result …`; leave required artifacts.

`ask` is the Agent Starter Kit dispatcher. Implementation stays under `_ask/scripts/`.

## Demo

End-to-end facilitator script (clear intent + optional Explore): [`_ask/docs/demo/end-to-end-plan.md`](_ask/docs/demo/end-to-end-plan.md).

Human-oriented overview and doc index: root [`README.md`](README.md).
