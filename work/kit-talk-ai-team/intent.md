# Intent: AI team talk on method and tooling

## What

Ship a 90-minute slideshow an AI team can present from a browser. The talk covers the kit method (Division of Engineering Labor, engineering-system ownership, Explore + pipeline, evidence) and the tooling (`./ask` commands, workstreams, pinned skills, thin Cursor binding). Give `setup`, `install`, and `prepare` their own slide so the three objects stay distinct. One slide points at the existing facilitator demo; the demo is not the spine of the hour.

Explore skipped: destination already clear.

## Why

The team needs a shared account of why the kit exists and which command does which job. `setup`, `install`, and `prepare` already confuse people who work in this repo.

## Non-goals

- Running Path A moons training as the main act
- Rewriting Guide or Build Spec prose
- Renaming `setup` / `install` / `prepare`
- A Streamlit or Reveal.js app as the deck
- New kit protocol, policies, or `./ask` commands

## Known assumptions

- "1.5" means 90 minutes.
- Format is one self-contained HTML file under `_ask/docs/talks/`. Open the file; no server.
- Claims stay inside the Guide, root `README.md`, `./ask` help, and `_ask/docs/demo/end-to-end-plan.md`.
- Humanizer in embedded mode. Technical/plain voice. No writing sample.
- Empty `askit-global-cli` template stubs were discarded so this workstream could start.
- Linking the talk from `_ask/docs/README.md` is enough; root `README.md` stays the kit entry.

## Open questions

None that block Intent.

## Human decisions

- Audience: AI team.
- Length: 90 minutes.
- Demo: one slide, light weight.
- Method and tooling both in scope.
- Three-verb confusion is in scope.
