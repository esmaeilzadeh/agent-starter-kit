# Intent: pin Community Skills to mattpocock/skills v1.2.3

## What

Bump `_ask/skills/manifest.yaml` (and `skills-lock.json`) to `mattpocock/skills` **v1.2.3** for wayfinder, research, prototype, and grilling. `--skill` names must exist at that tag. Never `revision: latest`.

Explore skipped: destination already clear.

## Why

`v1.0.0` has no `wayfinder` or `research` (`decision-mapping` instead). `./ask prepare` fails closed on required `wayfinder`. `v1.2.3` restores those names and includes `prototype`.

## Non-goals

- Pinning the rest of the mattpocock repo.
- Changing prepare-skills.sh behavior beyond what the new pins require.
- The skip-explore gate (other workstream).

## Known assumptions

- Latest tag at pin time is `v1.2.3`.
- Found during skip-explore; run here as its own work-id.

## Open questions

None.

## Human decisions

- Pin the newest tag, not the string `latest`.
- Include optional `prototype` (Explore bind list).
