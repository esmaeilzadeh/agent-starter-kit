# WB-009 preliminary browser test-design review

Verdict: **REJECTED / INCOMPLETE TEST DESIGN**. This is a preliminary review of
the browser obligations, not candidate integration approval, a TaskResult review,
or workstream completion. The writer is continuing separately.

Reviewer: `/root/review_wb009_tests`, independent child of `/root`.
Runtime: Codex. Resolved reviewer model: `gpt-6.1-sol`, high effort, from the
workstream model binding. Parent model identity was not supplied to this child.
Reviewed immutable commit: `3caf633db7345bc3df67b45e90e7444b38d96882`.
Inspected detached snapshot: `/tmp/ask-wb009-browser-review-3caf633`.
No production or test source was edited or committed by this reviewer.

## Authority and scope

Read the WB-009 handoff, plan, test plan, canonical JSON specification revision 3,
draft review, session evidence correction, browser tests, fixture construction,
and relevant navigation/detail implementation at that exact commit. This review
addresses draft findings 1–3 and obligations `WB-browser-journey`,
`WB-browser-accessibility`, `UI-browser`, and `UI-browser-gitless`.
All sixteen WB-009 assignments and their accepted ownership remain unchanged.
The other twelve obligations, final visual checkpoint, final verification, and
candidate-bound independent integration review remain outside this preliminary
decision. The commit changes only the two owned browser test modules.

## Prioritized findings

1. **P1 — Hierarchy assertion design stops before proving the accepted chain.**
   `_ask/tests/test_engineering_workbench_browser.py:203` checks that the story
   exists, but never opens it; lines 212–218 check completed-task list text but
   never open the completed task. Lines 224–239 navigate directly to test,
   scenario, test and result. A broken story → scenario or completed-task → test
   link would therefore escape the intended chain check. Open the recorded story,
   scenario, completed task, owned/shared test and its specifically qualified
   result in sequence, checking selected detail and persistent ancestor context.
   Scope summary assertions to their actual detail/filter container: line 207
   currently matches both outline and detail; line 209's whole-page count of one
   is incompatible with intentionally repeated outline/detail labels. The
   exploratory run fails at line 207 with a strict-mode violation. Assert the
   exact filtered record IDs and count, including exclusion of other records,
   rather than counting every occurrence of a title on the page.

2. **P1 — Accessibility coverage remains incomplete and has false-pass paths.**
   Lines 279–313 now perform actual Tab/Enter scenario/task/test traversal at
   390 and 1440 pixels, which improves the draft. However, only the scenario
   button's focus style/contrast is asserted. The debug control is only checked
   collapsed at line 313, never reached/expanded with keyboard or inspected.
   There is no rendered large-text contrast assertion. The focus calculation at
   lines 286–296 discards alpha, uses the control background without resolving
   transparent ancestors, and does not check the adjacent outer background;
   `_contrast` does compositing for text but is not used for focus. The written
   status contrast assertion is conditional on presence at lines 314–317, so
   missing required status text can pass. The decision flow occurs only after
   the width loop at 1440, and actor/rationale use `fill()` without proving
   keyboard reachability. Overflow is checked only after the decision at 390,
   not during source/debug inspection. Require visible focus on primary controls,
   explicit status text, normal/large/focus contrast with resolved colors, debug
   expansion, keyboard attribution and submission, and route-level overflow at
   both widths. At line 309, use an exact heading selector: the exploratory run
   matches both the source heading and unavailable-source message and fails
   strict mode before the remaining journey.

3. **P1 — Browser result selectors are unqualified and evidence identity checks
   are weak.** `_ask/tests/test_engineering_ui_browser.py:87` calls a helper that
   clicks the first generic `Result / evidence` button. The fixture contains tests
   E and U, and the exploratory run opens E, then fails at line 88 because no
   `Load test results` control exists. The new hierarchy module's result helper
   has the same generic-first behavior at lines 54–58. Select the result belonging
   to the intended test and scenario, and assert its test ID, qualified case,
   work, candidate, source revision and actual outcome. `Passed`, a filename,
   `test U`, or `(historical)` alone do not establish that tuple. The legacy case
   adds available/missing/historical inspection and source checks at lines 86–99,
   but should also explicitly verify canonical assertion and revision provenance,
   not merely `assertEqual` somewhere in source. Preserve these checks when
   repairing routing; the run has not reached the stale/refresh portion.

4. **P2 — Recorded task-result fixture has inconsistent identity.**
   `_ask/tests/test_engineering_workbench_browser.py:142` associates task `build`
   with `results/WB-001.json`, whose line-147 `task_id` is `WB-001`, not `build`;
   `candidate_sha` is the non-SHA literal `fixture-candidate`. This is not valid
   implementation evidence for that completed task. Use a matching task ID and
   real fixture candidate SHA, and distinguish recorded integration status from
   independently verified completion. The fixture also does not assert the shared
   test's deduplicated relationships despite that accepted precondition.

