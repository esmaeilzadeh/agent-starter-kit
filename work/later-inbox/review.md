# Review

## Scope

`.later/` inbox vs `specs/current/later-inbox.md`.

## Findings

gitignore exception for README works (`test-later-inbox-gitignore.sh`). Stock explore-map from old start-work was removed (real skip).

## Suggested fixes

None.

## Residual risks

`git add -A` could still try to add cards; ignore rule should stop it.

## Review verdict

Pass after guidance-test harness fix.
