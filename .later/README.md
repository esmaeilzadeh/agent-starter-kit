# Later work (local inbox)

Not a live workstream. `./ask status` lists these cards as a later block (checkout `.later/*.md`, skip this README). `--later-only` prints only that block. `--work-only` prints only workstreams.

When a second job appears **during** a running work:

1. Copy `_ask/templates/later-work.md` to `.later/<slug>.md`.
2. Stay on the current `work/<id>/`. Do not run `./ask start-work` for the new id in this session unless the human explicitly sequences another job.
3. Later: new session → `./ask start-work <id>` → Explore / Grill / …

Card files in this directory commit on `develop` with a tracker issue (`_ask/policies/git-flow.md`). This README is kit-owned.
