# Plan

## Specification

`specs/current/kit-talk-ai-team.md`

## Approach

One HTML file with inlined CSS and a few lines of JS for navigation and notes. Copy claims from the Guide, root README, `./ask` help, and the demo plan. Humanizer pass on prose before finish.

## Work breakdown

1. Intent, spec, challenge, plan on this branch.
2. Write `_ask/docs/talks/method-and-tooling.html` plus a short `README.md`.
3. Link the talk from `_ask/docs/README.md`.
4. Verify.

## Risks

Slide prose can drift into Guide paraphrase that still reads like default-model text. Run humanizer on the visible copy.

Empty `start-work` templates in this folder should not be committed until they have content (intent and plan already do).

## Verification approach

- File exists; keyboard handlers are in the page.
- Demo section is a single content slide.
- Docs index links the talk.
- `./ask verify`

## Out of scope for this plan

Live demo execution. Command renames. Guide edits.
