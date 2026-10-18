# Review

## Model

Repository-based static review.

## Scope

Checked exit-code handling, both SHA values in the diagnostic, unchanged completion failure behavior, and the isolated orphan-commit regression.

## Findings

The helper returns on success, maps status 1 to a specific non-ancestor error, and retains stderr or a command/status fallback for other failures. No evidence eligibility logic changed.

## Suggested fixes

None for this diagnostic-only scope.

## Residual risks

The card's broader Git ancestry/evidence policy remains unresolved and parked.

## Review verdict

Accept the narrow diagnostic fix.
