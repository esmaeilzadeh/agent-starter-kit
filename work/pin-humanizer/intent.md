# Intent: pin humanizer for docs and specs

## What

Pin Community Skill `humanizer` from `blader/humanizer` at tag `v3.0.0` in the kit skill manifest. Add a stock Cursor rule plus Spec-stage contracts so agents always apply that skill when writing or editing documentation and specifications.

Explore skipped: destination already clear.

## Why

Kit docs and specs were shipping with default-model writing tells. This work wires the method. Rewriting the kit’s own Guide and Build Spec stays parked.

## Non-goals

- Rewriting existing kit Guide, Build Spec, ADRs, or README in this workstream.
- Vendoring the skill body into git.
- `revision: latest`.
- Applying humanizer to code, commands, paths, YAML metadata, or link targets.

## Known assumptions

- Newest tag at pin time is `v3.0.0`.
- `required: true` so prepare fails closed.
- Role `docs-voice`.
- Thin always-on Cursor rule (not glob-only) so it fires when creating new docs or specs.
- Existing consumers keep their own manifest on upgrade; this repo’s stock pin is the default for new installs and for this dogfood clone.

## Open questions

None.

## Human decisions

- Skill: https://www.skills.sh/blader/humanizer/humanizer
- Always use it when writing docs and specs.
- Commit, merge to `main`, and push.
- Park “humanize the kit’s own docs and specs” in `.later/`.
