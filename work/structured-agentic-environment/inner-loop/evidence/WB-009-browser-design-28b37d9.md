# WB-009 preliminary browser design re-review

Verdict: **REJECTED / INCOMPLETE TEST DESIGN**. This does not approve candidate
integration, TDD continuity, the full WB-009 task or workstream completion.

Reviewer: `/root/review_wb009_tests`, independent child of `/root`.
Runtime: Codex; resolved reviewer binding `gpt-6.1-sol`, high. Parent model was
not supplied to this child. Exact reviewed commit:
`28b37d9271243b7768b0f40f96614a6d473055eb`.
Detached snapshot: `/tmp/ask-wb009-browser-review-28b37d9`.
No shared production/test source edits or commits were made by this reviewer.

Scope and authority remain the first report's four browser obligations, accepted
test plan, specification revision 3, plan, WB-009 handoff and evidence correction.
Compared the new immutable browser bytes against report
`WB-009-browser-design-3caf633.md`. All sixteen WB-009 assignments and accepted
ownership are preserved; performance and the final candidate review are separate.
This checkpoint changed the two owned browser modules and test requirements,
plus coordinator evidence artifacts. No spec or accepted pin changed.

## Findings and required fixes

1. **P1 — Legacy evidence observations were removed rather than repaired.**
   `_ask/tests/test_engineering_ui_browser.py:89` replaces the previous available,
   unavailable-current-candidate and historical-candidate journey with test/source
   captions. `historical` returned at line 70 is now unused. The accepted
   `UI-browser` scenario explicitly requires historical/missing inspection and
   canonical assertions/provenance. Restore all three evidence observations on
   the qualified U result before the linked-spec amendment. Assert actual passed
   outcome and work/test/run/contract/candidate provenance, unavailable newer
   HEAD, then retained historical evidence explicitly tagged historical. Source
   text is not evidence outcome/provenance.

2. **P1 — Gitless evidence assertion was weakened to generic debug text.**
   `_ask/tests/test_engineering_ui_browser.py:176` selects a test rather than its
   result, and lines 181–183 check debug field labels and a generic `unavailable`
   value. The previous actionable `Git evidence inspection is unavailable`
   assertion was removed. Restore selected CASE-1 result inspection, an actionable
   Git-evidence reason, and expanded debug with usable inspect commands/artifact
   context, preserving the fatal-Git-output exclusion. The accepted scenario
   requires selected test/result detail and expanded debug, not merely a missing
   Git revision field.

3. **P1 — Summary filter assertions can pass without opening the filter.**
   `_ask/tests/test_engineering_workbench_browser.py:222` now checks scenario
   outline buttons, which are present before clicking `View scenarios`. It no
   longer checks any filtered record set. Task/decision text assertions at
   lines 225–235 similarly do not compare exact row identities/counts to metrics.
   Assert the active filter and its exact Open-record row IDs, independently of
   the permanent outline and overview story rows. Expected sets for this fixture:
   scenarios `{scenario, scenario-other}`, tasks `{build, review-build}`, blocked
   `{review-build}`, decisions `{choice}`. A no-op summary callback must fail.

4. **P1 — Test source oracle and result identity remain incorrect/incomplete.**
   `_ask/tests/test_engineering_workbench_browser.py:249` requires `test_behavior`,
   but the actual Consumer source contains `test_app.Cases.test_unit` for U and
   `test_cli` for E. This is a wrong oracle, not an implementation requirement.
   Correct it to the plan's qualified U method and inspect its exact source.
   Lines 254 and 90 of the legacy module use `nth(1)` for generic result buttons;
   the legacy selected-test postcondition improves safety but position is still
   brittle. The hierarchy case still lacks explicit case/run/contract identity;
   alternate branch result selection at line 270 still uses the first generic
   result button. Assert positive selected work/test/candidate/source identities
   and exact expected unavailable state on that branch. The full chain now opens
   story/scenario/Build/test, an improvement, but ancestor IDs and contextual
   related links are not asserted. Shared-test deduplication remains untested.

5. **P2 — Recorded task-result path is still inconsistent.**
   `_ask/tests/test_engineering_workbench_browser.py:157` writes `results/build.json`
   with corrected task ID and real fixture SHA, but line 153 still points `build`
   to `results/WB-001.json`, which is not written. Correct the path and assert the
   selected completed task's matching result identity. Do not infer verified
   completion from a dangling result path or integration status alone.

