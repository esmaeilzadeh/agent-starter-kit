# Intent: Prefer the checked-out workstream when resolving continuation

## What

When the human says “continue,” “resume,” or equivalent without naming another
workstream, use the checked-out `agent/<work-id>` branch and its artifacts as
the primary continuation target when they resolve to one workstream. Resume its
exact authorized stage and task if work remains. If its recorded state is
terminal or its plan explicitly stopped, report that endpoint and do not ask
the human to choose among unrelated live workstreams. Ask which workstream to
resume only when the branch and repository evidence do not identify one target
or conflict. An explicitly named target takes precedence over the checkout.

## Why

On `agent/shorter-hashes`, “continue” was followed by a choice question because
many unrelated workstreams were live, even though the checkout identified
`shorter-hashes` and its recorded result explicitly stopped at a sealed plan.
The question ignored the strongest available continuation context and made the
user restate what the branch already showed.

## Non-goals

Reopening a terminal workstream, expanding its authorized scope, starting a
different workstream automatically, changing explicit-target precedence,
weakening approval or clean-worktree gates, or changing Engineering Model
subject resolution.

## Known assumptions

The branch name is a reliable locator when it has the form `agent/<work-id>`
and matching workstream artifacts exist. Terminal status means report the
authorized endpoint; it does not authorize new work.

## Open questions

None. The desired next action is determined by explicit target, checked-out
workstream state, and whether the existing authorization permits more work.

## Human decisions

Approve or request changes to this complete intent and its assumptions before
implementation.

## Subject intake

The required read-only intake was attempted with the later card as proposal
context. It returned `valid: false` because the newly seeded workstream has no
`engineering-model.json`. No Engineering Model subject association was
established; the card remains proposal context.

## E2E

Applicability: `not_applicable`

If `not_applicable`, reason: This is a bounded agent instruction change. The
observable continuation cases are: an unfinished checked-out workstream
resumes; a terminal checked-out workstream is reported as terminal; an
explicitly named target overrides the checkout; and ambiguous evidence without
a usable work branch prompts for a choice.
