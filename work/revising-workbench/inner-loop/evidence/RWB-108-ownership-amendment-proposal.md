# RWB-108 narrow ownership amendment proposal

Status: **PROPOSED — not applied or accepted**. Reviewer recommendation: the eleven additions below are a justified minimal ownership expansion for the current RWB-108 design, subject to the explicit authority/tooling decisions below. This proposal does not clear the rejected integration boundary.

Prepared independently by `/root/review_unblock`, runtime Codex, configured model `gpt-6.1-sol`, reasoning high. Actual model and parent model identifiers are unavailable. Inspected checkout: `96f5bcdc58d315475b88d0c438f68abb225124db`. Supporting rejections: `RWB-108-boundary-review-b5794ca.md` and `RWB-108-boundary-review-5dd55fc.md` in this evidence directory.

## Intended change

Expand only RWB-108's accepted `owned_paths` by these exact eleven paths. Retain its eleven existing entries. No wildcard or whole-directory grant is proposed.

```yaml
add_to_RWB-108_owned_paths:
  - _ask/scripts/engineering_model/passages.py
  - _ask/scripts/engineering_model/admission.py
  - _ask/tests/test_revising_context.py
  - .agents/ask/verification/run.py
  - .agents/ask/verification/traceability/cli.py
  - .agents/ask/verification/traceability/evidence.py
  - .agents/ask/verification/traceability/adapters.py
  - _ask/scripts/inner_loop/__main__.py
  - _ask/scripts/inner_loop/driver.py
  - _ask/scripts/inner_loop/evidence.py
  - _ask/scripts/inner_loop/integrate.py
```

The matching RWB-108 ownership row in `work/revising-workbench/plan.md` would receive the same additions. The existing completion evidence stays unchanged. RWB-109 ownership stays unchanged.

The passages/admission seams support the pilot's two exact required specification passages and distinguish implementation delivery Tasks from product Tasks with explicit foreign execution aliases. The context test preserves refusal for a genuinely selected product Task with missing passages. The workflow/inner-loop/verifier entrypoints must carry that distinction consistently through spawn, review, verification and integration. The adapter change binds detached genuine-evidence subprocesses to the retained runtime root. These are specific dependencies of the accepted pilot behavior; their ownership does not authorize unrelated workflow or verifier changes.

## Preserved contract

- Original RWB-108 base: `743309782b5f08f5a46fe03178651e106a7e3150`. Preserve that base and historical state/results; retain the existing single writer and FF-only integration rules.
- Canonical specification, criteria, test cases, scenario/assertion content, executable selectors, runner definitions, source-path obligations and test types remain unchanged by this ownership proposal. Preserve the existing contract identities; acceptance of an amended TaskGraph will produce a new graph/contract identity through the normal authority operation rather than editing an old pin in place.
- Preserve task order and dependencies, including RWB-107 → RWB-108 → RWB-109. RWB-109 remains responsible for successful browser/human demonstration and measured budgets.

Preserve these exact RWB-108 assignments:

| Test ID | Type | Runner | Executable selector |
| --- | --- | --- | --- |
| RWB-MIGRATION | integration | rwb-migration | `_ask.tests.test_revising_pilot.MigrationTests.test_reviewed_adoption_preserves_v1_identity_references_and_evidence` |
| RWB-NEW-CONTRACT | integration | rwb-new-contract | `_ask.tests.test_revising_pilot.MigrationTests.test_new_work_requires_own_spec_graph_review_and_accepted_contract` |
| RWB-READABILITY-BINDING | unit | rwb-readability-binding | `_ask.tests.test_revising_pilot.ReadabilityTests.test_each_answer_and_changed_dependency_control_comprehension_validity` |
| RWB-GENUINE-WB003 | integration | rwb-genuine-wb003 | `_ask.tests.test_revising_pilot.RepresentativeTests.test_required_retained_wb003_result_is_genuine_and_historically_applicable` |
| RWB-MIGRATION-PASSAGES | integration | rwb-migration-passages | `_ask.tests.test_revising_pilot.MigrationTests.test_migration_passage_dependencies_use_real_guarded_entry` |
| RWB-DEMO-PASSAGES | integration | rwb-demo-passages | `_ask.tests.test_revising_pilot.RepresentativeTests.test_required_passages_gate_demo_without_fabricated_success` |

