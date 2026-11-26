# Client hooks release repair

## Authority and scope

The human requested “fix them” after checking the unfinished entry-point feature
and the client-hook acceptance blockers. They delegated acceptance when confidence
exceeds 90%. This repair uses the highest-priority source self-development rule:
the kit workflow is disabled; the frozen checkout remains unchanged at
`0e303265ceae1fbcdc9b2261bd922b003ab68924`.

Sequence: repair and verify the hook release, record direct source-development
acceptance with its limits, release with an annotated tag and matching README pin,
then complete the separate source-entry-point documentation feature. Do not
synthesize missing coordinator state or relabel the rejected historical workflow
completion as passing.

## Reproduction

`timeout 45s bash _ask/tests/test-sync-off-path-command.sh` exited 124 in the
working checkout. It copied `_ask/.venv` (589 MB) into the disposable Git fixture.
The unchanged test in a clean detached checkout at `c61ebc7b` passed in 5.21 seconds.
This isolates ignored checkout data from the sync transaction and exit trap.

## Fix

Build the fixture with `git archive HEAD _ask .agents/ask`. It exercises the
committed source while excluding untracked or ignored environments and logs.
The existing off-path projection assertions are unchanged.

## Verification

Pending the focused rerun, hook journeys, and full release CheckPlan.
