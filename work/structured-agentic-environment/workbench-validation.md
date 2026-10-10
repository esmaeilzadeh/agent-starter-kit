# WB-009 workbench validation

## Legacy UI continuity

The AppTest cases keep their existing `case_id` methods and behavioral scope while moving navigation from the removed `workbench_section` selector to the connected Epic → Story → Scenario → Task → Test → Result / Evidence outline.

| Existing journey | Current route and preserved behavior |
| --- | --- |
| Historical/current evidence candidate | `result:U`; inspect a current unavailable candidate and a retained historical candidate without presenting either SHA as the result identity |
| Planned test source | `test:CASE-1`; show qualified test identity, planned assertion, source path and source assertion in the selected detail |
| Decision from overview | Open the originating decision from the Epic attention list and retain the guarded decision form |
| Overview hierarchy | Keep source and evidence lazy at the Epic; show delivery counts and linked Test/Result routes, then show source after opening the Test route |
| Result loading/debug | Keep overview evidence scans deferred; load selected Result evidence explicitly and explain Git revision versus snapshot digest |
| Nested evidence warnings | Load selected Result details and keep repeated nested controls addressable; migration diagnostics remain warnings |
| Empty collections | Show clear no-task/no-scenario states from the Epic and an empty filtered summary |
| Gitless evidence | Keep the model usable and show an actionable unavailable-evidence state without Git fatal output |
| Decision persistence | Submit through captured decision form keys; preserve actor/rationale and unblock state across a new AppTest session |
| Stale decision form | Reject incomplete input and a form captured before a referenced-spec-only change without changing the published decision; explicit refresh permits the valid resolution |

Browser case IDs remain assigned to `test_engineering_ui_browser.py`; their route and accessible-control migration is pending the WB-009 production ownership amendment. No case IDs or planned outcomes were removed here.

## AppTest red checkpoint

At the red revision before production repair, the targeted command was:

```text
PYTHONPATH=_ask/tests python3 -m unittest -v test_engineering_ui
```

Result: 10 tests collected, 2 passed, 8 failed with assertion failures. The two passing cases cover empty hierarchy states and opening a decision from overview attention. The Epic overview already exposes Test and Result route buttons, task/scenario counts, and keeps source content lazy. The failures are current behavior gaps reached through successfully loaded AppTest sessions: the selected Result has no evidence-candidate control or lazy result-load action; selected Test details lack qualified source/assertion data; selected Result details do not expose loaded migration-warning or Gitless evidence states; and resolved decisions disappear from the outline after persistence, preventing history inspection in a new session. The stale-form case performs a linked-spec-only change, confirms the model and decision stay unchanged and the stale submission makes no write, then confirms the valid post-refresh resolution; its remaining assertion failure is the missing resolved-history route.

The first combined baseline attempt also entered the old browser test and stalled waiting for its obsolete `Workstream in current branch` selector; it was interrupted before browser behavior ran. This is setup evidence only and is not counted as a browser regression result. Browser migration and its own red capture remain pending.
