# Skills

## Manifest schema (v1)

`manifest.yaml` entries:

| Field | Required | Meaning |
| --- | --- | --- |
| `source` | yes | `owner/repo` or git URL (skills.sh / GitHub) |
| `revision` | yes | Git tag such as `v1.2.3` or a full commit SHA |
| `skill` | yes when repo has many | CLI `--skill` name |
| `role` | yes | kit semantics (`explore-map`, `intent-clarification`, `docs-voice`, …) |
| `required` | no | prepare fails closed when true |

`./ask prepare` uses `.agents/ask.local/skills/manifest.yaml` when it exists.
It resolves a tag to a commit before installing the skill. AskIt stores the
approved commit locally and asks again if the tag moves. `SKIP_INSTALL=1`
validates tag syntax without contacting the source.

## Dual lock

- `.agents/ask.local/skills/manifest.yaml` — project pins to review and commit
- `_ask/skills/manifest.yaml` — default pins used to seed new projects
- `skills-lock.json` (repo root) — CLI install record; commit it
- `.agents/skills/` — prepared bodies; gitignored; regenerate via `./ask prepare`

## Never

- `revision: latest`
- blind `skills update` for critical engineering methods

Bump pins deliberately in the manifest instead.

Stock docs-voice pin: `humanizer` from `blader/humanizer` (human-facing set only). Stock agent-docs pin: `writing-for-agents` from `mattpocock/skills`. See ADR 0017.
