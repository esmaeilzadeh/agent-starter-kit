# Request routing guard: scoped authorization

## User direction

Before any stage prompt is selected, classify each requested outcome against
the existing accepted behavior. A reproduced defect follows the focused
reproduction-first repair path. A feature follows the feature workflow. A mixed
request is split into separate workstreams with linked dependencies and
sequential execution when the work overlaps.

This direction applies even when the user invokes an Explore or Grill stage
directly. Existing passing edge guards remain Green. Do not invent Red targets,
feature specifications, plans, tests, or fixes for hypothetical failures.

## Boundaries

- Put the routing gate in the root agent instructions and Cursor's always-applied
  workflow rule, then reference it from the canonical Explore and Grill prompts.
- Preserve CR-T13 as its existing one-cycle Green guard.
- Do not remove tests or code without evidence that they were added for the
  unsupported repeated-reopen defect. The current audit found no such test or
  implementation; the sibling setup-error correction is a separate evidenced
  behavior fix.
- Keep the approved workstream `intent.md` and traceability test mapping
  unchanged.
