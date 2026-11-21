# Completion handoff

Status: incomplete; implementation paused after diagnosis at the human's request.
This handoff is stored and pushed on `agent/client-security-hardening` by explicit
human direction. It adds no implementation changes or passing verification claim.
Resume the remaining work below when implementation is requested.

## Baseline and authority

- Diagnosed source: `7022e057` (resolve to its full SHA when resuming).
- All CSH-01 through CSH-10 tasks are recorded as integrated. Milestone records
  exist under `progress/`; final aggregate verification and closeout remain due.
- State revision 119 still names coordinator source
  `f15be1d952878f0c3f5458480bf2f992a4b32b24`; retained checkpoint is
  `1f1ec069eb47dbc63a2b2526f46d2ef2b8aed6bd`. Recheck these observations on resume.
- `verification-result.json` records a failed aggregate at that coordinator SHA.
  `result.json` still records the earlier `plan-ready` endpoint, not completion.
- Keep accepted intent, spec, registry, test plan, TaskGraph and authority pins
  unchanged. Continue on this branch under `completion-scope.md` and
  `completion-implementation-plan.md`, with kit dogfooding disabled.
- Use the active runtime's configured implementor, reviewer and confidence ladder,
  including user overrides. The dispatcher already resolves runtime, project and
  workstream ladder settings; retain that behavior.

## Ordered implementer work

### 1. Preserve evidence and reconcile the maintenance baseline

`git status` has no tracked edits at the diagnosed source, but `./ask check-clean`
fails: the last aggregate's completion projection, appended execution ledger,
run `4c14655e6508421b9775c93de4d44f8c`, and static logs/receipt are not retained in
the current checkpoint. The static log directory is
`traceability/static-runs/27df1e7012d84fd8bfeafbade0d051a5/`.

Preserve that failed evidence and its private raw output. Use the existing
reviewed recovery/checkpoint transaction to reconcile the maintenance commits
after the recorded coordinator, plus this documentation handoff. Validate exact
source, checkpoint, revision, append-only ledger and immutable prior evidence.
If terminal workstream finalization lacks a supported operation, implement the
smallest explicit validated operation at that boundary. Keep task results and
integration receipts unchanged; avoid manual state/ref rewrites or broad clean
gate exceptions. Completion criterion: retained evidence and an attributable
current coordinator baseline, with no lost or relabeled failed runs.

### 2. Fix project model override propagation

`_ask/scripts/sync-cursor-binding.sh` omits `_ask/bindings` from its transaction
inputs, although the runtime model resolver reads `_ask/bindings/models.yaml` as
the legacy project override. The standalone runtime sync includes this input.
Include the missing input in normal sync and add a focused consumer check that
normal `./ask sync` preserves the configured project and workstream choices.
Keep native model names in runtime/user configuration.

### 3. Repair I07's ordering and candidate/publication identities

Fresh focused checks at the diagnosed HEAD: I09 passes; I07 fails with
`uncommitted or unretained paths before publication: work/w/result.json`.
I07 is in `_ask/tests/test_traceability_entrypoints.py`.

Move result recording after integration and the corresponding final verification.
Preserve the clean publication guard. The isolated probe without premature result
recording integrates successfully and publishes a milestone commit; coordinator
and HEAD then name that publication, while the milestone keeps the original tested
candidate SHA. Replace I07's assumptions that all these SHAs are identical with
assertions against those distinct identities and the exact publication receipt.

Ordering alone is insufficient: the probe's subsequent acceptance rejects the
publication SHA for missing current review, and recording a pass for the old
candidate rejects it as non-current. Obtain the fixture's exact current-candidate
review and Green/static evidence before current acceptance/result recording;
retain original task verification as historical task evidence. Preserve rejection
of stale or substituted candidate evidence.

### 4. Finish the remaining verification mismatches

- CSH-T22, `test_client_verification.ClientTests.test_private_retained_outputs`,
  freshly fails at its expectation that `runs/<id>/results.json` is visible to Git.
  Align this assertion with the approved compact-milestone design: execution
  summaries are checkpoint-retained runtime, public task progress remains tracked,
  and raw output retains private permissions and protection from ordinary staging.
  Preserve the legacy tracked-log warning and index-preservation assertions.
- `test_client_model_decisions.ConfidenceDecisions.test_strict_threshold_and_malformed_confidence`
  emits seven unsupported `subTest` outcomes in instrumented aggregate collection.
  Use equivalent assertions supported by the existing runner; keep every malformed
  value and threshold check. Do not silently drop unknown or unsupported cases.
- `test-check-workstream-guidance.sh`: freshly fails before its intended assertion
  because generated model-state publications are unretained. Prepare and retain
  fixture state so the test actually reaches missing-spec guidance.
- `test-codex-skill-parity.sh`: the last aggregate fails because its copied consumer
  is not initialized as a Git repository for transactional sync. Repair fixture
  setup while preserving its collision, overlay and idempotence checks.
- `test-humanizer-docs-specs.sh`: freshly fails on its obsolete `v3.0.0` assertion.
  The manifest pins commit `9862685f575c65a8247f90369951df1b3416e3d6`.
  Correct the test's pin expectation; retain the current dependency pin.
- `test-start-work-no-explore-map.sh`: the last aggregate reports missing
  `inner_loop/clean.py` in its copied fixture. Include the clean check's dependencies.
- `test-inner-loop.sh`: the last aggregate reports required candidate verification
  failure. Reproduce in its isolated consumer, inspect the exact failed receipt,
  and repair the cause. Its root cause was not established in this diagnostic turn.

Other fixture repairs were committed in `7022e057`; the complete suite has not been
rerun at that commit. Treat historical failures as historical until a current
focused run or the final aggregate establishes their current status.

### 5. Complete one bounded verification and closeout

Commit each meaningful correction. Run focused checks while correcting failures.
Finish task milestone publication before the final aggregate. Obtain independent
review of the final exact source candidate using the configured reviewer, then run
`ASK_WORK_ID=client-security-hardening ./ask verify` and the explicit remaining
obligations in the implementation plan. Require every mandatory check to pass and
all 40 accepted client-security test identities to have valid passing evidence.

Retain aggregate output through the validated checkpoint boundary without
regenerating all task milestones. Record the supported final result against the
exact verified source SHA. A compact closeout commit must preserve that identity
and distinguish it from its own evidence-publication SHA. Recheck accepted artifact
digests and retained clean status. Report remaining human acceptance authority.

Stop once that closeout is complete. Repeat affected verification only for a new
source change, a concrete failure or unresolved concern; evidence-only publication
does not itself restart implementation or the entire milestone publication cycle.

## Local evidence custody

The visible untracked review/adoption evidence remains local and checkpoint-bound:
`inner-loop/evidence/CSH-10-final-review.md`,
`inner-loop/evidence/recovery-adoption-final-review.json`,
`inner-loop/evidence/recovery-adoption-final.json`, and
`traceability/reviews/f3a4be41d96d4d391b16727d34e25852b0c694bd.json`.
This source-branch push does not transfer private checkpoint refs or raw logs.
Preserve their existing local custody; use reviewed private checkpoint transfer
if a later implementer needs another machine.
