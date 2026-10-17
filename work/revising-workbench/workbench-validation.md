# RWB-109 validation

## Run identities

- Browser benchmark candidate: `f52c441d780473bad86cae24abe4f0ae57d5a547`
- RWB-108 test candidate: `9c92504605824eb7c9430108ea01c96b6f4cf007`
- Latest recorded verification candidate: `f085f12b376dc13a5b26cdead68d8da0d86e9d29`
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

The candidate traceability execution on `f085f12` recorded 70 final-green cases:
64 passed, 5 failed, and 1 errored. The RWB-108 failures are
`RWB-GENUINE-WB003` and `RWB-DEMO-PASSAGES`, both blocked by the absent WB-003
ledger. RWB-109 also has three browser failures (`RWB-BROWSER-NAV`,
`RWB-BROWSER-ACCESS`, and `RWB-BROWSER-PILOT`) because those cases open
`work/ask-status` without an admitted engineering model; the browser app reports
`EM001_MODEL_READ`. `RWB-BROWSER-BUDGETS` errors on the same missing historical
WB-003 identity. These RWB-109 failures need correction under RWB-109's task
scope after RWB-108 is completed.

## Kit verification

The RWB-107 amendment is now coordinator-pinned at contract `54d2e10`. The task
was paused and readmitted under that reviewed pin in commits `b000e92` and
`f085f12`, preserving its original base `7433097`.

`./ask verify` on `f085f12b376dc13a5b26cdead68d8da0d86e9d29` passed all 37
repository checks, then failed workstream completion because no independent
review is recorded for that candidate at
`work/revising-workbench/traceability/reviews/f085f12b376dc13a5b26cdead68d8da0d86e9d29.json`.
The generated completion record is ignored runtime output at
`work/revising-workbench/traceability/completion.json`. No review was
self-authored or claimed.

At the time of this record, RWB-108 remains the active task and RWB-109 remains
pending. Final acceptance also still requires the candidate-bound human
comprehension exercise.
