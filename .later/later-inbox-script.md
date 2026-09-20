# Later inbox add/list via `./ask` script (not an agent write)

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `inner-loop-hardening` (2026-09-20)
- **Start later:** new session, `./ask start-work later-inbox-script`
- **First stage:** 01 Grill (dest is ownable: dispatcher subcommand that copies the template). Skip 00 unless Grill opens tracker-sync as the same work-id (see `.later/later-inbox-tracker-sync.md`).

## Why

Parking a later card is copy `_ask/templates/later-work.md` → `.later/<slug>.md` and fill slug/title/Why/What. Agents currently read several cards and rewrite the file each time. Kit spec §30.1 still says there is no later-inbox subcommand. `./ask status --later-only` already lists cards; add is missing.

## Proposed What (unapproved)

- `./ask later add <slug> --title "…" --why "…" [--what "…"] [--found-during <work-id>]` writes the card from the template. Refuse overwrite unless `--force`.
- `./ask later list` can stay an alias of `status --later-only` if Grill wants one surface.
- Agent contract: call the script; do not author `.later/*.md` by hand when the script exists.
- v1 stays local (gitignored cards) unless Grill sequences tracker-sync in the same workstream.

## Note

Local inbox card (gitignored). Pair with `.later/later-inbox-tracker-sync.md`. Sequence script first if they stay split.
