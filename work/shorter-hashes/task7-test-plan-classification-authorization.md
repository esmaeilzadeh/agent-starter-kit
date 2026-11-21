# Task 7/2 test-plan classification authorization

This scoped authorization changes only `work/shorter-hashes/test-plan.json` case `7/2` from `change_kind: new` to `change_kind: regression`.

The user explicitly authorized the Red-gate exception: “The human has explicitly authorized ignoring failures to produce Red; this is the precise gate they waived.” Existing run outcomes remain unchanged. The mapped 7/2 behavior passed on the authenticated pre-Task-7 baseline candidate; an independent plan review assessed the classification decision at 96% confidence and concluded that `regression` accurately describes the existing behavior covered by this case. Its passing result remains a Green guard and is not relabeled as Red.

No intent, specification, acceptance criterion, scenario, expected assertion, runner, source binding, implementation, or other test classification is changed. Task 7 attempt 1 remains interrupted and its candidate-bound TaskResult and review/run evidence remain preserved. This authorization permits only this test-plan classification correction, subject to independent exact-plan review and the supported plan-acceptance registration before Task 7 resumes.
