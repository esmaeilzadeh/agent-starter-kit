# Intent: recover continuation execution evidence

## What
Prepare and seal the durable continuation repair plan addressing all R1–R4
findings, isolated from the interrupted product workstream.

## Why
Missing/replaced runtime state must not erase real execution or restart a task
at its implemented candidate without reconciliation.

## Non-goals
Implementation, behavior execution, runtime initialization/bootstrap, product
integration/adoption, scheduling and workstream acceptance.

## Known assumptions
Local cooperative Git; existing coordinator admission, authority and TDD gates
remain required. The selected base is the original current product branch.

## Human decisions
Explore skipped: destination already clear. Existing explicit planning direction
and selected base are recorded in authorization.md. This derived planning intent
records scope; it is not a fabricated submitted complete-intent approval.
No implementation may start without the normal exact intent confirmation.

## E2E
Applies: disposable Git repositories and bounded fresh processes, specified in
plan.md and test-plan.json; no behavior execution at the planning endpoint.
