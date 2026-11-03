# Intent: Ignore template guidance when inferring workstream stage

## What

Fix `./ask status` stage inference so instructional placeholder text in workstream templates does not count as completed artifact content. In particular, a new workstream with an untouched `review.md` must not be reported as `reviewed`. Preserve recognition of substantive review content.

Also ensure that when the workflow must pause for a human choice, prepared workstream artifacts are checkpointed on the work branch first, leaving the checkout clean and resumable.

## Why

The current `meaningful()` heuristic accepts prose under `## Findings` in the stock review template. `stage()` then reports `reviewed`, which misleads continuation recovery and can make an incomplete workstream look further along than its evidence supports. Leaving newly prepared but uncommitted artifacts in the checkout when a required choice is pending also makes a later continuation fail the clean-worktree gate.

## Non-goals

- Change review requirements or the review template’s guidance.
- Change `check-workstream` confirmation behavior.
- Change workstream branch inventory, archive rules, or stage ordering.
- Repair other workstreams’ artifacts.
- Stash or discard pending work automatically.

## Known assumptions

- The status stage is inferred from committed artifact contents.
- Template instructions should not count as evidence that a stage was completed.
- The fix can remain local to `./ask status` inference.
- A prepared intent can be committed as an unapproved draft before asking the required intent choice; approval remains tied to its exact content.

## Open questions

None.

## Human decisions

None.

## E2E

Applicability: not_applicable

If not_applicable, reason: This is a local CLI inventory classification fix with no separate end-to-end user journey or external system.

Explore skipped: destination already clear.
