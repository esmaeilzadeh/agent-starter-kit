# Workflow verification repairs

## Authorization and route

Bug-fix continuation of `fix/workflow-routing-and-authority`. The human asked to
run all tests and check the flows, then explicitly requested: “do bug fixes with
kit enabled bug fix flow”. Preserve existing contracts and approval boundaries;
do not change product expectations to make checks pass.

## Frozen kit authority

Dogfooding enabled for these remaining repairs using commit
`0e303265ceae1fbcdc9b2261bd922b003ab68924` at
`/home/mohamad/Projects/UNI/ai-agent-start-kit-dogfood-0e303265`.
That detached checkout was verified clean. Keep this pin and copy unchanged.
Its workflow policy's reproduced-bug path governs diagnosis, repair, independent
review and verification. This working checkout remains the product under test.
No feature spec/plan or TaskGraph is adopted for this focused repair.

## Initial evidence

- At `36c12c062415e68931495005005e6f609ec5b55c`, all 41 repository CheckPlan
  checks passed using temporary Node 22.18.0 (including previously skipped cases).
- Expanded Python discovery on independent baseline `4c525115` ran 302 cases:
  20 failures and 4 errors. Log: `/tmp/ask-all-python.log`.
- The missing runner-adapter fixture failure is already repaired in `c384f72a`.
- Some browser/benchmark checks modified tracked evidence in that disposable
  checkout; later checks correctly refused dirty candidate provenance.
- Remaining failures require individual reproduction before any repair. Distinguish
  product defects, stale/incomplete fixtures, process-global test contamination,
  missing retained evidence and environment failures. Never weaken authority,
  provenance or isolation guards to obtain green results.

## Completion evidence

Pending focused reproductions, minimal repairs, independent review, and final
repository verification plus expanded test results at the resulting commit.
