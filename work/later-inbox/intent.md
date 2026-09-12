# Intent: later-inbox for mid-work discoveries

## What

A gitignored inbox (`.later/`) so a running workstream can **park** a new issue/story without creating a live `agent/*` or mixing it into the current job. A later session starts it with `./ask start-work`. `./ask status` does not list parked cards.

Explore skipped: destination already clear.

## Why

Discoveries mid-session (e.g. a skill-pin bump) must not become a second live work or silent product on the active branch. No issue tracker is required.

## Non-goals

- `./ask later` CLI.
- Listing `.later/` in `./ask status`.
- Tracker integration (optional later).
- Changing one-plan-one-branch.

## Known assumptions

- README in `.later/` is kit-owned; cards are local (gitignored).
- Found during skip-explore; implemented on its own work-id.

## Open questions

None.

## Human decisions

- Not a live workstream until `start-work`.
- Gitignored folder in the repo when there is no tracker.
