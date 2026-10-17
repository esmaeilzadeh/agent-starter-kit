# Supplemental rerun-barrier review

Decision: **APPROVED** for this narrow technical correction. No blocking findings in the reviewed delta. This supersedes the specific readiness-race finding against `228f229`; that earlier rejection remains an accurate record of the prior candidate.

Reviewer: `/root/review_unblock`. Runtime: Codex. Configured model: `gpt-6.1-sol`; reasoning: high. Actual model and parent model identifiers are unavailable. Immutable reviewed range: `228f229c2d7eb0587da7abe44f270f82c11d43e8` → `e514444977dcfd09cfff6114ac2e45251378018e`. Only `_ask/ui/benchmark_workbench.py` changes in this delta.

## Assessment

The new `_select_model_option` addresses the dependent-widget ordering defect. It first requires the app to be idle, observes the app's script-state attribute before changing the widget, waits for an observed rerun to finish, and then verifies the resulting widget value. Workstream and Source use this operation sequentially, so Source is selected only after the Workstream rerun has applied its options/default. An already-correct value returns after the idle check without waiting for a rerun that would never occur.

The MutationObserver handles both ordinary and fast transitions. A non-idle current attribute marks a started rerun; when multiple changes arrive in one observer batch, `attributeOldValue` retains an intermediate non-idle value even if the current value is already `notRunning`. Only an observed start followed by idle marks completion. The observer is limited to the script-state attribute, and `finally` disconnects it and removes the temporary window state after success or failure. Installed Streamlit exposes `data-test-script-state` on `stApp` and defines the idle value as `notRunning`, matching this harness dependency.

The correction preserves the independent `Validated inputs` check in `browser_session` and benchmark route/title/status assertions. It adds no arbitrary sleep, changes no production app state rules or admission checks, and leaves legacy historical-source refusal journeys and their separate startup harness unchanged. Source, state, TaskResult, accepted contract and authority data are outside this delta.

## Observed validation and limits

The coordinator-run detached NAV rerun has completed successfully. `work/revising-workbench/traceability/rwb109/unblock-nav-rerun-barrier.log` records `test_direct_story_task_standalone_shared_back_and_exact_counts` passing: one test in 14.999 seconds, `OK`. The inspected log SHA-256 is `de3506c47a930fc82f08db9fa2544c2fdd210f211bb37b73d85ac6ff873c10e3`. This reviewer inspected that existing result and ran no additional tests. The previous candidate's failing NAV log is not reused as successful evidence.

This establishes the observed detached startup/navigation correction for the reviewed candidate. It does not claim a completed broader RWB-109 suite, TaskResult integration, whole-workstream semantic/traceability approval, RWB-108 completion, or human comprehension/acceptance. The harness intentionally depends on Streamlit's exposed test attribute and must retain its normal validation when that dependency changes. No source/state edits or commits were made by this reviewer; only this artifact was written.
