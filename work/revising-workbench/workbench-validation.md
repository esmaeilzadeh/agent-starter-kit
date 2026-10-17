# RWB-109 validation

## Run identities

- Browser benchmark candidate: `f52c441d780473bad86cae24abe4f0ae57d5a547`
- RWB-108 test candidate: `9c92504605824eb7c9430108ea01c96b6f4cf007`
- Latest recorded verification candidate: `0dff0d5cd1a24c5f265354ada63d85cf372a4a3c`
- Workstream: `agent/revising-workbench`
- Browser: `/usr/bin/google-chrome`
- Test environment: `_ask/.venv`, installed from `_ask/ui/requirements.txt` and
  `_ask/ui/requirements-test.txt`

## Browser and performance evidence

The benchmark command was run on 2026-10-17:

```text
PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/google-chrome
_ask/.venv/bin/python -m unittest _ask.tests.test_revising_performance -v
```

The benchmark stopped during fixture validation, before launching the browser.
It reported that representative admission identities could not be verified
because the retained successful historical report/log identity was missing or
ambiguous. The required
`work/structured-agentic-environment/traceability/executions.json` ledger is not
present in this checkout. No warm samples, cold starts, browser traces, or
screenshots were produced. The ignored local diagnostic is
`work/revising-workbench/traceability/rwb109/browser-benchmark.json`; it records
the failed run against the candidate above.

The earlier successful browser suite and pre-`68a1cea` benchmark described in
`handoff.md` remain historical evidence and do not certify this candidate.

## Remaining evidence

- Restore the genuine WB-003 execution ledger and confirm its report/log identity
  through the existing evidence authority, then rerun the benchmark.
- Complete browser navigation, guard, evidence, accessibility, and pilot checks;
  retain their traces and screenshots against the final candidate.
- Record the genuine human comprehension exercise against the final candidate.
- Complete the independent semantic review and final workstream verification.

No human acceptance or successful RWB-109 validation is claimed here.

## RWB-108 prerequisite check

`python3 -m unittest _ask.tests.test_revising_pilot -v` ran 12 cases on the
RWB-108 candidate: 8 passed and 4 failed. The failures were the genuine WB-003
observation and representative passage gate; both depend on the absent retained
execution ledger. The source workstream's existing
`work/structured-agentic-environment/traceability/completion.json` records
`candidate source/CheckPlan changed during verification`, so its reports cannot
be promoted as completed evidence. No ledger or historical completion record
was reconstructed.

## Kit verification

`./ask verify` on `0dff0d5cd1a24c5f265354ada63d85cf372a4a3c` failed before running
any checks with `candidate acceptance document differs from coordinator
authority`: the candidate pin names contract `54d2e10`, while the coordinator
ref names `54ef012`. An independent review artifact for the candidate contract
exists, but the accepted ref was not advanced through the coordinator workflow.
The inner-loop still marks RWB-108 running, so its plan's no-running-task gate
must be followed before advancing that ref. This record does not alter the
acceptance authority or task state.
