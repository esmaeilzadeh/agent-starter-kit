# Independent WB-004 remediation review — 6b046a5

- **Verdict:** REJECTED
- **Boundary:** ok
- **Reviewer:** /root/review_wb001
- **Model:** gpt-6-astra
- **Runtime:** codex
- **Parent model:** gpt-6-luna
- **Candidate:** `6b046a50ed3ebb400af4faeabc36ebea09bb520d`
- **Task base:** `70dd295aacff869857081a94870d02fcbf4d640c`
- **Accepted contract / inventory base:** `55c11fad3e0391f8a47236166c8d5941d824ef73`
- **Spec digest:** `f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb`
- **Plan digest:** `4845c9f46fb7ecfe4f368e006c1a8d89b2f7c3ea5beefe1478b08ea184eb09e8`
- **TaskResult:** `work/structured-agentic-environment/inner-loop/results/WB-004.json`
- **TaskResult SHA-256:** `ece4abce67c6ad7f0149784de80e626b9ee4c3029a82f1efe5959dc9ec6f2e71`

## Blocking finding

### R4 — high — `_ask/ui/streamlit_app.py:149`

The new committed-source path constructs a `Snapshot` then calls `project` without invoking the shared captured-input validator. `read_snapshot` verifies Git/file access; it does not validate the Engineering Model and linked canonical contracts. Returning only `initial.diagnostics` therefore treats parseable but invalid committed inputs as a usable hierarchy.

**Reproduction:** Build the assigned pilot fixture on a live `agent/pilot` branch. Increment `specs/current/pilot.json` revision without changing `work/pilot/test-plan.json`'s `spec_digest`, then commit. Working-tree selection has no admitted projection. Select `git:agent/pilot`: the committed hierarchy renders normally with `view['diagnostics'] == []`. Calling `view['captured'].diagnostics(root)` returns:

```json
[{"code": "EM001_CANONICAL_DEFINITION", "path": "work/pilot/test-plan.json", "message": "spec_digest_mismatch: "}]
```

The UI shows its ordinary committed/read-only source badges, story/scenario/task/test outline and no invalid-source warning. Read-only edit restrictions do not establish source validity. Validate the complete immutable captured input set through the existing authority before publishing its view, preserve one-revision reads, and surface invalid/missing definitions honestly. Add a committed invalid-binding regression and retain genuine red/green evidence.

## Prior findings resolved

| Finding | Remediation | Independent result |
|---|---|---|
| R1 — lost second-scenario test/result | Per-scenario task aliases and `(test, scenario)` emission keys retain each context. | Routes include `build`, `test:CASE-1`, `result:CASE-1`, `build@scenario-2`, `test:CASE-2`, `result:CASE-2`; the expanded AppTest follows second test/result ancestry. |
| R2 — Back renders old detail | Navigation, breadcrumb and Back mutations now run as callbacks before page rendering. | Scenario → Back yields state `purpose` and visible subheader `Purpose` in the same rerun. |
| R3 — no committed source journey | Separate Source selector uses inventory and committed snapshots, pins a full commit SHA, resets context and disables semantic edits. | Selected committed bytes differ from a working draft; form submission is disabled. Advancing the selected branch retains the old pinned source during navigation; explicit Refresh admits the new tip and resets to the root. Source validity is separately blocked by R4. |

## Boundary and independent checks

The task-base→candidate implementation diff still contains only the five WB-004 owned shell/context/navigation/config/test paths. Other changed paths are inherited inner-loop coordinator evidence/results/state. Boundary is **ok**. The accepted spec/plan are unchanged. The post-integration UI checkpoint is not a rejection reason.

Both exact-candidate assigned tests pass independently: **2 tests, 5.843s**. Independent temporary Git/AppTest fixtures checked the three prior remediations, full immutable SHA retention across a moving ref, explicit Refresh, disabled historical decision submission, and the invalid committed binding above. An initial moving-ref probe used a branch without a distinct work commit and selected a nonexistent source option; the corrected fixture creates a live branch with a distinct work commit before source selection.

