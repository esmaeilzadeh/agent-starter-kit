# RWB-108 boundary review

Verdict: **REJECTED**. Boundary: **glob_too_narrow**, with separately identified **extras**. Candidate `b5794caaf0391864ef96ad48fb9448dd4fb34d25` cannot honestly receive `APPROVED / boundary=ok` under the current accepted RWB-108 ownership.

Reviewer: `/root/review_unblock`; runtime Codex; configured model `gpt-6.1-sol`, reasoning high. Actual model and parent model identifiers are unavailable. This independent assessment covers ownership/integrability only, comparing recorded base `743309782b5f08f5a46fe03178651e106a7e3150` to exact candidate `b5794caaf0391864ef96ad48fb9448dd4fb34d25`. It does not supply semantic, test-adequacy, TDD, TaskResult, integration or human acceptance approval. No tests were run.

## Rule applied

`.agents/ask/stages/07-review.md` requires matching the current writer's changed paths against its accepted `owned_paths`: unnecessary outside paths are `extras`; required outside paths mean `glob_too_narrow` and blocked. `_ask/policies/delegation.md` prohibits silent scope expansion and requires escalation for architecture/domain/API changes. Passing execution and earlier narrow fix approvals do not amend ownership. RWB-109 explicitly depends on RWB-108.

There are 49 changed paths. RWB-108's accepted owned paths are identical at the supplied base and candidate. Eleven changed paths match RWB-108, nine match successor RWB-109, eleven additional implementation/test paths are necessary seams for the current RWB-108 implementation, fourteen are operational evidence/state/result paths, and four are additional nonruntime paths discussed below.

## Within accepted RWB-108 ownership: 11 paths

- `_ask/docs/engineering-model.md`
- `_ask/scripts/engineering_model/__main__.py`
- `_ask/scripts/engineering_model/actions.py`
- `_ask/scripts/engineering_model/migration.py`
- `_ask/scripts/engineering_model/readability.py`
- `_ask/scripts/engineering_model/workflow.py`
- `_ask/scripts/model.sh`
- `_ask/tests/test_revising_pilot.py`
- `work/revising-workbench/engineering-model.json`
- `work/revising-workbench/migration-review.md`
- `work/revising-workbench/representative-story.md`

These paths implement the assigned migration, pilot registration, representative gates, comprehension binding and documentation. This classification alone is not implementation approval.

## Required outside seams: glob_too_narrow

- `_ask/scripts/engineering_model/passages.py`: the representative Task selects two required specification passages; `required_task_passages` now permits multiple available spec passages while retaining exactly one plan selection. The same file adds explicit delivery-task alias resolution.
- `_ask/scripts/engineering_model/admission.py`: threads delivery-task selection into admission so an implementation delivery scope without a product alias does not accidentally select a foreign product Task.
- `_ask/tests/test_revising_context.py`: regression coverage for that distinction and preservation of refusal when an explicit product alias requires missing context.
- `.agents/ask/verification/run.py`
- `.agents/ask/verification/traceability/cli.py`
- `.agents/ask/verification/traceability/evidence.py`
- `_ask/scripts/inner_loop/__main__.py`
- `_ask/scripts/inner_loop/driver.py`
- `_ask/scripts/inner_loop/evidence.py`
- `_ask/scripts/inner_loop/integrate.py`

The seven entrypoint/plumbing paths above carry the new delivery-task selector through spawn, review, verify and integration. They are necessary to the current implementation's distinction between this workstream's delivery Tasks and the foreign historical WB-003 execution represented in its product model. They are outside RWB-108's accepted boundary despite being motivated by the pilot. Changes to these shared workflow/verifier APIs require explicit accepted ownership/tooling treatment; calling them routine fixes does not authorize them.

- `.agents/ask/verification/traceability/adapters.py`: exports the runtime root to detached test subprocesses so genuine retained evidence can be inspected outside the candidate checkout. This is necessary to the current detached genuine-evidence implementation, but changes shared execution tooling outside ownership. The accepted plan states that runner changes require a scoped tooling amendment. Its necessity makes the boundary too narrow, rather than making the path implicitly owned.

This section classifies necessity for the current design; it does not independently approve the changed semantics or an ownership amendment.

## RWB-109 work present prematurely: extras for RWB-108

All nine paths below match RWB-109's explicit ownership and no RWB-108 ownership:

