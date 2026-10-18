# Intent: Show durable later cards from the integration branch

## What

Make `./ask status` read committed `.later/*.md` cards from local `develop`, falling back to `origin/develop` when the local branch is absent. Use the existing default branch only when neither develop ref is available. Keep all other status behavior unchanged.

## Why

A work branch can omit committed develop cards, making durable parked work invisible and causing agents to miss queued tasks.

## Non-goals

Adding a later-card creation command, tracker integration, publication workflow, or a new policy for unpublished local cards.

## Known assumptions

The repository policy defines `develop` as the integration branch and keeps parked cards there.

## Open questions

None for the confirmed listing bug.

## Human decisions

None required; existing Git-flow policy establishes the integration branch and the bug has a deterministic regression test.

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: The isolated status CLI test covers the observable behavior through a temporary git repository.
