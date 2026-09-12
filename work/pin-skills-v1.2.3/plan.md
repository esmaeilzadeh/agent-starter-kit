# Plan

## Specification

`specs/current/pin-skills-v1.2.3.md`

## Approach

Edit manifest, align spec example, run `./ask prepare`, commit lock.

## Work breakdown

1. Manifest + spec example.
2. `./ask prepare` → `skills-lock.json`.
3. Verify.

## Risks

Tag `v1.2.3` could move. Mitigation: lock hashes.

## Verification approach

`./ask prepare` exit 0; `./ask verify`.

## Out of scope for this plan

skip-explore. later-inbox.
