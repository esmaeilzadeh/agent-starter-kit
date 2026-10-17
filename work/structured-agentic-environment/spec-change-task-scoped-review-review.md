# Independent task-scoped semantic review amendment challenge

## Final re-review: 722fe300

Decision: **APPROVED**. Challenge verdict: **PASS**. No blocking findings remain at exact candidate `722fe3002253e473de0689823c3fe35052d458a1`, compared with accepted pin `822c24338765f00cc66b189d863e247a2b688d38`.

Reviewer: `review_checkplan_amendment`, independent child context; model: `gpt-6-astra` (configured Spec Challenge role); runtime: `codex`; parent model: not exposed. This decision covers the task-scoped semantic review amendment, its reviewed verification-support implementation and regressions, task ownership, and future UI checkpoint obligations. It authorizes coordinator pinning of this exact candidate. It does not integrate WB-001 or approve workstream completion.

| Contract | Canonical digest |
| --- | --- |
| Specification | `f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb` |
| Test plan | `572d2c3dda82e69a49d78b1320ec35835f4f153137e62c35f41af678ad106330` |
| Parsed TaskGraph | `99d51266063945de345d4df1c85a31b06b3536442db162b1c16b40d3de73674a` |

R1 is resolved: completion derives scope/task identity from the bound semantic review and requires the outer record to agree. Independent reproductions of both previously passing mutations now fail: promoting a task-a review to workstream scope and relabeling it as task b. Both produce the scope-mismatch error and the relevant coverage rejection. Mutating selected test IDs, criterion IDs, source digests or naming an unknown task also rejects.

R2 is resolved: full-workstream review selects every ID in the accepted specification, including criteria verified by review. Task reviews retain the criterion union for their exact accepted cases. The corrected I08 regression builds an authorized review-only criterion and first asserts its contract validates. An independent valid-contract reproduction confirms that including this criterion succeeds and omitting it rejects. No invalid empty-type obligation is used.

R3 is resolved: WB-001 owns both modified fixture files in the plan and TaskGraph. All nine task scopes match their graph case lists, all 57 accepted tests have one owner, dependencies precede dependents, and owned paths remain distinct. The canonical product specification and test plan are unchanged from the accepted comparison pin.

The WB-004–WB-009 UI rule retains unique per-task notes/screenshots, the exact integrated SHA, visual inspection against the connected hierarchy and task outcome, and correction of mismatches before the next UI task. These remain future delivery requirements, separate from the verification-support checks completed here.

Verification: `python3 -m unittest discover -s _ask/tests -p 'test_traceability*.py'` passed **22 tests** in 29.234 seconds. Exact-candidate `contracts_at` validation and independent graph consistency checks passed. Disposable-fixture adversarial checks described above passed. No implementation files were edited by this reviewer, and no full workstream verification or UI checkpoint was claimed.

The coordinator must commit the new accepted pin, bind the fresh WB-001 attempt to that coordinator/base, and retain prior attempt evidence. Subsequent semantic review records must use the implemented `ask-test-review/v2` shape with explicit scope, task, test and criterion bindings. WB-001 still needs current task execution, candidate review and integration evidence; final completion still needs a full workstream review and all accepted execution obligations. Earlier rejection records below are historical.

## Re-review: ed47a0f

Decision: **REJECTED** for exact candidate `ed47a0f70815e7095897be4670c34b5a70ac4792`, compared with accepted pin `822c24338765f00cc66b189d863e247a2b688d38`. Reviewer `review_checkplan_amendment`; model `gpt-6-astra`; runtime `codex`; parent model not exposed. R1 and R3 are resolved; R2 remains blocking.

Current canonical digests: specification `f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb`; test plan `572d2c3dda82e69a49d78b1320ec35835f4f153137e62c35f41af678ad106330`; TaskGraph `99d51266063945de345d4df1c85a31b06b3536442db162b1c16b40d3de73674a`. `contracts_at` validates the exact candidate.

The new completion guard derives scope/task identity from the nested semantic review and rejects a differing wrapper. Repeating the prior task-to-workstream promotion now fails with both scope-mismatch and task-review-cannot-satisfy-workstream errors. Both fixture paths are now explicitly owned by WB-001 in the plan and graph. The UI checkpoints and execution authorization remain explicit.

R2 now derives full-workstream criteria from `plan['obligations']`. Valid review-only criteria have no entry there: `coverage.py` rejects an obligation whose criterion has `verification_mode=review`. Therefore full review still excludes those criteria. Repeating the counterexample with a valid authorized review-only criterion yields zero contract-validation errors, but including its review still fails and omitting it still succeeds.

New test I08 masks this defect by adding an invalid empty-type obligation for its review-only criterion and omitting that criterion's required authorization fields. It never validates the altered contract. Correct the selection to all IDs in `spec['criteria']`, and make the regression construct a valid authorized review-only criterion without an obligation, asserting `validate_plan` succeeds before exercising review validation. The retained review-only orchestration fixture must continue to work.

