# Independent review: WB-001

## Model

- model: gpt-6-astra
- runtime: codex
- parent_model: gpt-6-luna
- reviewer: /root/review_wb001
- Human model choice and same-family second confirmation were supplied before this review.

## Scope

- work_id: structured-agentic-environment
- task_id: WB-001
- base_sha: b1f8b49fe4c94c993deb1d65ea59a04303fc66df
- candidate_sha: 7c75164647fec43ba1ac5908ae16038342932511
- TaskResult: work/structured-agentic-environment/inner-loop/results/WB-001.json
- Accepted contract SHA: b755d83141b030d2d101e9fd9f37b51e28a8ef26
- spec_digest: f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb
- plan_digest: 572d2c3dda82e69a49d78b1320ec35835f4f153137e62c35f41af678ad106330

Authority inspected: accepted task graph/scopes, current specification revision 3, plan, workbench-design.md relationship authority, implementation handoff, independent planning approval, candidate implementation and changed tests, retained task reports and logs. `./ask inner-loop status structured-agentic-environment` identifies WB-001 as the current running writer.

This decision covers the current writer's projection and 25 assigned cases. It does not approve subsequent task behavior or final workstream completion.

## Steering boundary

boundary: ok

`git diff --name-only b1f8b49fe4c94c993deb1d65ea59a04303fc66df 7c75164647fec43ba1ac5908ae16038342932511` returned exactly:

- _ask/scripts/engineering_model/projection.py
- _ask/scripts/engineering_model/workbench.py
- _ask/tests/test_engineering_workbench.py

All match WB-001 owned paths. No extras or required out-of-boundary remediation identified. The runtime state and submitted result are distinct from this committed source diff. Review changes no implementation and commits nothing.

## Findings

### R1 — Canonical criterion membership is omitted from relationship joins (blocking, high)

Location: `_ask/scripts/engineering_model/workbench.py:56`, especially lines 85–92 and 104–108.

`scenario_ids_by_case` is populated exclusively from Engineering Model `covers` edges. The accepted test plan's `criterion_ids` are never read. Canonical test cases are therefore disconnected from their recorded model scenarios unless each case also has a redundant model test node and `covers` edges. Task-to-scenario and secondary scenario-mediated task/test links inherit this omission.

The accepted design's relationship table explicitly requires scenario-to-test joins from canonical test criterion IDs and model covers references, and scenario-to-task fallback from the criterion membership of a task's owned tests. WB-001 is responsible for those joins; missing duplicate model records do not mean canonical membership is missing.

Concrete counterexample executed in a disposable WB-001 fixture: remove the `case-second` model test node and its covers edge while preserving CASE-2's canonical `criterion_ids: [C2]`, scenario s2's `specs/current/pilot.json#C2` reference and task-b's CASE-2 ownership. Actual CASE-2 projection has `scenario_ids: []`, task-b has `related_scenarios: []`, and shared CASE-1 loses its secondary task-b association. Expected canonical membership is s2 with the task/test relationship labeled through scenario coverage. No repository source or pilot data was mutated.

The committed real pilot also demonstrates this: MV-graph references EM-001 and is owned by WB-001, but its projected `scenario_ids` is empty even though `representative-model-is-accepted` references the same current-work EM-001 criterion. The existing fixture duplicates every local test's criterion membership in model covers edges, so its passing assertions do not distinguish this incorrect implementation.

Suggested fix: join current-work test-plan criterion IDs to scenario canonical references using qualified specification/work identity; union those associations with legitimate recorded covers edges, deduplicate, and derive task and secondary links from that union. Add a discriminating case without the duplicate model test node, including a foreign-work reused criterion/test identity that must not join.

### R2 — Recorded associations are dropped for model-only tasks (blocking, medium)

Location: `_ask/scripts/engineering_model/workbench.py:127`, especially lines 133–139.

The graph-task path retains `explicit_scenarios_by_task`, but the model-only fallback unconditionally emits `related_scenarios: []`. A real recorded implementation-to-task and implementation-to-scenario association is discarded solely because the task lacks a historical task graph row. It then also disappears from scenario-mediated test navigation.

Concrete counterexample executed in a disposable fixture: retain model-only `legacy-task`, add `implementation -> legacy-task` with type implements, and keep the existing `implementation -> s3` implements relation. The earlier loop records the association, but the emitted legacy-task still has `related_scenarios: []`. Expected: preserve s3 as `recorded-implementation` while retaining `status: not-recorded`, `record_source: engineering-model` and no fabricated runtime/completion evidence. The accepted plan requires legitimate many-to-many links and separately identified model-only pilot tasks; absence of runtime history is not absence of recorded semantic relationships.

Suggested fix: preserve explicit scenario associations in the model-only fallback and cover them with a regression assertion while proving their presence cannot assert integration or completion.

## Test assertions, counterexamples and continuity

The changed test inventory is exactly the three new cases in `_ask/tests/test_engineering_workbench.py`; no foundation test was changed or excluded. The candidate adds workbench.py and changes projection.py. No changed Python test is outside the accepted WB-001 mapping.