The canonical JSON specification digest recorded in the current plan is `549e490b2e013957fea941921d41d48338d7faca98cf3e98d5baa5cfbf4475a1`. This proposal changes no canonical plan bytes. Neither an existing pass nor this proposal supplies a new accepted contract or execution result.

## Required removal of successor extras

Before RWB-108 integration, restore each path below to its exact bytes at the original RWB-108 base. A path absent at that base must be absent in the corrected candidate tree. Preserve the existing history/evidence; new corrective commits can restore these bytes without rewriting history.

```text
_ask/tests/revising_browser_support.py
_ask/tests/test_revising_browser.py
_ask/tests/test_revising_performance.py
_ask/ui/benchmark_workbench.py
_ask/ui/streamlit_app.py
_ask/ui/workbench_loading.py
_ask/ui/workbench_navigation.py
_ask/ui/workbench_tests.py
work/revising-workbench/workbench-validation.md
.gitignore
_ask/tests/test_engineering_ui_browser.py
work/revising-workbench/handoff.md
```

The first nine paths are explicitly RWB-109-owned. The remaining three are the dependency-environment exclusion, legacy browser support and mixed-task handoff identified in the boundary rejection. Their restoration is an integration prerequisite, not a claim that the successor changes are technically wrong. RWB-109 can introduce its own implementation later under its existing scope. A successful browser run does not waive this required final-tree separation.

## Explicit authorization metadata handling

`work/revising-workbench/intent-confirmation.json` is outside the source ownership additions and outside the runtime evidence exception. Preserve its exact human response, `comfirm changing intent`, and require its stored intent digest to match the current `intent.md`; that match was observed during proposal preparation. Treat this single path as separately reviewed coordinator authorization metadata associated with the already confirmed intent. Approval of this amendment must explicitly acknowledge that treatment. It supplies no general exemption for `work/**`, changes no What/Why, and grants no implementation authority by itself. Do not restore a stale confirmation merely to satisfy a source ownership check, or invent a new human response.

The ordinary inner-loop evidence/state/result exceptions retain their existing definitions. Amendment review artifacts and authority records must remain attributable. They cannot be used to hide additional source or workstream documents from boundary review.

## Remaining decisions and acceptance conditions

1. **Independent exact amendment review and normal acceptance are still required.** Apply no plan/TaskGraph/pin changes from this proposal alone. Any later amendment must preserve the original base, six assignments above, canonical specification/plan, dependency order and integrity gates, and use the normal reviewed contract publication. Respect the existing restriction on amending a running writer through an explicit audited transition; do not initialize a replacement task/base.
2. **Pinned verifier compatibility is unresolved.** `_ask/scripts/inner_loop/evidence.py:snapshot_runner` loads verifier code from the original task base. That base's `verification/run.py` still supplies `selected_execution={work_id, task_id}`, while the new model lacks a product alias for delivery task RWB-108. The proposed candidate verifier entrypoint uses `delivery_task_id` instead. This static mismatch requires an authority-preserving compatibility/tooling decision and eventual execution; ownership expansion alone does not make candidate verifier changes execute in the trusted base gate. Keep the recorded base, base runner/import identity and existing CheckPlan/candidate-integrity checks intact. If compatibility cannot be achieved within those constraints, stop for a separate scoped tooling decision. This proposal does not authorize candidate verifier self-validation or changing the runner pin.
3. **Changed-seam coverage requires a concrete review.** The standalone `test_delivery_scope_without_product_alias_does_not_select_foreign_task` in the newly owned context test file is outside the six existing RWB-108 selectors. Ownership approval alone does not make it assigned completion evidence. Retain the six identifiers/types/selectors and require a later test review to show that actual relevant entrypoint/alias/refusal behavior is exercised by the existing accepted obligations and required checks; a manually reported extra pass is insufficient.
4. **Fresh whole-task boundary and technical evidence remain required.** The corrected candidate's base diff must contain no successor extras, every remaining implementation path must have accepted ownership, the exact authorization metadata treatment must be recorded, and the unchanged task obligations must pass through the normal gate. Obtain a fresh complete-task independent source/test review and TaskResult-bound decision. Prior narrow unblock approvals and previous candidate results do not supply that approval.

This proposal is limited to preparing the ownership decision and its prerequisites. It changes no accepted plan, TaskGraph, canonical specification/test plan, pin, production source, task state or TaskResult. No tests were run, no commit was made, and no implementation or integration was started.
