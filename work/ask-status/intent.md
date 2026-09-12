# Intent: workstream status and kit-path guidance

## What

1. `./ask status` — live/archived workstreams from git refs (no checkout, no INDEX).
2. Kit path is **guidance, not a lock**, with this meaning of skip:
   - **On the path:** every next stage still gets its artifact. You do not skip documents.
   - **Skip** = skip extra *approvals*. After one “I approve these defaults are OK,” the agent prepares spec (CURRENT), plan, review, etc., without re-blessing each file. **Accept** is the second confirm.
   - **Off the path** (“skip the kit” / “just code”) is leaving the workflow: warn once and follow. If they stay on the path but artifacts are missing, **prepare** them from those defaults and confirm once — do not jump to code.

## Why

`work/` is branch-local, so status must be computed from refs. The kit should guide engineering steps instead of vibe coding, without trapping the human in per-stage ceremony.

## Non-goals

`work/INDEX.md`. External trackers. Checking out branches to build a board. Locking Implement. Autoplays `/01`–`/10` as a batch job. Auto-deleting `agent/*`.

## Known assumptions

Human said “all recs” on the guidance grill (two confirms; prepare-if-missing on-path; fold into this work-id).

## Open questions

None from the closed grill frontier.

## Human decisions

- Live = unmerged `agent/*`. Archive = `work/*` on default with no unmerged `agent/*`.
- Two confirms on-path: (1) defaults OK after Grill/Spec recs, (2) Accept.
- On-path + missing artifacts → prepare from defaults, confirm once, then continue.
- Off-path only when the human explicitly leaves the kit; then warn once and follow.
- `check-workstream` stays exit 1 when the default path is incomplete; wording is guidance, not a padlock.
- No `./ask next` in this work.
