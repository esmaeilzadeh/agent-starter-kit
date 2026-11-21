# Task 1 candidate evidence

- Work/task: `shorter-hashes` / `1`
- Task base: `c8a5ea24821b0f984f4e9d7ddee38714d4409d16`
- Immutable candidate: `c8a5ea24821b0f984f4e9d7ddee38714d4409d16`
- Owned source paths: `.agents/ask/workflow_refs/benchmark.py`, `_ask/tests/test_workflow_refs_baseline.py`

## Task cases

- **1/1 Red:** `f6d6791cbdfe985c89df38226808ebb86968bc3b`, amended-plan traceability run `0596b1e2696c429da0ca511fa248a302`; behavior assertion failed because unavailable encoding data leaked `OSError` instead of `BenchmarkError`. Captured output: `work/shorter-hashes/traceability/runs/186cc05d0e7c433e8fc63e2bb619994d/7a14a92aa9a342f39291e6708ed1e66e.log`.
- **1/2 at Red:** passed in the same run.
- **1/1 and 1/2 final Green:** candidate `c8a5ea24821b0f984f4e9d7ddee38714d4409d16`, traceability run `83ad2f42bd5e43018d18da00cfac4eb4`; both passed. Captured output: `work/shorter-hashes/traceability/runs/eb3d7ba983d1445c9c34d8f038194633/51180e28269840c9b5b320d38a240c0d.log`.

## Refactor checks

- No applicable structural cleanup: the behavior fix is a one-line expansion of the tokenizer-load exception tuple.
- `python3 -m py_compile .agents/ask/workflow_refs/benchmark.py _ask/tests/test_workflow_refs_baseline.py` passed.
- `git diff --check` passed.

The task result is `work/shorter-hashes/inner-loop/results/1.json`. Independent review `/root/review_task1` approved candidate `c8a5ea24821b0f984f4e9d7ddee38714d4409d16` with no findings; review evidence is in `work/shorter-hashes/traceability/review-task-1.json`. Integration remains a coordinator action.
