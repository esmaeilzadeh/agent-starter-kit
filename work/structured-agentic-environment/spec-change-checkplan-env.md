# Specification Change Proposal: isolate synthetic risk checks from CheckPlan context

## Current specification

The accepted workbench plan is pinned to a nine-task sequence. WB-001 owns only its listed projection modules and tests. Its verification uses the accepted unittest adapter and CheckPlan static checks. The plan states that any necessary runner-binding change requires independent review and a new pin before use.

The current verification environment sets `ASK_WORK_ID` for static checks. The `test-sync-runtime-agents.sh` check also runs synthetic risk-selection examples by setting `ASK_RISK=HIGH`, then expects the generated Review model to reflect HIGH risk. When a workstream ID is present, `sync-runtime-agents.py` correctly resolves the workstream's configured risk first, so this test observes MEDIUM instead. The exact test passes without `ASK_WORK_ID` and fails with it. WB-001's behavior checks and independent review pass; candidate integration stops at this static check.

## Proposed change

Amend the accepted plan's verification contract to permit an explicit test-local environment reset for synthetic CheckPlan examples. Update `_ask/tests/test-sync-runtime-agents.sh` so its `ASK_RISK=HIGH` and `ASK_MODEL_07_REVIEW=thinking` invocations run with `ASK_WORK_ID` unset. Preserve production risk precedence, CheckPlan's normal workstream context, WB-001's behavior contract, and all existing acceptance criteria.

Treat this as a small verification-harness support change required to unblock WB-001 candidate integration. Independently review the exact changed test and plan amendment, then accept and pin the amended contract before using the change in a candidate run.

## Why the change is needed

The static check combines two distinct inputs: inherited task context from CheckPlan and explicit synthetic inputs used to test runtime model selection. The inherited `ASK_WORK_ID` changes the behavior under test and makes the expected HIGH-risk assertion invalid for a MEDIUM-risk workstream. Resetting only that variable in the synthetic invocations restores the test's stated purpose without weakening the assertion or altering runtime behavior.

## Impacted artifacts

- `work/structured-agentic-environment/plan.md`: clarify this narrow verification harness exception and list the support file under WB-001's bounded verification support.
- `work/structured-agentic-environment/inner-loop/tasks.yaml` and `test-plan.json`: record the support ownership/obligation if required by the accepted contract validator.
- `_ask/tests/test-sync-runtime-agents.sh`: clear only `ASK_WORK_ID` for the two synthetic model-selection invocations.
- New plan review and traceability acceptance evidence for the amended exact contract.

No production code or model precedence changes are proposed. No acceptance criterion IDs or product behavior change.

## Impacted workstreams

Only `structured-agentic-environment` WB-001 candidate integration. Later tasks continue to use the amended contract. No other workstream or branch is proposed.

## Migration / transition notes

Keep the rejected candidate review and the first integration failure as historical evidence. Preserve WB-001's approved review for candidate `69cfc37ff6b0d8264f0200c6a17668f3efc3e288`, but bind any new integration attempt to the amended plan revision and a new candidate run. Do not edit the accepted plan, task graph, test plan, or test harness until this proposal is confirmed and the amendment is independently reviewed and pinned.

## Acceptance criteria for the change

1. With CheckPlan's `ASK_WORK_ID` present, the static sync-runtime check passes because each synthetic invocation explicitly removes that inherited context.
2. The test continues to assert the HIGH-risk model choice and explicit Review override behavior.
3. Runtime workstream risk precedence remains unchanged.
4. WB-001 remains `running` until the amended candidate integration succeeds; WB-002 does not start before then.
5. The amended exact contract receives independent review and a new traceability pin before the harness change is used.

## Decision

Approved by the human in chat on 2026-10-09. The accepted plan/task graph are being amended, pending independent review and a new traceability pin. No production or test implementation has been changed by this proposal.
