# Plan: Read the shared Later inbox from develop

## Specification

The later listing is based on committed cards from the integration branch rather than the current worktree. Use local `develop`, then `origin/develop`, with current default-branch fallback only when no develop ref exists.

## Approach

1. Add a temporary-repository regression: a card exists on develop but not on the checked-out feature branch; verify the CLI lists it.
2. Read `.later` file names and contents from the integration Git ref.
3. Update usage guidance, ADR, policies, and the still-open card to reflect the implemented listing behavior and preserve unrelated proposed work.
4. Run the full status test and repository verifier; record any independent gate.

## Work breakdown

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| LATER-001 | Integration-ref listing with regression coverage | — | `_ask/scripts/status.sh`, `_ask/tests/test-status.sh`, relevant policy/docs | status integration-ref fixture | Test passes for local and remote develop refs |

## Risks

Repositories without a develop ref retain their existing default-branch fallback behavior.

## Verification approach

Run `bash _ask/tests/test-status.sh`, `git diff --check`, and `./ask verify`.

## Out of scope for this plan

Card creation, tracker synchronization, uncommitted-card display, or Git publication changes.

## E2E

`not_applicable`: the status CLI test exercises the cross-branch scenario in an isolated Git repository.
