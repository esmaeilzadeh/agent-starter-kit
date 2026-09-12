# Explore Map: real skip of 00 when destination is already clear

## Destination

When the human asks a **new task**, the agent must **decide** — and say so — whether:

- **00 is required** (destination foggy → run Explore until What/Why can be owned), or
- **00 is a real skip** (destination already sharp enough for Intent → jump to `01 Grill`, do not pretend Explore ran).

“Real skip” is the thing to make precise. It is **not** the ask-status meaning of skip (skip extra *approvals*, still write later artifacts). It is a **stage omit**: Explore did not run.

## Notes

- This workstream **needs Explore**. The user invoked `/00-explore`, and the destination is foggy: kit texts already disagree (Guide/spec say skip 00 when clear; `workflow.md` + `00-explore.md` say do not skip the explore-map artifact).
- Standing: never auto-approve recommendations; expand before resolve (ADR 0007).
- Prepare: `grilling` @ v1.0.0 ok. Manifest pins `wayfinder` and `research` failed (`No matching skills` at `mattpocock/skills@v1.0.0`; upstream list has `decision-mapping` / `prototype` / `grilling`). Out of scope to re-pin unless this work later owns the manifest.
- Kit `00 Explore` ≠ Cursor’s built-in Explore subagent.

## Tracker map (optional)

Not used. This file is canonical.

## Decisions so far

Research facts (not human decisions):

- **Guide already allows omit:** `_ask/guide/02-workflow.md` — Explore is optional when the destination is already clear; “Skip Explore only when the human already has a destination sharp enough for Intent → Grill.”
- **Spec already allows omit:** `_ask/spec/01-layout-and-concepts.md` §5.1 — “Skip `00` when the human already has a destination sharp enough for Intent → Grill.” Example 31.2 is “Clear intent (skip Explore)” and goes straight to `01 Grill`. Artifact model: `explore-map.md` exists **only when Explore ran** (`_ask/spec/02-artifacts.md` §6.0, `_ask/spec/04-scripts-and-git.md` §30).
- **AGENTS.md already asks the question** (“Foggy destination? Run 00…”) but does not tell the agent to **announce a skip** and jump to 01. Demo Path A: “Skip Explore. Destination is already sharp.”
- **Contradiction from ask-status:** `_ask/policies/workflow.md` “Artifacts are not optional” / “Skip = skip extra approvals, not documents” plus `_ask/agents/00-explore.md` kit emphasis: “prepare the explore-map (do not skip the artifact).” That leaked the *pipeline* skip-meaning onto the *optional on-ramp*.
- **`./ask start-work` always seeds** `work/<id>/explore-map.md` from the template, so a skipped Explore still has a stock file. `./ask status` already ignores stock explore-map boilerplate when inferring handoff.
- **Return path exists:** if fog comes back at destination scale, return to 00 rather than forcing Spec Change to do wayfinding.

Human decisions (this grill):

- **Q2 (partial):** Who calls foggy vs clear — **B: agent proposes, human confirms** (stated). Tension with Q3 free-chat “route by agent decision” is still open.
- **Q3 (partial):** Explicit `/00-explore` or “00-explore” → **start 00 immediately**; do not ask whether Explore is really needed. Free on-path chat → route to 00 or 01 from the agent’s fog call (confirm-vs-proceed still open). `/01-grill` when foggy is still open.

Working call for **this** task (applies the gate we are designing):

| Signal | This task |
| --- | --- |
| Slash command | `/00-explore` → run 00 even if we might have skipped |
| Can we own What/Why without inventing? | No — “real skip” vs stub map vs always-write-map is open; who decides fog is open |
| R&D / wayfinding? | Yes — reconcile Guide/spec omit with workflow “don’t skip the artifact” |
| **Call** | **Need 00** (this map). Not eligible for 01 until the grill frontier below is settled. |

## Not yet specified

Human decisions still open:

1. **Meaning of real skip** — omit vs stub map vs always write a map.
2. **Free-chat confirm** — Q2-B says wait; Q3 “route by agent decision” may mean proceed. Must resolve.
3. **`/01-grill` when dest is foggy** — still run 00, or honor the command?
4. **Carve-out** — 00 optional on-ramp vs same “don’t skip documents” as 01–10.
5. **Seeded `explore-map.md`** — blocked on (1).
6. **Where the gate lives** — AGENTS + workflow + 00 vs AGENTS only vs new policy file.

## Out of scope

- Re-pinning Community Skills (`wayfinder` → `decision-mapping`, etc.) unless a later plan step owns the manifest.
- A new `./ask` subcommand to decide fog (agent judgment + written gate is enough unless Grill says otherwise).
- Changing `01`–`10` skip-approvals meaning from ask-status.
- Off-path / “just code” behavior (already session-only).
- Autoplaying `/01`–`/10` as a batch.

## Handoff to Intent

**STILL_FOGGY.** Do not enter `01 Grill` until the frontier in this map is resolved.

Owned enough to say:

- **Why this work exists:** agents must **find out** at new-task start whether 00 is required or a **real skip**, then either Explore or jump to 01. Today the kit *says* skip-when-clear in the Guide/spec and *says* don’t-skip-the-map in workflow/00 emphasis. Agents follow the louder checklist and run 00 (or skip documents) inconsistently.
- **This session’s call:** need 00 (invoked + destination not ownable yet).

Blocked on human answers to **Not yet specified** (grill round below). After those land, handoff can name What/Why: a written Explore gate, real skip = omit 00, pipeline skip-approvals unchanged.