## Retained red/green evidence

- **red:** `03333875786242e2bc771c816a81fbf7` at `19d45be51e4b69f71083bc07a688d54229a20a6f`; canonical report digest `7cc45db6aefa7654a72eb8237f5892396209a6191c72078fc86c7059f9f7f641`; report-file SHA-256 `feec59958ec73bc47655e635f0fb20d5dffda6a6d75b83bf7c94fe0506aceeb8`; log `work/structured-agentic-environment/traceability/runs/03333875786242e2bc771c816a81fbf7/6da66e942ce3447ca329242c39254aa2.log`, SHA-256 `1aa78d76169d599f97be123c9bbcbd36eb2d6ce5dd33708c4c9ac19baba38cf3`.
- **green:** `117dad552c424c8ba36b2eb105bb568e` at `6b046a50ed3ebb400af4faeabc36ebea09bb520d`; canonical report digest `a268d440a793f4f0aecabbd53ec8b432a406a8e9914e74d47cc052a2c3c0bfbc`; report-file SHA-256 `58ce830c89dadbe45bff2588fd1ae2ba85d299eea2d2f017f80afb33b6765ba8`; log `work/structured-agentic-environment/traceability/runs/117dad552c424c8ba36b2eb105bb568e/0ce577dc13e440a8b98131692ad30e86.log`, SHA-256 `5e30f075f0ccd0935585b964132847c25f38257151d18b783a7e6060710914a4`.

The remediation red collects both mapped cases and fails by behavior assertions: Back still renders Canonical behavior instead of Purpose; archive source lacks the read-only badge. Final green collects both and passes at this candidate. Mapped test-file bytes are identical between red and green. Ledger canonical report digests, accepted spec/plan bindings, source-blob digests and actual log bytes were checked. There is no TDD exemption. The new invalid committed-binding counterexample is absent from these assertions.

The TaskResult green summary says 4.121s, carried over from the preceding candidate. The actual retained final-green log reports **6.042s**. This review uses the genuine report/log and does not infer extra execution evidence from that summary.

## Semantic decisions

- **EM-006 assigned stale-edit slice:** APPROVED; original captured identity and no-write stale guard behavior remain exercised.
- **EM-008 connected navigation slice:** APPROVED; distinct shared-task routes and same-rerun visible Back behavior are now discriminated.
- **EM-009 inspected-source slice:** REJECTED; source identity and edit restrictions work, but committed snapshot validation is bypassed.
- **WB-navigation:** REJECTED; meaningful new assertions fix the previous omissions, but all committed inputs in its fixture are valid and it misses R4.
- **WB-form-context:** APPROVED for captured working-tree form behavior; the sibling assigned navigation case additionally exercises historical noneditability. This does not approve R4.

## Exact owned-source digests

- `_ask/tests/test_engineering_workbench_navigation.py`: `9a41242e70f1c781cf73d000929c6bb0b647ab2e87f553bbb9637d7b7af8cc31`
- `_ask/ui/.streamlit/config.toml`: `4118213e373c3f93ce0f484656443566f07a789c72ae1b9b086f58cae588f2c6`
- `_ask/ui/streamlit_app.py`: `4124fb68d9e592d9484c04c5db232756c3c7ccf407331128aab1554d3b24ab4b`
- `_ask/ui/workbench_context.py`: `48795174d0d8bbad7bc816488fc2e4a81bddf83798c270535709e38efee72e9c`
- `_ask/ui/workbench_navigation.py`: `f12971e89879984158f427c09ee7af2f64521a09a336e1f37f73c7af9caa39ee`

Companion semantic artifact: `work/structured-agentic-environment/traceability/review-input-WB-004-6b046a5.json`. Its accepted-pin inventory includes inherited task files/cases and its decisions cover only WB-004. Read-only semantic validation reports only the intended rejected EM-009/WB-navigation decisions, with no candidate/source/inventory binding errors.

The preceding rejected review is preserved. No implementation edits, coordinator-state updates, recording, integration or commits were performed.
