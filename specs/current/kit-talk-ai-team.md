# Specification: AI team talk on method and tooling

## Status

CURRENT

## Goal

A 90-minute talk an AI team can copy off the machine: `_ask/docs/talks/method-and-tooling.pptx` and `_ask/docs/talks/method-and-tooling.pdf`. Same 24 slides as the HTML source. The talk teaches the kit method and the `./ask` tooling. The facilitator demo gets one slide.

## Non-goals

- Live moons training as the main act
- Changing Guide, Build Spec, policies, or command names
- A Streamlit or Reveal.js runtime
- New `./ask` commands

## Behavior

- Portable files: `.pptx` (present in PowerPoint / LibreOffice / Keynote) and `.pdf` (print or project without the kit repo).
- Speaker notes live on the PPTX slides.
- HTML at `_ask/docs/talks/method-and-tooling.html` remains a local preview, not the handout.
- Section order: method first, tooling second, demo one slide, adopt/discuss last.
- One slide names the three objects: `install` (kit files), `prepare` (pinned Community Skills), `setup` (human-only tracker + MCP). `sync` may appear as a fourth verb on that slide or the next; it must not be collapsed into those three.
- Demo slide points at `_ask/docs/demo/end-to-end-plan.md` and states the punchline (registry + SHA, not chat). It does not walk Path A command-by-command.
- Every claim is supported by the Guide, root `README.md`, `./ask` help, or the demo plan. No invented metrics, dates, or product promises.
- `_ask/docs/README.md` lists the talk.

## Interfaces

- Files: `_ask/docs/talks/method-and-tooling.pptx`, `_ask/docs/talks/method-and-tooling.pdf`
- Preview: `_ask/docs/talks/method-and-tooling.html`
- Optional short how-to in `_ask/docs/talks/README.md`
- Index link: `_ask/docs/README.md`

## Constraints

- No network required to present (no CDN).
- Humanizer embedded mode on prose. Leave commands, paths, and link targets unchanged.
- Do not edit `_ask/guide/` or `_ask/spec/` in this workstream.

## Invariants

- Demo is one slide.
- `setup` is described as human-only / TTY / agents must not run it.
- `install` targets another git repo; this kit repo already has the kit.
- `prepare` reads `_ask/skills/manifest.yaml` and refuses `revision: latest`.

## Failure cases

- A presenter cannot advance slides from the keyboard.
- Notes are the only place a required claim appears (audience cannot follow without notes).
- The three verbs are listed without saying what object each one acts on.

## Acceptance criteria

- PPTX and PDF exist under `_ask/docs/talks/` and contain the full 24-slide deck.
- Method and tooling each have multiple slides; demo has exactly one content slide.
- `_ask/docs/README.md` links the talk.
- `./ask verify` passes.

## Open questions

None.

## Source intent

`work/kit-talk-ai-team/intent.md`
