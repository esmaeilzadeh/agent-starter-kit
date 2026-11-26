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

## Hook preservation regression

The install journey with a pre-existing `.codex/hooks.json` containing only
`PostToolUse` failed with `unowned destination collision`. The transaction
comparison assumed the startup event already existed. Treat an absent event as
an empty list, matching the hook merger. The focused regression covers both
editors, preserving unrelated handlers and loading both registered commands.
It failed before the production change.

Access-preflight tests also exposed stale fixtures: the hook fixture omitted
the shared bootstrap, the start-work fixture omitted its clean-check module,
and a workspace-denial pattern also matched linked Git metadata. Correct the
fixtures without changing access-check behavior. All five access tests pass.

Add both suites to this source repository's mandatory CheckPlan and document
client hook ownership and runtime trust. The original four CWH journeys pass
at `5550dc86`; the expanded suite and aggregate will be rerun on the new commit.

## Verification

The fixed off-path test passed in the original checkout in 4.92 seconds.
The full CheckPlan passed all 41 checks at `99682327`, including five hook
journeys and five access checks. Three additional transaction safety cases pass.
The only follow-up implementation delta is test probe cleanup in
`test_access_check.py`; all five access tests pass in primary and linked
checkouts at `91ba897c`, with no leftover probes. Production code and CheckPlan
are unchanged. Reports: `verification.json` and `followup-verification.json`.

## Reproduce on another machine

Check out the annotated `v2.0.2` release in a clean clone and run `./ask verify`.
To inspect the historical accepted test authority, fetch
`refs/ask/accepted-tests/client-workflow-hooks` from origin explicitly. The
release uses direct source verification; historical coordinator state remains
unavailable and is not synthesized. The stable frozen-checkout pin and
recreation command remain in `../dogfood-directory-persistence/frozen-copy.md`.
