# Plan

## Specification

`specs/current/drop-pek-cli.md`

## Approach

Delete the obsolete work directory. No code rename.

## Work breakdown

1. Delete `work/pek-cli/`.
2. Verify status no longer lists `pek-cli`.
3. Verify + Accept.

## Risks

History still mentions `pek` in `git log` and `work/rename-pek-to-ask`. Fine.

## Verification approach

- `test ! -e work/pek-cli`
- `./ask status --work-id pek-cli` exits 0 with “no workstream”
- `./ask verify`

## Out of scope for this plan

Merging other live branches.
