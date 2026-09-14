# Mid-work discoveries go to `.later/`, not a second live branch

When a new job appears during a running workstream, write a parked card under `.later/` (gitignored except README). Do not create `agent/<new-id>` in that session unless the human explicitly sequences another job. `./ask status` lists those cards as a later block from the checkout; they are not live workstreams. Template: `_ask/templates/later-work.md`.
