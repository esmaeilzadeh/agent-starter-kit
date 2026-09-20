# Later work

Not a live workstream. `./ask status` lists these cards as a later block (checkout `.later/*.md`, skip this README). `--later-only` prints only that block. `--work-only` prints only workstreams.

Cards are durable coordination state. Commit them to `develop` (or the
repository's configured Git-flow integration branch) and mirror each card to
the configured issue tracker. Do not merge a card directly into protected
`main`.

When a second job appears **during** a running work:

1. Copy `_ask/templates/later-work.md` to `.later/<slug>.md`.
2. Create or update its tracker issue.
3. Publish the card to the integration branch without starting a second workstream.
4. Stay on the current `work/<id>/`. Do not run `./ask start-work` for the new id in this session unless the human explicitly sequences another job.
5. Later: new session → `./ask start-work <id>` → Explore / Grill / …
