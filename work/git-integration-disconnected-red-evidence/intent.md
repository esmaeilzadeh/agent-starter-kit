# Intent: Explain disconnected red source commits

## What

When traceability completion sees a recognized red source commit that is not an ancestor of the final candidate, report a clear error naming both commit IDs. Preserve the existing failure and evidence eligibility rules.

## Why

Git's expected exit code 1 for `merge-base --is-ancestor` has no stderr; converting it directly to `Invalid` currently writes an empty string into completion errors.

## Non-goals

Changing registration, retention, exclusion, ancestry requirements, duplicate-tree handling, or any evidence acceptance policy.

## Known assumptions

`git merge-base --is-ancestor` exit code 1 means the commits are not in the required ancestry relation; other nonzero statuses remain Git errors.

## Open questions

None for the diagnostic-only fix.

## Human decisions

None required; the failure mode and desired diagnostic are explicit in the card.

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: A real temporary Git repository in the traceability evaluator unit test reproduces and verifies the diagnostic.
