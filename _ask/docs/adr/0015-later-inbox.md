# Mid-work discoveries go to `.later/`, then `develop`

When a new job appears during a running workstream, write a parked card under `.later/` and commit it on `develop` with a tracker issue link. Do not create `agent/<new-id>` in that session unless the human explicitly sequences another job. `./ask status` lists committed cards from `develop` (or `origin/develop` when no local `develop` exists), regardless of the checked-out work branch; they are not live workstreams. Template: `_ask/templates/later-work.md`. Git-flow: `_ask/policies/git-flow.md`.