6. **P2 — Accessibility coverage improved but still misses required states.**
   Lines 305–359 retain Tab/Enter inspection at both widths, add large-title
   contrast, compose alpha/ancestor background for focus, and open debug with
   keyboard. Lines 369–374 now type attributed input through keyboard. Retain
   those improvements. Visible focus and its ratio are still asserted only on
   the first scenario button, not primary task/test/debug/decision controls.
   Status contrast remains optional at line 357; assert the required textual
   state exists. The decision flow runs only after the width loop at 1440;
   overflow is checked only at 390 after submission rather than on source/debug
   and other primary routes. The focus calculation checks the outer parent
   background, not both adjacent resolved colors, and chooses outline color
   whenever outlineStyle is not none even if only a box shadow supplies the
   visible indicator. Match the measured color to the actual visible indicator.
   Verify known expander state at each width: the same keyed debug expander may
   retain its expanded state, so blindly pressing Enter twice can close it on the
   second width. Require actual keyboard expansion and visible content each time.
   Persist the chosen option ID as well as actor/rationale and task consequences.

7. **P2 — No-write checks do not cover publication identity.**
   The stale-submit comparison at legacy lines 118–132 correctly compares
   model/spec/plan bytes after external mutation, then open decision/history.
   Add the published pointer/generation digest comparison to substantiate no
   publication, and retain the fresh-session blocker consequence at lines 146–153.
   Foreign browsing at hierarchy lines 277–279 correctly compares HEAD and refs,
   but its protected byte set still omits spec/source/task/publication state.

## Selector and observation guidance

`render_outline` already supplies keys `route:result:U`, `route:test:U` and
`breadcrumb:<id>`. Prefer those identity-bound controls over generic result labels
and ordinal selection. Streamlit key wrapper attribute selectors such as
`[class~="st-key-route:result:U"]` avoid colon CSS escaping; verify the actual
rendered wrapper once, then select its button. Always assert selected U and its
qualified source/result identity afterward.

`workbench_overview._render_filter` gives each filtered row an `Open record`
button keyed `overview:filter:open:<kind>:<id>`. Collect and compare that precise
set, assert `Clear filter`, and compare metric counts. This distinguishes summary
rows from outline and story-overview controls. If native key classes are not
exposed as expected, scope the actual right detail column and the subsection
after its exact filter heading, then inspect its Open-record rows/captions.

`evidence_workbench()` returns a retained successful candidate in `historical`
(`consumer.sha`); its current HEAD is a newer model adoption without corresponding
execution. Capture expected work/test/accepted-contract/run identities from the
fixture before launch. Select U result and require retained pass, unavailable
current HEAD, and explicitly historical retained-candidate inspection before
continuing to stale edit. Missing UI controls should remain behavior assertions
where they are required by the accepted journey, rather than be deleted because
the current result renderer does not expose them.

## Independent execution and limits

Executed the immutable snapshot directly, without monkeypatching or source edits:

```sh
ASK_BROWSER_CHANNEL=chrome /tmp/ask-wb009-venv/bin/python -m unittest discover -s _ask/tests -p 'test_engineering*browser.py' -v
```

Environment: Python 3.12; Streamlit 1.59.2; Playwright 1.63.0; PyYAML 6.0.3;
installed Chrome 142.0.7444.162. The new requirements declare PyYAML and both
modules honor explicit Chrome channel, resolving the earlier dependency/binary
setup issues. Result: **four failures, zero errors, four cases in 34.003s**.
Log: `/tmp/ask-wb009-browser-review-28b37d9.log`.

| Case | First observed failure | Interpretation |
| --- | --- | --- |
| UI-browser-gitless | line 176, missing Behavior assertion route | Fixture admission/projection or route behavior needs diagnosis; no result/debug proof reached |
| UI-browser | line 93, missing Selected source path: test_app.py | Selected U reached; source metadata/rendering behavior gap; stale/persistence assertions not reached |
| WB-browser-accessibility | line 330, focus contrast 2.3889570666987545 < 3 | Concrete accepted focus threshold failure under the implemented compositing algorithm; confirm indicator/color selection before recording as genuine red |
| WB-browser-journey | line 248, missing Selected source path: test_app.py | Story/scenario/Build/test traversal reached; required source missing; later wrong test_behavior oracle and evidence/foreign-source assertions not reached |

No import, server-launch or browser-binary setup error occurred in this run.
These assertion failures are useful diagnostic observations, not automatic
approval of all test design or continuity. The incorrect method oracle, deleted
evidence checks, missing path identity and false-pass filters must be repaired
before final continuity assessment. No final green or all-case red is claimed.
Earlier WB-006–008 evidence corrections remain in force. Full browser/visual
checkpoint, sixteen-case task evidence, performance, Verify and candidate-bound
independent review remain outstanding.
