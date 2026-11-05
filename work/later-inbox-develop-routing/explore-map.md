# Explore Map: shared later-inbox visibility

## Destination

Make committed later cards on the integration branch visible from an agent/work branch.

## Notes

The repo's Git-flow and worktree policies already say later cards are committed on `develop`; `status.sh` instead enumerated `.later` in the current checkout.

## Decisions so far

Use `develop` as the integration ref when present, fall back to `origin/develop` when only the remote-tracking ref exists, and use the existing default branch only in repositories without a develop ref.

## Not yet specified

How a future add command should show unpublished local cards or handle tracker publication.

## Out of scope

Creating cards, tracker sync, publication safeguards, or changes to uncommitted-card handling.

## Handoff to Intent

The isolated status test reproduces a card committed only to `develop` disappearing from an agent branch. Implement only integration-ref listing and correct docs that claimed checkout-local listing.
