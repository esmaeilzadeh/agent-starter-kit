# Specification Change Proposal

## Current specification

HTML-only deck at `_ask/docs/talks/method-and-tooling.html`.

## Proposed change

Ship portable `_ask/docs/talks/method-and-tooling.pptx` and `.pdf` as the handout. HTML stays as a local preview.

## Why the change is needed

The talk has to leave this repo: email, USB, a laptop that is not the kit clone.

## Impacted artifacts

`specs/current/kit-talk-ai-team.md`, `_ask/docs/talks/`, `_ask/docs/README.md`

## Impacted workstreams

`kit-talk-ai-team` only.

## Migration / transition notes

Same 24 slides and claims.

## Acceptance criteria for the change

PPTX and PDF exist and contain the full deck.

## Decision

Accepted. Human asked for PDF or PPT because the deck must be portable.
