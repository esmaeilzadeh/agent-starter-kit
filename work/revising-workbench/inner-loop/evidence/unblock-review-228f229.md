# Supplemental narrow blocker-fix review

Decision: **REJECTED**. One blocking readiness race remains.

Reviewer: `/root/review_unblock`. Runtime: Codex. Configured model: `gpt-6.1-sol`; reasoning: high. Actual model and parent model identifiers are unavailable. Review scope is only `46eae34383cb64ae24ce18eff7ff09639f24a1da` → `228f229c2d7eb0587da7abe44f270f82c11d43e8`; no full task or workstream approval is implied.

## Blocking finding

**P1 — Wait for the Workstream rerun before changing Source** (`_ask/ui/benchmark_workbench.py:201`–`205`).

`select_working_model` checks the browser's Workstream input value and immediately selects Source. That input value can update before Streamlit has processed the Workstream change. The app computes Source options/default from the selected workstream on the subsequent rerun; in this detached checkout its workstream-change branch resets `source_id` to `git:agent/revising-workbench`. Selecting `working-tree` on the old Source widget can therefore appear successful to `to_have_value`, then be replaced by the server's workstream default. An input-value assertion is insufficient evidence that this dependent widget is ready.

The actual current-candidate detached NAV run reproduced the problem. `work/revising-workbench/traceability/rwb109/unblock-nav-green.log` records one test, failure after 43.595 seconds, at the retained `Validated inputs` assertion. Its final accessibility snapshot shows:

- Workstream: `revising-workbench`.
- Source: `git:agent/revising-workbench`.
- Committed source at `228f229`, with `EM001_CANONICAL_DEFINITION` because `specs/current/revising-workbench.json` is unavailable in that committed source.

The inspected log SHA-256 is `7c2d6583b5ef8fd2aeb5084e5356fe079d423e57469b3cefd21312b1ee38a1ed`. It reaches the later admission assertion, so the helper's temporary Source value assertion already passed. The log demonstrates the reset; the inter-widget rerun timing explanation is supported by the app's workstream-change/defaulting branch and installed Streamlit widget/session-state behavior.

Required correction: use an observable server-processed Workstream rerun boundary before interacting with the resulting Source widget, then select `working-tree` and require actual working snapshot admission. Retain the independent route/model readiness assertions. Rerun the existing detached NAV case on the resulting exact candidate. An arbitrary delay or weaker assertion would not resolve the ordering requirement.

## Other assessments and limits

Explicitly selecting the working snapshot is appropriate because these callers admit and benchmark working model bytes. The change does not weaken production admission or evidence authority. The legacy `_ask/tests/test_engineering_ui_browser.py` harness, its historical-source refusal paths, and journey assertions are unchanged by this delta. Its reused refusal journeys start through their own `_server` path, so this helper does not force those historical selections back to working tree. The helper also returns before individual new journeys perform later source interactions.

No new tests were launched by this reviewer. The existing coordinator-run detached NAV result was inspected directly. The earlier scoped run `cd850fb6aa79470ead4a694896193577` is not treated as successful validation of this delta. The earlier ledger-recovery assessment is not changed by this Source-selection finding.

This is a supplemental technical fix review only. It is not TaskResult integration approval, whole-workstream semantic or traceability approval, or human acceptance/comprehension evidence. No source, state, pin or TaskResult was edited and no commit was made by this reviewer; only this artifact was written.
