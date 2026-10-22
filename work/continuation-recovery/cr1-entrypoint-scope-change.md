# CR-1 entrypoint-fixture scope amendment

## Trigger

The mandatory aggregate CheckPlan run failed in two existing public-entrypoint
cases after CR-1 added recovery admission: `test_I05_all_normal_entrypoints_reject_omitted_e2e`
and `test_I07_complete_evidence_agrees_across_entrypoints`. Their disposable
consumer commits task-owned source changes after the accepted contract anchor,
then first initializes the task loop. The recovery guard correctly rejects that
history because there is no attempt record.

## Change

CR-1 owns `_ask/tests/traceability_fixture.py` and the mapped
`_ask/tests/test_traceability_entrypoints.py` assertion module. An explicit
fixture option starts the selected task from the accepted anchor before its
candidate source is committed; only CR-T53/54 enable that lifecycle setup. Add exact
regression selectors CR-T53 and CR-T54 for the two affected public-entrypoint
tests, binding the fixture, assertion module, and recovery admission sources.
Keep their omitted-E2E rejection, evidence agreement, integration, and acceptance
assertions unchanged. Do not weaken recovery behavior or change CR-01–CR-08.

Only CR-1 ownership and its test/source mappings change. Intent, specification,
task order, and CR-2–CR-4 ownership remain unchanged. Existing aggregate checks
remain mandatory.

## Decision

Authorized by the user's explicit direction to expand CR-1 integration scope
after the required aggregate gate exposed the fixture incompatibility. This
amendment preserves the previously accepted intent and requirements.
