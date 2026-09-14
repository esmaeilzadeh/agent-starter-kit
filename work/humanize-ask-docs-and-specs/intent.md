# Intent: humanize kit Guide, docs, and README pages

## What

Run the prepared `humanizer` skill in file mode over kit Guide modules, `_ask/docs/` (ADRs, demo, research, kit-author notes), and README pages (`README.md`, `_ask/README.md`, and READMEs inside those trees). Keep every supported claim. Do not invent facts. Leave code, commands, paths, YAML metadata, and link targets unchanged. Do not change protocol meaning.

Explore skipped: destination already clear.

## Why

`pin-humanizer` only wired the method. Guide, kit-author docs, and README pages still read like default-model prose. Build Spec stays machine-first: agents consume it, so its current wording is more important than a human voice pass.

## Non-goals

- `_ask/spec/` and the monolith Build Spec stub.
- `_ask/agents/`, `_ask/policies/`, `_ask/templates/`.
- Generated `.cursor/` projections.
- Historical `work/` and `specs/current/` records.
- Scripts, tests, YAML, lockfiles.
- Changing must/must-not meaning, commands, or path names.

## Known assumptions

- Technical/plain voice. No writing sample.
- Full pass on the in-scope set, not a two-file sample.
- Root `CONTEXT.md`, `AGENTS.md`, `_ask/OWNED-PATHS.md`, and `_ask/MAPPING.md` stay out (not Guide, `_ask/docs/`, or README).
- Research under `_ask/docs/research/` is in because it lives under docs.
- No `./ask sync` unless a synced source changes (none in this cut).
- `.later/` card stays local and uncommitted.

## Open questions

None that block Intent. Assume-list above still needs “defaults OK” if you want a different cut (drop research, add CONTEXT, etc.).

## Human decisions

- Q1: spec is out. Only docs, Guide, and README pages.
- Machine-readable Build Spec wins over a humanizer pass on `_ask/spec/`.