5. **P2 — Gitless test is not executable and omits debug inspection.**
   `_ask/tests/test_engineering_ui_browser.py:163` uses `tempfile` without importing
   it, producing `NameError` before browser setup. Lines 177–181 never select a
   qualified test or expand its debug trace as the accepted scenario requires.
   Add the import and complete those interactions; retain actionable unavailable
   evidence and the prohibition on raw fatal Git output.

6. **P2 — New test dependency and browser selection are undeclared/unhandled.**
   `_ask/tests/test_engineering_workbench_browser.py:15` imports `yaml`, but
   `_ask/ui/requirements-test.txt` does not declare PyYAML. Initial discovery in
   the pinned venv failed with `ModuleNotFoundError`, not a behavior assertion.
   The workbench module launches bundled Chromium at lines 198 and 276; it does
   not honor `ASK_BROWSER_CHANNEL=chrome`. The legacy module honors only an
   explicit executable path. Declare the required test dependency and support a
   documented explicit browser override; do not treat missing binaries/dependency
   errors as accepted red evidence. Coordinator subsequently installed PyYAML
   6.0.3 in the venv, which does not amend this commit's requirements.

## Coverage retained and still requiring proof

| Obligation | Present in source | Remaining requirement / execution limit |
| --- | --- | --- |
| WB-browser-journey | Recorded story/task fixtures; summary attempts; branch-specific source marker; foreign read-only notice and no resolve button; HEAD/refs/model and plan comparisons; fresh current-work default | Actual full chain, exact filter sets, valid task evidence and qualified result identity; run stops at summary selector |
| WB-browser-accessibility | Actual Tab/Enter inspection at both widths; composited normal-text helper; one focus check; attributed choice and fresh-session blocker consequence assertions | Large text, resolved focus/adjacent colors throughout, mandatory status, keyboard debug/attribution, decision flow and overflow at both widths; run stops at source selector |
| UI-browser | Available/missing/historical attempts; linked-spec-only stale edit; model/spec/plan byte comparisons; open/history rejection; refreshed choice history; fresh-session actor/rationale and no-blockers assertions | Qualified result route, canonical assertions/provenance, and execution of later stale/persistence assertions; published-generation pointer identity is not compared |
| UI-browser-gitless | Actionable Git-unavailable assertion and exclusion of fatal Git output | Missing import, selected-test/result qualification, debug expansion; no browser interaction reached |

Foreign-source selection is now a real alternate-branch interaction in source,
with a unique source marker and an unavailable-result expectation rather than
historical-candidate substitution. This is a meaningful repair of draft finding 1.
The branch no-mutation comparison still covers only four model/plan files, HEAD
and refs; it does not compare canonical specs, source/task files or publication
state. Strengthen it to the relevant protected file/publication snapshot. These
assertions were not reached in this run. A missing-result label on w-alt does not
prove a positive matching result from that branch; assert selected branch/work/
candidate identities explicitly.

The stale test now compares definition bytes after external mutation and before
the attempted stale submit. That is the correct comparison boundary and repairs
part of draft finding 3. It also retains decision lifecycle/history checks and a
fresh-session task consequence. Compare the published generation pointer/digest
as well if claiming no publication rather than only no changed definitions.

## Execution evidence and continuity

Initial unmodified discovery using `/tmp/ask-wb009-venv/bin/python` and
`ASK_BROWSER_CHANNEL=chrome` failed to import the workbench module because yaml
was absent. This is setup failure and proves no behavior-red continuity.

An **exploratory** external runner at
`/tmp/ask-wb009-browser-review-run.py` ran both browser modules from the detached
snapshot. It appended `/usr/lib/python3/dist-packages` for the initial yaml
fallback and monkeypatched Playwright `BrowserType.launch` to remove
`executable_path` and select `channel='chrome'`. Source bytes were unchanged.
Environment: Python 3.12, Streamlit 1.59.2, Playwright 1.63.0, installed Chrome
142.0.7444.162. Result: **four cases, three failures and one error, 19.332s**.
Full log: `/tmp/ask-wb009-browser-review-3caf633.log`.

The failures are the two strict-selector violations and legacy absent-results
assertion described above; the error is missing `tempfile`. Ambiguous selectors
and missing imports are test defects, not proof that the accepted behaviors were
red. The wrong-result-route assertion also does not establish stale-save or
persistence behavior, which was never reached. These exploratory results are not
accepted runner records, final green evidence, or a claim of full genuine red.
No additional execution is needed before the writer commits test-only repairs.

The handoff and evidence correction remain authoritative: historical WB-006–008
independent-review/TDD claims stay withdrawn. Fixture-generated domain/CLI red
and green are not continuity evidence for these workbench browser assertions.
This review restores no prior approval and manufactures no historical runs.
Further test changes need semantic continuity review at the exact repaired
test-only revision and eventual production candidate.

## Handoff

Complete the test design and fixture repairs without dropping or reclassifying
any of the sixteen accepted WB-009 obligations. Capture genuine behavior
assertion failures where possible, separately record setup/test defects, then
repair production within accepted ownership. Request fresh candidate-bound
independent review after actual final runs, browser/visual evidence and required
benchmarks. This preliminary verdict must not authorize integration or Accept.
