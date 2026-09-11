# Skills

## Manifest schema (v1)

`manifest.yaml` entries:

| Field | Required | Meaning |
| --- | --- | --- |
| `source` | yes | `owner/repo` or git URL (skills.sh / GitHub) |
| `revision` | yes | tag, branch, or SHA — **never `latest`** for critical methods |
| `skill` | yes when repo has many | CLI `--skill` name |
| `role` | yes | kit semantics (`explore-map`, `intent-clarification`, …) |
| `required` | no | prepare fails closed when true |

Pins map to the skills CLI as `source#revision`.

## Dual lock

- `manifest.yaml` — human-reviewed pins (this directory; **consumer-owned** on upgrade)
- `skills-lock.json` (repo root) — CLI install record; commit it
- `.agents/skills/` — prepared bodies; gitignored; regenerate via `./pek prepare`

## Never

- `revision: latest`
- blind `skills update` for critical engineering methods

Bump pins deliberately in the manifest instead.
