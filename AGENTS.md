# Agent instructions

This repository uses the AI Engineering Starter Kit (Cursor-first).

Protocol SoT for stages, bindings, and verification is `.agents/ask/`. `_ask/` holds Guide, Build Spec, policies, skills manifest, and templates. `_ask/agents` and `_ask/bindings` are pointers. Do not treat Cursor config as the source of truth.
When an inner-loop TaskGraph is active, follow `.agents/ask/task-loop.md` for per-task Red → Green → Refactor, independent Review, correction, and integration evidence.

## Checklist

0. **Session/resume write preflight:** at the start of every project session and before resuming work, run `./ask access-check`. If it fails, report the blocked location and stop project work until access is restored. This applies across Codex, Cursor, and OpenCode.

1. **Continuation before new-task intake:** For “continue,” “resume,” or equivalent, inspect the current branch, workstream artifacts, inner-loop state, and recent commits. Resolve an explicitly named workstream first; if it is ambiguous or unavailable, ask about it and do not substitute the checkout. Without an explicit target, prefer a matching checked-out `agent/<work-id>` workstream over unrelated live workstreams. Resume its exact authorized stage and task. If it is terminal or its plan explicitly stops, report that endpoint without a chooser and do not infer later-stage authorization. Use remaining evidence for other checkouts; ask only when no target is identifiable, multiple targets remain plausible, or stage/authorization evidence conflicts. **Explore gate (new task):** apply only after establishing that the request starts a genuinely new task. Decide foggy vs clear and **say so**. `/00-explore` (or explicit “00-explore”) → start kit **00 Explore** immediately (not Cursor’s built-in Explore subagent); do not ask whether Explore is needed. Free chat → offer **Start Explore** / **Start Grill** choice buttons and wait for a submitted choice. `/01-grill` does not skip 00 when the destination is foggy. **Real skip** (destination already ownable): omit 00; do not write `explore-map.md`; put `Explore skipped: destination already clear.` in `intent.md`. If 00 runs: create `work/<work-id>/explore-map.md` if missing; Handoff must be non-empty before 01.
2. **Prepare skills:** `./ask prepare` (never vendor skill trees; never `revision: latest`). Before Grill/Explore decision questions: offer extra related skills that would change What/Why as selectable choices, prepare only selected ones, and pin them in `_ask/skills/manifest.yaml` for later work in this repo.
3. **Sync Cursor binding:** `./ask sync` so `.cursor/skills` and `.cursor/commands` match `.agents/ask/` (+ `.agents/ask.local/` overlays).
4. **Clean worktree (hard gate):** never start labor on a dirty tree. Run `./ask check-clean`. If dirty, offer selectable choices for each uncommitted/untracked path (commit / stash / discard / move) — do not stash or reset silently. See `_ask/policies/worktree.md`.
5. **One plan → one branch:** `./ask start-work <work-id>` from `develop` (`agent/<work-id>`). Git-flow: `_ask/policies/git-flow.md`. Do not run multiple related branches that touch common files in parallel. List live/archived workstreams with `./ask status` (workstreams from refs, not the checkout; committed later cards from `develop` or `origin/develop`).
   **Mid-work discovery:** park it in `.later/<slug>.md` (from `_ask/templates/later-work.md`). That is not live. Do not start a second `agent/*` in this session unless the human explicitly sequences another job.
6. **Default path (guidance, not a lock):** every session starts on-path — **prepare each artifact**. Request every required confirmation as a question with selectable choices; never ask for an approval sentence. Present the complete intent and assumptions as **Approve** / **Request changes** choices and record the submitted approval with `./ask confirm-intent`. `./ask check-workstream` hard-refuses implementation if confirmation is missing or stale. After intent approval, prepare remaining artifacts without re-confirming until **Accept**, presented as **Accept workstream** / **Request changes** choices. `/off-path` is **this chat only** (do not persist). See `_ask/policies/workflow.md`. Read `_ask/policies/` (`delegation.md`, `risk.md`, `verification.md`, `worktree.md`, `workflow.md`, `git-flow.md`).
7. **During work:** stay in scope; do not silently change What/Why or acceptance criteria; escalate per policy; **commit after each meaningful step on `agent/<work-id>` without waiting for the human to ask** (the work branch is the safety boundary — see `_ask/policies/worktree.md`). Do not defer commits until plan end.
8. **Before claiming completion:** `./ask verify`; `./ask record-result --work-id … --commit-sha … --result …`; leave required artifacts.

`ask` is the Agent Starter Kit dispatcher. Implementation stays under `_ask/scripts/`. **Do not run `./ask setup`** — that wizard is human-only (needs a TTY).

## Asking the user to decide

- Prefer the native `request_user_input` tool with explicit selectable options whenever it is available. Keep an optional text field available in the same response so the user can add nuance with any selection. If the tool is unavailable, present numbered options and invite an added-text response alongside the selected number or label.
- Ask one question per decision. For architecture and design decisions, offer 2–4 meaningful choices, mark the recommended choice, and briefly explain each choice’s trade-offs.
- **During Grill, apply this to every grilling question:** provide selectable options and accept accompanying free text even when an option already fits. Do not ask grilling questions as plain text or require the user to choose “Other” before adding nuance.

## Progress feedback

During active work, send a concise progress update at least every 60 seconds and after meaningful results or changes of direction. Name the specific task, the actual operation or check underway, the latest result, and the next step. A generic “Working” indicator is insufficient feedback. If work is blocked or awaiting input, report the blocker promptly.

## Demo

End-to-end facilitator script (clear intent + optional Explore): [`_ask/docs/demo/end-to-end-plan.md`](_ask/docs/demo/end-to-end-plan.md).

Human-oriented overview and doc index: root [`README.md`](README.md).