| Case | Assertion assessment and counterexample |
| --- | --- |
| WB-relations (EM-008/unit) | Asserts two owners, shared scenario IDs, one secondary task link and two deduplicated tests. Insufficient for canonical-only memberships: R1 passes these assertions. The foreign test reuses a scenario already covered locally, so accidental foreign coverage is not distinguishable by the current expected set. |
| WB-task-history (EM-008 and EM-010/integration) | Asserts graph title/outcome/paths, explicit graph-task scenario association, planned missing-runtime status, labeled model-only record, integrated and blocked runtime statuses. Model-only explicit relationships are untested: R2 passes. Only an empty dependency list is asserted; a nonempty dependency assertion would strengthen the accepted metadata checks. |
| WB-story-context (EM-008/unit) | Asserts recorded story membership s1/s2 and unassigned s3, without manufacturing a story for task-a. Adequate for the implemented story slice. |
| MV-valid | Accepts a broad typed model and rejects absent intent/test coverage. Retained regression. |
| MV-graph | Checks precise errors for duplicate/missing identities, illegal relationships, cardinality and cycles. Retained regression. |
| MV-fields | Rejects malformed types/fields, options, resolution/history and references without repairing input. Retained regression. |
| MV-refs | Rejects unknown/escaping references and malformed canonical definitions; concurrent referenced changes cannot get a valid receipt. Retained regression. |
| ME-decision | Checks attribution, revision, blocker propagation, reopening/history and retired prerequisites. Retained regression. |
| ME-revise | Checks transitive invalidation and preserved prior resolutions across edits. Retained regression. |
| ME-reject | Invalid and stale commands preserve bytes and expose diagnostics. Retained regression. |
| ME-race | Competing CAS writers yield one winner, one stale loser and one revision increment. Retained regression. |
| EV-real | Actual evidence identities/assertions/outcomes and read-only inspection are checked; tampered logs/receipts/review/source fail current completion. Retained regression. |
| EV-missing | Missing/malformed evidence and historical candidates retain unavailable/invalid/historical meaning; historical output tampering is detected. Retained regression. |
| MP-shared | JSON/Markdown retain model IDs, references and snapshot digest without introducing completion, and reject invalid focus/current input. Retained regression; does not assert parity of the new workbench-only fields. |
| MC-journey | CLI inspect, attributed resolve, reload/unblock and invalid edit preservation. Retained regression. |
| DG-pre | Invalid prestate prevents invoking the action. Retained regression. |
| DG-post | Invalid candidate preserves published stable generation. Retained regression. |
| DG-refs | Referenced specification changes invalidate admission. Retained regression. |
| DG-events | External changes and missed observer events fail freshness checks. Retained regression. |
| DG-parity | Cached and full validation agree across changed input. Retained regression. |
| DG-publish | Concurrent multi-file publication/recovery yields one coherent winner. Retained regression. |
| DG-bootstrap | Initial publication requires validated input. Retained regression. |
| ME-batch | Atomic node/edge and lifecycle batches retain validity and semantic history. Retained regression. |
| DG-success | Successful guard ordering and state identities are checked. Retained regression. |
| DG-entrypoints | Public mutators cannot bypass shared admission. Retained regression. |

Criterion/type assessment: retained cases exercise WB-001's foundation assignments under EM-001–004 and EM-007. New WB cases cover the assigned EM-008 unit/integration projection slice and EM-010 integration metadata slice, with the gaps above. Required UI/e2e coverage under EM-005–006 and EM-008–012 remains assigned to later tasks. Passing task cases do not establish all criterion/type obligations for final workstream completion. Existing foundation tests are unchanged regressions; this review invents no historical behavior-red evidence for them.

## Retained execution evidence

Red run: `work/structured-agentic-environment/traceability/runs/ec50d7d6193f4b72b79a3d8f975666d4/results.json`.

- source_sha: c8d97cb89270da80bb8e34756745da7e9ac3e6b0
- phase red, collection_status ok, exit_code 1
- 25 recorded cases: 22 passed; WB-relations, WB-task-history and WB-story-context failed with failure_kind behavior_assertion.
- Exact log: `work/structured-agentic-environment/traceability/runs/ec50d7d6193f4b72b79a3d8f975666d4/2c1988e3c65445e6a98a7342397284c2.log`
- Verified log SHA-256: ad8b2de31f374d579f1d0569cab1089fb3a58b033a5a706b9b88a51baed622c9
- Failures are actual assertions that the new workbench projection is absent, not import/collection errors.

Final green run: `work/structured-agentic-environment/traceability/runs/bc215f3cafbc4b2c9bb5c517a1df1804/results.json`.

- source_sha: 7c75164647fec43ba1ac5908ae16038342932511
- phase final_green, collection_status ok, exit_code 0
- All 25 recorded cases passed, matching the log's 25 tests / OK.
- Exact log: `work/structured-agentic-environment/traceability/runs/bc215f3cafbc4b2c9bb5c517a1df1804/02ca046c983048ee919305cdf7aee7cf.log`
- Verified log SHA-256: bd436f8e706fda746085657ee68a0b02c0f3da1330861c3016e2da6b763c87ab

Both reports bind the accepted spec/plan digests above and task WB-001. Every reported case source digest was independently compared with its committed source using git show; no mismatch. The three new tests have identical bytes at red and final green, SHA-256 464d33ac8eff78af2e8df9019945bb5de50e0588e5e78249be96f48e9c8adeb1. The TaskResult commands/output agree with these reports. This is valid TDD continuity for the implemented assertions; it does not close the uncovered counterexamples.

## Suggested fixes

Address R1 and R2 within WB-001 owned paths, add discriminating assertions for the demonstrated counterexamples, and submit a new committed candidate with attributable execution evidence for fresh independent review. Strengthen foreign-work isolation by using a distinct foreign-only scenario or association whose accidental addition changes the expected result.

## Residual risks

No completion is inferred from a declared done lifecycle; missing runtime records are planned/not recorded, and integrated status remains separately attributed to task-state. Graph scopes and model test references use current-work identity checks. Branch/revision source selection, detailed integrity-bound evidence, UI journeys, performance and full Verify belong to later tasks and final gates. No review or integration authority is conferred by this Markdown alone; the coordinator must bind this decision to the exact candidate and TaskResult.

## Review verdict

verdict: REJECTED

boundary: ok

R1 and R2 must be corrected before WB-001 integration. No implementation changes or commits were made by this reviewer.
