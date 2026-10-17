# Handoff: continue RWB-109 on another machine

**Repository:** `agent-starter-kit`  
**Branch:** `agent/revising-workbench`  
**Starting commit:** `68a1cea` — `test(ui): retain browser journey traces and screenshots`  
**Remote:** `origin/agent/revising-workbench`

The branch was pushed and the worktree was clean when this handoff was prepared.

## Resume

1. Fetch and check out `agent/revising-workbench`.
2. Read `AGENTS.md` and the current RWB-109 workstream artifacts before editing.
3. Run `./ask check-clean` before starting work.
4. Rerun the interrupted performance benchmark on the current candidate:

   ```bash
   PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/google-chrome \
     _ask/.venv/bin/python -m unittest _ask.tests.test_revising_performance -v
   ```

   If Chrome is installed elsewhere, set `PLAYWRIGHT_CHROMIUM_EXECUTABLE` to its path. The benchmark takes a few minutes. The previous attempt was stopped at the user's request, so it did not produce a completed result for `68a1cea`.

5. Inspect `work/revising-workbench/traceability/rwb109/browser-benchmark.json`. The last completed benchmark was bound to `cdd9d7f`, before the trace-retention-only change in `68a1cea`. It passed: warm p95 was 299 ms overview, 152 ms metadata navigation, 195 ms filter, and 484 ms source/result; five cold starts were 2.0–2.4 seconds. Rerun to produce measurements for the current candidate.
6. Complete `work/revising-workbench/workbench-validation.md` with the candidate identity, browser outcomes, benchmark measurements, artifact paths, and remaining manual checks. Browser traces and screenshots are written under `work/revising-workbench/traceability/rwb109/browser-traces/`; generated runtime artifacts are ignored.
7. Run `./ask verify` and follow the repository's result-recording workflow. Do not record human scenario acceptance or independent semantic review as complete without their required evidence.

## Findings and changes already committed

- The root `.venv` was removed. Workbench dependencies live in `_ask/.venv`, and launcher/helper paths and ignore rules were updated.
- The no-op Scenario “Open test” route was fixed by including inline canonical scenario tests in navigation and test records.
- The WB-003 result view now uses the retained approved test-review contract and genuine historical execution evidence. Its cache key incorporates relevant evidence content.
- The keyboard-focus contrast failure was real: the teal outline against Streamlit's dark focused button background measured 2.37:1. Commit `cdd9d7f` added a white inner outline and teal outer ring; the narrow keyboard browser test passed.
- The full browser suite passed once. A later rerun had a transient timeout in a legacy fixture's “Behavior assertion” route; that journey passed when rerun in isolation. Record both outcomes accurately.

## Remaining

- Complete the final benchmark for `68a1cea`.
- Write the RWB-109 validation record and run final `./ask verify`.
- The user's first-deployment walkthrough and its genuine human-comprehension record are pending. The automated test only verifies that missing or invalid human records are rejected.
- Independent semantic review remains a workflow prerequisite. Do not fabricate or self-approve it.