- `_ask/tests/revising_browser_support.py`
- `_ask/tests/test_revising_browser.py`
- `_ask/tests/test_revising_performance.py`
- `_ask/ui/benchmark_workbench.py`
- `_ask/ui/streamlit_app.py`
- `_ask/ui/workbench_loading.py`
- `_ask/ui/workbench_navigation.py`
- `_ask/ui/workbench_tests.py`
- `work/revising-workbench/workbench-validation.md`

The browser/accessibility/performance harness, startup fixes, representative UI wiring/cache and UI validation record serve the successor's real browser journey and budget obligations. The accepted plan expressly leaves successful browser/human demonstration in RWB-109. RWB-108's migration/representative gate cases can establish its assigned outcome without approving this UI/browser implementation. These changes therefore cannot ride through RWB-108 integration as implicitly necessary paths. The source-selection/rerun fixes remain technically reviewed improvements, but that narrow review supplied no RWB-108 ownership authority.

Two further extras support that successor work: `.gitignore` adds the UI dependency environment exclusion; `_ask/tests/test_engineering_ui_browser.py` updates the legacy browser journeys consumed by the new browser cases. Neither is RWB-108-owned or required for its assigned pilot gate assertions. `work/revising-workbench/handoff.md` records the broader mixed-task handoff and is also outside ownership; it has no blanket runtime exemption.

## Administrative and operational paths

`work/revising-workbench/intent-confirmation.json` records the updated exact intent approval. It is authorization metadata, not a pilot implementation deliverable; it is not one of the inner-loop runtime exceptions. Preserve genuine human authorization. Its presence does not widen source ownership or permit an `ok` boundary for the implementation above; its administrative handling must remain explicit rather than silently treating every workstream document as exempt.

The following fourteen changed paths are operational evidence/state/result records, not additional implementation ownership:

- `work/revising-workbench/inner-loop/evidence/RWB-107-excluded-attempt-ced3cf.json`
- `work/revising-workbench/inner-loop/evidence/RWB-107-review-7433097.md`
- `work/revising-workbench/inner-loop/evidence/RWB-107-test-review-7433097.json`
- `work/revising-workbench/inner-loop/evidence/RWB-107-test-review-fc091b9.json`
- `work/revising-workbench/inner-loop/evidence/RWB-108-ledger-recovery.md`
- `work/revising-workbench/inner-loop/evidence/unblock-review-228f229.md`
- `work/revising-workbench/inner-loop/evidence/unblock-review-46eae34.md`
- `work/revising-workbench/inner-loop/evidence/unblock-review-e514444.md`
- `work/revising-workbench/inner-loop/evidence/verify-pnt3tntp/integration.json`
- `work/revising-workbench/inner-loop/evidence/verify-pnt3tntp/output.log`
- `work/revising-workbench/inner-loop/evidence/verify-pnt3tntp/verification.json`
- `work/revising-workbench/inner-loop/results/RWB-107.json`
- `work/revising-workbench/inner-loop/state.json`
- `work/revising-workbench/result.json`

`_ask/docs/inner-loop-evidence.md` documents narrow inner-loop runtime exceptions; `_ask/scripts/inner_loop/evidence.py:runtime_exclusions` also explicitly excludes the workstream `result.json`. This boundary assessment does not review those records' correctness or grant an exemption to other workstream files. The restored ignored historical ledger is outside this Git diff; its provenance was separately reviewed, and it does not authorize unrelated paths.

## Integrability and correction

Current candidate is **not integrable with boundary=ok** under the accepted RWB-108 scope. Required outside seams need an explicit independently reviewed contract/ownership/tooling amendment or a redesign that removes them. Successor extras need removal from the RWB-108 candidate's final diff, or an explicitly approved resequencing/scope amendment. Execution success cannot replace either decision.

The mixed commits are already ancestors of the coordinator HEAD. Selecting an older pre-browser commit or peeling successor commits onto another line would require moving/reconstructing the existing history; it cannot be achieved by the normal FF-only integration operation from the current coordinator. Rebase/cherry-pick onto the coordinator are expressly forbidden by the worktree policy and must not be used as an unannounced repair.

**History rewrite is not required to correct the candidate tree.** New corrective commits can restore successor-only path bytes to their RWB-108-base versions (remove files added only for RWB-109), preserving all existing history and review evidence. After the necessary accepted scope handling and fresh exact-candidate review/verification, RWB-109 can introduce its assigned changes through later commits in the same existing workstream. Merely labeling old mixed commits as belonging to RWB-109 does not remove their bytes from the current RWB-108 base-to-candidate diff.

Only this review artifact was written. No source, accepted contract, task state or TaskResult was changed, and no commit or review decision was recorded into coordinator state.
