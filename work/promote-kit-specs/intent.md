# Intent: promote kit contracts into the Build Spec

Explore skipped: destination already clear.

## What

Fold the kit-protocol contracts that already live under `specs/current/` (later-inbox, workstream status / session-only off-path, real skip of 00, and `./ask record-run`) into the existing `_ask/spec/` modules so the Build Spec is the source of truth.

## Why

Those behaviors are shipped kit, but an agent reading only `_ask/spec/` still misses them. The portable contract should describe what the kit actually is.

## Non-goals

- New `_ask/spec/` files
- Moving product-only demo pieces (moons trainer, Streamlit viewer)
- Changing scripts, agents, templates, or policies
- Reconciling the earlier artifact-schema drift (challenge/review/acceptance JSON)

## Known assumptions

- “Move” means insert into the matching existing spec sections, then leave the product specs as pointers (not a second SoT).
- `demo-nn-train` stays as the demo-vehicle spec; only the `record-run` command contract is promoted.

## Open questions

None — human directed insert-into-existing-files.

## Human decisions

- Insert, do not create new Build Spec modules.
- Place each contract in the file it already belongs to.
