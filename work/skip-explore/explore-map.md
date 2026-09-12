# Explore Map: real skip of 00 when destination is already clear

## Destination

When the human asks a **new task**, the agent must **find out** whether:

- **00 is required** (destination foggy → run Explore until What/Why can be owned), or
- **00 is a real skip** (destination already sharp enough for Intent → jump to `01 Grill`, do not pretend Explore ran).

“Real skip” is a **stage omit**: Explore did not run. It is not the ask-status meaning of skip (skip extra *approvals*, still write later artifacts).

## Notes

- This workstream needed Explore (`/00-explore` + dest not ownable).
- Standing: never auto-approve recommendations; expand before resolve (ADR 0007).
- Kit `00 Explore` ≠ Cursor’s built-in Explore subagent.
- Mid-session discoveries (skill pin, later-inbox) are **other jobs**. Parked under local `.later/`; not this workstream. Human later said finish those jobs in this session **after** this work, each on its own `agent/<id>`.
- One session normally = one job. This chat is an explicit exception for the parked jobs, run **sequentially**, not on this branch.

## Tracker map (optional)

Not used. This file is canonical.

## Decisions so far

Research facts:

- Guide/spec already allow omitting 00 when Intent is ownable. `explore-map.md` exists **only when Explore ran**.
- ask-status leaked “don’t skip documents” onto 00 (`workflow.md`, `00-explore.md` kit emphasis).
- `start-work` seeds a stock `explore-map.md`. Status ignores stock boilerplate for handoff.
- Return to 00 if fog invalidates the destination.

Human decisions (grill + “continue till end” owns remaining recs):

- **Q2 = B:** Free on-path chat: agent proposes foggy vs clear; human confirms before 00 or 01 starts.
- **Q3 slash:** Explicit `/00-explore` or “00-explore” → start 00 immediately; do not ask whether Explore is really needed.
- **Q7 = A:** Free chat = announce and **wait** (fits Q2-B). Only `/00-explore` skips the confirm.
- **Q8 = A:** `/01-grill` does **not** skip a foggy dest. Fog wins; run 00 or stop.
- **Q1 = A:** Real skip = omit 00. No explore-map labor. Record in `intent.md`: “Explore skipped: destination already clear.”
- **Q4 = A:** `01`–`10` still “skip extra approvals, not documents.” 00 is the optional on-ramp exception.
- **Q5 = A:** `start-work` stops seeding `explore-map.md`. 00 creates the file when Explore runs.
- **Q6 = A:** Gate lives in `AGENTS.md` item 1 + `workflow.md` + `_ask/agents/00-explore.md`. No new policy file.

## Not yet specified

None for this destination. Pin bump and later-inbox are other work-ids.

## Out of scope

- Pinning Community Skills (parked: `.later/pin-mattpocock-skills-v1.2.3.md`).
- Later-inbox as kit product (parked: `.later/later-inbox-mechanism.md`).
- A new `./ask fog` command.
- Changing `01`–`10` skip-approvals meaning.
- Off-path / “just code” (already session-only).
- Autoplays `/01`–`/10` as a batch.
- Two live `agent/*` branches in parallel for these jobs.

## Handoff to Intent

**DESTINATION_CLEAR.**

**What:** A written Explore gate. At new-task start (on-path): if the human invoked `/00-explore`, run 00 with no second-guess. Otherwise the agent announces foggy vs clear and waits for confirm, then either runs 00 (creates `explore-map.md`) or real-skips to 01 (no map; `intent.md` notes the skip). `/01-grill` does not override fog.

**Why:** Agents must find out whether 00 is needed. Guide/spec already allow omit; workflow/00 text forbade skipping the map. That contradiction made Explore ceremony or silent skips.

**Pointers:** Human decisions above. Implement by aligning AGENTS.md, workflow.md, 00-explore.md, and `start-work` seeding — not a new policy file.
