# Ask local tracker context

- **`.ask/tracker.md`** — public tracker *type* and URL. Safe to commit. The setup wizard writes this.
- **`.ask/tracker-context.md`** — current epic/story. Gitignored. Do not commit.
- **`.ask.env`** (repo root) — secrets. Gitignored. Start from `.ask.env.example`.

Agents must not run `./ask setup` (human-only, needs a TTY).
