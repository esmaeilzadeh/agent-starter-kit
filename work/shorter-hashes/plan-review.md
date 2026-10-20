# Independent plan review

## Attribution and exact target

Reviewer `/root/shorter_hashes_challenge_r6`, Codex independent subagent, saved model `gpt-6.1-sol` at `medium` effort; parent model not exposed. Applied `kit-05-plan` structured-test review and the existing traceability authority/runner contract.

Reviewed commit: `8f40b6c83834d1224726962baa3b70fefc896705`.

- Sealed revision-7 spec canonical digest: `9bd9107a4d9490528178e2ac204c44926aa9b0e8675fd58f042e2a6fa2a77a3e`.
- Test-plan canonical digest: `99e3aa9e654e1f26156ffe4697ae759e8045b980dd55a6bbfe24a0291e874c9d`.
- TaskGraph canonical digest: `96ba0772a4d4e28630d64c34b604dec93b5d1769eda000d7874e20719d74524a`.

Exact-byte hashes for the plan, inventory, baseline, tokenizer requirements and spec seal are recorded in `traceability/plan-review.json`. Both records bind this exact committed target; they supply no execution evidence.

## Decision

**CHANGES_REQUIRED** for two bounded planning-contract corrections. The sealed specification does not need reopening.

### P1 — unclassified generated JSON/report producer

`_ask/scripts/record-run.sh` writes `eval-run-meta/v1` with a full `git_sha` into `run_manifest.json` and repeats the metadata in `summary.json`; it also emits SHA-bearing registry/report text. The supposedly complete surface inventory does not classify this producer, and no task owns it. Existing full-ID validation/plumbing can remain an explicit exception, but that alone does not justify repeated full hashes in newly generated ordinary records.

Counterexample: all ten tasks finish while `ask record-run` continues producing verbose repeated SHA metadata, yet the plan claims every eligible workflow JSON/report producer has been treated. The task allowlists prevent fixing the omitted writer within existing scopes.

Scope-preserving correction: inventory the boundary; assign new-record/reference normalization and legacy-compatible output/read behavior to task 8 with relevant executable assertions and source mapping. Alternatively justify a precise required verification exception rather than silently omit the family. Do not alter historical records or weaken exact HEAD validation.

### P2 — incomplete declared test-input/source binding

Task 9 owns a shared `_ask/tests/workflow_refs_fixture.py`, but every 9/* case lists only its main test file in `source_paths`. Measurement cases 1/* and 10/1 omit their frozen baseline/requirements inputs. Later integration/e2e cases also omit the already-existing shared reference modules they exercise. The existing adapter, review and completion helpers compute per-case/source digests from these declared paths; they do not automatically discover imported or subprocess inputs.

Counterexample: a shared fixture changes the generated repositories or expected result while the case body remains unchanged; its case-source declaration still identifies only the main file. The exact candidate SHA globally pins the repository, so this is not an authority bypass. It is an incomplete declared dependency/continuity contract contrary to the claimed complete mapping and the spec's actual-input binding requirement.

Scope-preserving correction: enumerate each consuming case's actual planned helper/config/module inputs. Include the fixture for task-9 consumers and frozen baseline/requirements for baseline/savings consumers. Bind existing shared production modules used by later tests. Preserve task executability: do not list paths introduced only by future tasks in an earlier task's run. No production implementation is needed for this correction.

## Assessment of the remaining contract

The ten tasks have concrete outcomes, exact case ownership and a linear dependency order. Shared paths in tasks 1/10 and 8/10 are explicitly serialized; one committing writer and scope-amendment rules preserve ownership. Task 9 is deliberately a tests/fixture deliverable; discovered production defects must amend the responsible task before edits. No behavior is hidden behind an unresolved design choice: numeric grammar, separate trust-anchored catalog, reviewed profiles, coherent capture, immutable decisions and migration/public interfaces are fixed within the sealed spec.

Read the current validators, `adapters.py`, `unittest_runner.py`, `evidence.py`, and the traceability documentation. All 14 declared module selectors use the supported unittest adapter; the named class/method IDs are suitable explicit future cases. Task filtering is supported. A module may contain only its mapped cases when collected for final workstream execution; unsupported subtests/extra unplanned cases cannot supply completion. Future tests still require behavior-assertion Red, not import/setup failure, followed by actual Green and independent continuity review. No planned test currently exists or has run.

The JSON obligations exactly match the specification's required types:

| Criteria | Required evidence types |
| --- | --- |
| SH-01, SH-02, SH-03, SH-06, SH-08, SH-09 | unit, integration |
| SH-04 | integration, e2e |
| SH-05, SH-07, SH-12, SH-13 | integration |
| SH-10, SH-11 | integration, e2e |
| SH-14 | e2e |
| SH-15, SH-16, SH-17, SH-18 | unit, integration, e2e |

All 18 have mapped meaningful positive/negative assertions. In particular, 3/* covers unknown fields, reviewed profiles and externally changed bindings despite equal blobs; 4/* covers direct versus potential impact, old-pin retention versus new revision, multiple inputs, inherited obligations, deletion and coherent capture including ABA/new owner refs; 5/* and 9/1 cover coordinator authority and exact approval/execution binding; 8/* covers explicit migration and interruption; 9/* covers actual CLI/worktree eligibility/completion outcomes. New formats are normalized before existing policy checks. Catalog authority cannot bootstrap accepted-tests authority from candidate data. Required full-value exceptions preserve plumbing, trust registration, exact checks and original historical bytes; they cannot justify ordinary report repetition without classification.

The frozen experiment contains all three questions and 14 real committed files, including historical reports and selected bound log bytes. Independently verified every byte length/hash against baseline source `9a3d25d035baafc23508f242020d46fae7ff5b14`. The tokenizer is pinned to `tiktoken==0.12.0`, `cl100k_base`, `encode_ordinary`; provisioning/version checking precedes measurement. No tokenizer execution or savings is claimed here. Question equivalence, complete needed lookups, unique generated JSON outputs, catalog/profile/index/decision overhead and retained original archives are counted. Strict aggregate token and JSON-byte reductions and disclosed per-journey regressions preserve SH-12. A failed benchmark cannot be accepted by changing thresholds.

Recovery and discovery are concrete obligations, not vague aspirations: common-directory persistent lock, generation/CAS and recoverable journal must preserve complete old/new observations, immutable targets and crash retries. Inventory capture covers local live/archive/shared owners; additions/removals/ABA and new-context freshness are explicitly tested. An unsupported external writer cannot silently produce complete clearance.

## Checks and boundaries

Loaded the exact committed spec/test-plan/graph through the existing `contracts_at` validator successfully. Independently checked 10 tasks, 37 cases, 14 runners, and exactly one responsible task per case. Independently verified all 14 frozen corpus files. These are planning checks, not behavior executions. The coordinator's reported graph/path validation remains separate from this semantic assessment.

Resolve P1/P2, commit the corrected planning contract, and renew independent review of its exact bindings. This decision cannot register an approved plan. It grants no complete-intent approval, task-loop initialization, implementation authorization, execution review, final completion or acceptance.
