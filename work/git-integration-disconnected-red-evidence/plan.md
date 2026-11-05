# Plan: Explain disconnected red evidence

## Specification

For a recognized behavior red whose source commit is not an ancestor of final candidate, completion fails with a non-empty explanation naming the red source and final candidate SHA. Other ancestry errors retain stderr or a command/status fallback.

## Approach

1. Add a regression using an orphan commit with a tree identical to the red source; require an actionable completion error.
2. Add a small ancestry helper that distinguishes `merge-base` exit 1 from unexpected Git errors.
3. Run the targeted regression and the traceability evidence test module.
4. Preserve the existing parked investigation for policy decisions beyond diagnostics.

## Work breakdown

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| TRACE-001 | Non-empty disconnected-source diagnostic | — | `.agents/ask/verification/traceability/completion.py`, `_ask/tests/test_traceability_evidence.py` | `test_disconnected_red_source_has_actionable_ancestry_error` | Targeted test and 13-test evidence module pass |

## Risks

Git exit status semantics must remain distinguished: 1 is the ordinary non-ancestor result; other nonzero statuses can indicate invalid objects or command failures.

## Verification approach

Run the exact regression first, then `PYTHONPATH=_ask/tests python3 -m unittest test_traceability_evidence`. Run `./ask verify` and record any unrelated migration gate.

## Out of scope for this plan

Any change to ancestry policy, identical-tree source identity, or retained attempt classification.

## E2E

`not_applicable`: the evaluator test runs against a temporary Git repository with a disconnected commit object.
