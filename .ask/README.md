# Ask local tracker context

- **`.ask/tracker.md`** — public tracker *type* and URL. Safe to commit. The setup wizard writes this.
- **`.ask/tracker-context.md`** — current epic/story. Gitignored. Do not commit.
- **`.ask.env`** (repo root) — legacy migration input. Gitignored; migrated credentials are stored outside the checkout. Start from `.ask.env.example` only for public tracker settings.

Agents must not run `./ask setup` (human-only, needs a TTY).

For safe install and upgrade, credential migration, verifier environment
allowlisting and private logs, see the kit's [client security guide](../_ask/docs/client-security.md).
