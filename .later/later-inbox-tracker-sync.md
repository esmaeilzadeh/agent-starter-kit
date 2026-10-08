# Later inbox syncs to the issue tracker when one is configured

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `inner-loop-hardening` (2026-09-20)
- **Start later:** new session, `./ask start-work later-inbox-tracker-sync`
- **First stage:** 01 Grill (dest is ownable: create/update tracker issue from a later card iff tracker is set up). Skip 00 unless the tracker surface (GitHub vs GitLab vs none) is still unnamed.

## Why

Kit spec §30.1: no issue-tracker sync. Inner-loop-hardening CURRENT spec already requires commit of `.later/<slug>.md` on `develop` plus create/update a tracker issue, but there is no script and no fail-closed/skip-when-unset rule. Existing cards (`explore-clone-fanout`, `openspec-pilot-evaluation`) have hand-written Tracker URLs. A machine without `gh`/`glab` must still be able to park locally.

## Proposed What (unapproved)

- If a tracker is configured (Grill: `gh` on GitHub remote, or equivalent), `./ask later add` (or `./ask later sync <slug>`) creates or updates one issue and writes `Tracker:` on the card.
- If no tracker is set up: skip sync, print that skip, exit 0 for the local park. Do not fail the add.
- Idempotent: second add/sync updates the same issue; does not open a duplicate.
- This workstream implements the sync. Commit-on-`develop` stays inner-loop-hardening git-flow unless Grill moves it here.

## Note

Local inbox card (gitignored). Pair with `.later/later-inbox-script.md`. Do not start this as a second `agent/*` while `later-inbox-script` is live unless the human sequences them as one job.
