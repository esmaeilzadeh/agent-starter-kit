# Missing-state continuation reproduction

Date: 2026-10-22. Source checkout: `c34c969844219458e4648a1aec020814454f6daf`.
Executed against a disposable repository through existing integration-test
fixtures. The fixture's TDD output is synthetic test data; this replay proves
scheduler behavior, not real product Red/Green or task acceptance.

## Command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=_ask/scripts:_ask/tests python3 - <<'PY'
from inner_loop_reliability import IntegrationTests
from inner_loop.driver import run_until
from inner_loop.state import state_path, load_state
case = IntegrationTests('test_other_candidate_report_is_rejected')
try:
    case.setUp()
    case.review()
    state_path(case.root, 'w').unlink()
    print('Retained TaskResult:',
          (case.root / 'work/w/inner-loop/results/a.json').is_file())
    print('Retained review:',
          (case.root / 'work/w/inner-loop/evidence/review.md').is_file())
    outcome = run_until(case.root, 'w')
    print('Observed continuation:', outcome)
    print('Recorded new base equals already implemented candidate:',
          load_state(case.root, 'w')['tasks']['a']['base_sha'] == case.candidate)
    assert outcome != 'running=a', 'BUG: continuation restarted executed task from its Green candidate despite retained execution/review evidence'
finally:
    case.doCleanups()
PY
```

## Observed output

```text
Retained TaskResult: True
Retained review: True
Observed continuation: running=a
Recorded new base equals already implemented candidate: True
AssertionError: BUG: continuation restarted executed task from its Green candidate despite retained execution/review evidence
```

Exit: 1, assertion failure at the scheduler outcome. Temporary repo cleaned.
No production fix is present.

## Workstream timeline

- Task 2's initial Red at `3c7f945` and subsequent corrections are described in
  retained `inner-loop/evidence/2-review.md` and `2-review-round3.md`.
- `235bc5f` adds the overflowing-number failing behavior assertion; `0d9089f`
  fixes it. Retained round-3 review approves exactly `0d9089f` and names the
  corresponding immutable run IDs; these claims need artifact verification
  during recovery, not blind promotion to current authority.
- Tasks 3–5 implementation commits follow Task 2 on this same branch.
- The earliest committed current state at `0dff56b` marks Tasks 2–10 pending.
  Prior runtime state was not committed; the exact action that produced that
  pending state is not established by Git history alone.
- `bdb7bac` records Task 1 integration and starts Task 2 at `c8a5ea2`, which
  already descends from `0d9089f` and includes Task 2 implementation.
- `43b9e0a` reclassifies nine passing Task 2 cases as regressions; `a8c5989`
  registers that amendment. `c34c969` records the integration gate blocker.

This establishes loss of continuity between implementation history and the
restarted queue. It does not establish the exact mechanism of the original
runtime-state loss or prove that historical integration receipts exist.
