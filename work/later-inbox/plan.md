# Plan

## Specification

`specs/current/later-inbox.md`

## Approach

Ignore rule + committed README + template + one AGENTS/`work/README` sentence.

## Work breakdown

1. `.gitignore`, `.later/README.md`, template.
2. AGENTS + work/README + short ADR.
3. Verify.

## Risks

Agents still commit cards if they `git add -A` without noticing. README + gitignore mitigate.

## Verification approach

`git check-ignore` on a sample card path; `./ask verify`.

## Out of scope for this plan

skip-explore gate. skill pins. status integration.