The prior review below is retained as history; the machine decision now binds this re-review SHA.

## Prior review: e681410

Decision: **REJECTED**. Candidate `e68141015f606ba6711dd923d8d197bc6f16491e` must not be pinned. Three blocking findings remain.

Reviewer: `review_checkplan_amendment`, independent child context. Model: `gpt-6-astra` (configured Spec Challenge role); runtime: `codex`; parent model: not exposed. Stage 03 Spec Challenge; writing-for-agents applied in embedded mode. Comparison baseline: prior reviewed pin `897cb40a8362aed3d5858a4e105b9a374480fcc5`.

## Exact reviewed contract

| Contract | Canonical digest |
| --- | --- |
| Specification | `f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb` |
| Test plan | `572d2c3dda82e69a49d78b1320ec35835f4f153137e62c35f41af678ad106330` |
| Parsed TaskGraph | `9d2538ae0c9f38714188eec790ba72370c3e7c3e5529d78bada13766ced7d2f4` |

Machine decision: `traceability/task-scoped-review-plan.json` under this workstream.

## Blocking findings

### R1 — Completion trusts scope outside the bound semantic review

Location: `.agents/ask/verification/traceability/completion.py:51`.

Completion checks the outer recorded `scope` and `task_id`, while `review_errors` selects obligations from the nested semantic review. Neither check requires those pairs to agree. The digest covers the nested review, so changing only the wrapper leaves that check valid. Comparing the supplied wrapper with the retained wrapper also passes when the retained record contains the mismatch.

Reproduced with the real disposable `Consumer(tasks='split')` fixture: independently record a task-a review containing only test U and its unit assessment. With genuine full U/E red/green records, relabel only the retained wrapper as `scope=workstream, task_id=null`. Full completion returns `status=pass, errors=[]` despite the missing E semantic assessment. Relabel only the wrapper task ID to b and supply genuine task-b E execution: task-b completion also returns pass with task-a semantic review.

Required correction: bind the recorded scope/task to the nested reviewed scope/task and enforce completion coverage using that validated identity. Add negative tests for both wrapper mutations. A task review must never satisfy another task or full completion through wrapper relabeling.

### R2 — Full review drops criteria verified by review

Location: `.agents/ask/verification/traceability/evidence.py:158`.

`selected_criteria` is derived from test links for both task and workstream scope. A legitimate `verification_mode=review` criterion has no test link, so it disappears from the required workstream review. This contradicts the proposal's requirement to retain review of every criterion and breaks the existing `FIXTURE-CONFIG` review in `traceability_support.py`.

Reproduced with a valid contract containing an authorized review criterion R: `validate_plan` returns no violations. A full review including R is rejected with stale-binding and missing-review errors; deleting R's identity and assessment makes `review_errors` return an empty error list.

Required correction: for workstream scope, derive required criteria from all specification criteria. Keep task selection explicitly scoped, and preserve the required treatment of review-only metadata. Add a regression that accepts a complete full review containing R and rejects its omission; exercise the existing configuration-only orchestration fixture.

### R3 — Fixture changes lack task ownership

Locations: `work/structured-agentic-environment/inner-loop/tasks.yaml:8` and the WB-001 row of `plan.md`.

The candidate changes `_ask/tests/traceability_fixture.py` and `_ask/tests/traceability_support.py` to emit the new semantic review schema. Neither file appears in WB-001's owned paths. Add both verification-support files to the plan and TaskGraph before the new pin. Their inclusion is necessary for the reviewed implementation scope to match its declared ownership.

## Confirmed properties

The canonical product specification and test plan are unchanged from the prior pin. Contract validation succeeds. All nine task scopes match the TaskGraph's exact case lists; all 57 tests have one owner; dependencies precede dependents; owned paths are distinct. Task-scoped review selects the accepted task's test IDs, criterion union and source digests and requires matching per-test decisions. Its two new positive tests pass, including the absence of a future task module.

The UI rule clearly requires running the exact integrated candidate after each WB-004–WB-009, retaining its SHA, screenshot, findings and corrections, and resolving a mismatch before the next UI task. The twelve checkpoint paths are unique and assigned to the corresponding task. These are future delivery obligations; no UI implementation or checkpoint execution is approved here.

The proposal explicitly requires independent review and a new accepted pin, a fresh coordinator/base, and preservation of the prior candidate evidence. The plan continues to require complete workstream review and genuine execution/TDD evidence at final completion; R1 and R2 prevent this candidate from reliably enforcing that promise.

## Verification performed and limitations

`python3 -m unittest discover -s _ask/tests -p test_traceability_evidence.py` passed all eight tests. Independent disposable-fixture counterexamples reproduced R1 and R2 without editing repository source. Read-only contract and ownership checks produced the results above. No full repository verification or UI test was run in this review. The existing tests passing does not resolve the reproduced authority gaps.

Amend the implementation, focused regressions and owned paths, then independently review the new exact candidate before pinning.
