# Agent instructions

This repository uses the AI Engineering Starter Kit (Cursor-first).

Protocol lives under `_ask/` (Guide, Build Spec, stage contracts, policies, skills manifest, templates). Do not treat Cursor config as the source of truth.

## Checklist

1. **Explore gate (on-path new task):** Decide foggy vs clear and **say so**. `/00-explore` (or explicit “00-explore”) → start kit **00 Explore** immediately (not Cursor’s built-in Explore subagent); do not ask whether Explore is needed. Free chat → announce 00 vs 01 and **wait for confirm**. `/01-grill` does not skip 00 when the dest is foggy. **Real skip** (dest already ownable): omit 00; do not write `explore-map.md`; put `Explore skipped: destination already clear.` in `intent.md`. If 00 runs: create `work/<work-id>/explore-map.md` if missing; Handoff must be non-empty before 01.
2. **Prepare skills:** `./ask prepare` (never vendor skill trees; never `revision: latest`). Before Grill/Explore decision questions: propose extra related skills that would change What/Why, **ask before preparing them**, and pin accepted ones in `_ask/skills/manifest.yaml` for later work in this repo.
3. **Sync Cursor binding:** `./ask sync` so `.cursor/skills` and `.cursor/commands` match protocol (+ `agents/*.local.md` overlays).
4. **Clean worktree (hard gate):** never start labor on a dirty tree. Run `./ask check-clean`. If dirty, **grill the human** on each uncommitted/untracked path (commit / stash / discard / move) — do not stash or reset silently. See `_ask/policies/worktree.md`.
5. **One plan → one branch:** `./ask start-work <work-id>` (`agent/<work-id>`). Do not run multiple related branches that touch common files in parallel. List live/archived workstreams with `./ask status` (workstreams from refs, not the checkout; later cards from `.later/` on this checkout).
   **Mid-work discovery:** park it in `.later/<slug>.md` (from `_ask/templates/later-work.md`). That is not live. Do not start a second `agent/*` in this session unless the human explicitly sequences another job.
6. **Default path (guidance, not a lock):** every session starts on-path — **prepare each artifact**. After one “defaults OK,” do not re-bless Plan/Review until **Accept**. `/off-path` is **this chat only** (do not persist). See `_ask/policies/workflow.md`. Read `_ask/policies/` (`delegation.md`, `risk.md`, `verification.md`, `worktree.md`, `workflow.md`).
7. **During work:** stay in scope; do not silently change What/Why or acceptance criteria; escalate per policy; **commit after each meaningful step on `agent/<work-id>` without waiting for the human to ask** (the work branch is the safety boundary — see `_ask/policies/worktree.md`). Do not defer commits until plan end.
8. **Before claiming completion:** `./ask verify`; `./ask record-result --work-id … --commit-sha … --result …`; leave required artifacts.

`ask` is the Agent Starter Kit dispatcher. Implementation stays under `_ask/scripts/`. **Do not run `./ask setup`** — that wizard is human-only (needs a TTY).

## Demo

End-to-end facilitator script (clear intent + optional Explore): [`_ask/docs/demo/end-to-end-plan.md`](_ask/docs/demo/end-to-end-plan.md).

Human-oriented overview and doc index: root [`README.md`](README.md).
