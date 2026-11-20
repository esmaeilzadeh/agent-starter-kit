# Client security completion and maintenance implementation plan

Status: implementation-ready companion plan; stop after independent plan review.
Planning coordinator: Sol/high for this task only. Execution handoff: Luna
coordinator; independent reviewer: Sol/medium. Consult the approved confidence
ladder autonomously when material uncertainty remains at 90% or below.
Scope authority: companion `completion-scope.md`, committed at `be8929f`, records
the human's latest all-three-outcomes direction and immutable accepted preimages.

## Authority, routes, and boundaries

The human explicitly requires all three outcomes for the current work on
`agent/client-security-hardening`: recover and finish CSH-10, publish compact
milestone evidence including the current backfill, and finish operational
laddered escalation. Recovery is a bug fix: retained valid evidence and a pending
task cannot be reconciled safely by current tooling. Milestones are a feature;
the clean gate's refusal of documented retained-runtime exceptions is a bug fix.
Escalation is completion of the same-branch authorized feature at `6400154` /
`e8414c4`. Reproduce each defect in an isolated fixture before its regression and
repair. Preserve passing guards as Green. These outcomes share files and run
serially under one committing writer; no new workstream or overlapping branch.

AGENTS.md's self-development rule governs: kit dogfooding stays disabled during
this maintenance and closeout. The frozen copy at
`/tmp/askit-security-csh06.98f3c09.frozen`, commit
`98f3c09d958a75c6e78181f196f313a99b4c0379`, remains unchanged. It is historical
runner evidence, not the controller for these changes. Do not upgrade its pin or
claim its blocked reconcile succeeds. Use directly invoked, independently
reviewed product recovery/verification tooling and isolated fixtures. This avoids
requiring the unrecovered CSH-10 loop to authorize its own repair. Existing
accepted security tests, independent review, and final verification remain due;
no kit workflow artifacts or feature gates are prerequisites for this maintenance.

Keep `intent.md`, accepted spec/registry, test plan, TaskGraph, and their authority
pins byte-identical. This companion plan supplies bounded maintenance tasks; do
not amend accepted ownership globs to absorb maintenance. Human approval and
explicit scope decisions retain their authority. The current endpoint authorizes
planning only: review this plan, commit it, report the handoff, then STOP for the
human's switch back to Luna. No recovery transition, migration, or implementation
is authorized by reaching that endpoint alone.

## Evidence and source baseline

Recheck these identities at execution; never substitute a newer value silently.

- Planning source started at `72c7e4d`; record the exact reviewed plan commit and
  eventual execution HEAD separately. State revision 108 has digest
  `c05a4f9478cf1888a2d721b8e84bb606c331537152dba736a865f1211cc57dc3`, coordinator
  `9c62390c2f8b135f0b0256c2ad1233145d64c6d7`, checkpoint
  `c8ebe82a55f40fca95036c0555e5280bbe605add` at
  `refs/ask/inner-loop/client-security-hardening`. CSH-10 is pending, attempt 0,
  with no attempt history. Preserve that history; no historical attempt exists.
- CSH-01–09 results retain contract
  `ab109ead101e409f8f30b5339cd3ecf2157bf4c6`; current accepted contract is
  `18783adf1f922fa902215b49a45938ddeea9cba0`. Existing scope/document/review
  checks pass before the traceability predicate. Do not rewrite old result pins.
- Current ledger has 80 rows, digest
  `f526f52796a1e360e8b2c4120171721966a230c83fe1a13459354e484a7da95f`;
  checkpoint's 77 rows are its exact prefix. Preserve every row and report,
  including historical CSH-10 Reds `9df29c7a6725452e8824ccb902094a2b` and
  `45a9810a47ca418da3f4d329695a04b6`, and failed aggregate
  `bf2e9bdc52cb4e95b0242d78a4216c59`. None authorizes a new attempt or a pass.
- `e889779` retains the 279-file structured recovery bundle and manifest;
  archive digest is `6605baa865406e1137d66e1add0469cc4a649463535bc132bc6be5dbd5dd6091`.
  Raw 128 logs remain private at
  `/home/mohamad/.local/state/askit/recovery/private-raw-logs-20261120T121230Z/raw-logs.tar.gz`
  (parent 0700, archive 0600), including the 89 report-referenced outputs.
  Verify bytes without printing output/credentials or copying raw logs to Git.
- Recovery rejects changed `traceability/model-state/current.json`, newly
  published generation/publication files, and new `completion.json`. Current
  `_traceability_matches_checkpoint` only accepts replacement completion as a
  JSON object when already retained; it has no authenticated new-projection
  treatment. Append-only ledger extension is already supported.
- The queued draft under
  `/home/mohamad/.local/state/askit/recovery/evidence-20261120T025943Z/queued-evidence-publication-draft`
  is design input only. Its `milestones.py` and `clean.py` are not installed.
  Its integrated-only/terminal-backfill assumptions block the required current
  backfill. Do not copy it wholesale or retain its broad evidence-ignore rules.

## Chosen design

Use the existing state/checkpoint transaction boundary for one explicit reviewed
recovery adoption. Keep CSH-10 pending at attempt 0 during adoption, advance only
the coordinator baseline and append a recovery receipt, then start a real new
attempt through supported tooling. Implement the missing transition first; do
not edit state/ref JSON by hand, use `resume`/`resume-repair`, reset source, forge
an interruption, or mark CSH-10 integrated from earlier runs. Direct disabled-kit
closeout still uses validated evidence and supported state transitions, so it
leaves a resumable consistent repository.

Treat mutable projections separately from immutable evidence. Model state is
published by `_ask/scripts/engineering_model/admission.py` (`_pointer`,
`_publication`, `_load_generation`, `guarded_publication_chain`), not hypothetical
`publication.py` or `evidence_state.py` modules. Reuse its validators through one
small read-only boundary if needed. Content hashes prove consistency; its
publication token is cooperative provenance, not independent authentication.
Bind permitted replacements to retained checkpoint ancestry plus the exact
independently reviewed adoption manifest, or a subsequent exact verifier receipt.
A filename/prefix, valid JSON, or self-reported digest alone grants no authority.

Publish one normal Git file `work/<id>/progress/<task-id>.json` per task, updated
at serialized meaningful task boundaries. Preserve rejected reviews, corrected
submissions, executions, refactor notes, and integration history inside that
compact record. Raw output stays private. A source candidate SHA always means the
actual tested/reviewed candidate; an evidence publication commit never replaces it.

## Ordered implementation tasks

All tasks below belong to the Luna coordinator as sole committing writer, with
Sol/medium read-only review of each exact candidate. These are companion task IDs,
not additions to the accepted CSH TaskGraph. Commit after each reviewed meaningful
step on the existing branch; preserve rejected candidates and correction evidence.

| ID | Deliverable and dependencies | Exact owned surfaces | Focused cases |
| --- | --- | --- | --- |
| CMP-01 | Recovery projection validation; first | `_ask/scripts/inner_loop/recovery.py`; narrow read-only helper in `_ask/scripts/engineering_model/admission.py` if necessary; `_ask/tests/inner_loop_recovery.py`, `_ask/tests/inner_loop_recovery_fixture.py`; `_ask/docs/inner-loop-evidence.md` | REC-01–04 |
| CMP-02 | Reviewed pending/zero-attempt adoption tooling; after CMP-01 | `_ask/scripts/inner_loop/recovery.py`, `state.py`, `checkpoint.py`, `__main__.py`; `ask` help only; same recovery test/fixture files; `_ask/docs/inner-loop-evidence.md`, `.agents/ask/task-loop.md` | REC-05–09 |
| CMP-03 | Milestone publisher, clean migration, current backfill support; after CMP-02, before any live adoption/backfill | new `_ask/scripts/inner_loop/milestones.py`, new `clean.py`; `driver.py`, `__main__.py`, `checkpoint.py`, `evidence.py` only for shared retention/publication hooks; `_ask/scripts/check-clean-worktree.sh`; `.gitignore`; new `_ask/tests/test_task_milestones.py`; `_ask/tests/test-check-clean-worktree.sh`, `inner_loop_reliability.py`, `test-inner-loop-reliability.sh`; `_ask/policies/worktree.md`, `_ask/docs/inner-loop-evidence.md`, `.agents/ask/task-loop.md`, `ask` help | MIL-01–09 |
| CMP-04 | Operational confidence ladder and projections; after CMP-03 | `_ask/scripts/model-decisions.py`; `.agents/ask/bindings/runtimes/{codex,claude,cursor,opencode}.yaml`; `_ask/policies/delegation.md`, `workflow.md`; `.agents/ask/stages/00-explore.md` through `10-accept.md`; `.agents/ask/task-loop.md`; `_ask/tests/test_client_model_decisions.py`, `test_client_runtime_config.py`; `_ask/tests/test-stages-inner-loop.sh`; `_ask/docs/codex-model-routing.md`, `.agents/ask/bindings/README.md`; generated runtime views via existing sync scripts | LAD-01–08 |
| CMP-05 | Exact current recovery review, adoption, and CSH01–09 backfill; after CMP-01–04 pass independent review | New scoped records under `work/client-security-hardening/inner-loop/evidence/` and `work/client-security-hardening/progress/`; state/checkpoint changed only by reviewed CMP-02/03 commands; compact inventory sidecar if needed | LIVE-01–03 |
| CMP-06 | Fresh CSH-10 attempt, complete journeys, aggregate closeout; after CMP-05 | Existing CSH-10 source/test/docs ownership in accepted TaskGraph only; new CMP progress/evidence records; source fixes outside that ownership remain separately attributed maintenance and require fresh candidate review | LIVE-04–06 |

No new dependency or orchestration framework. Inventory generated tracked paths
with the current sync scripts before editing; change canonical sources and
regenerate `.cursor/commands`, `.cursor/skills`, `.cursor/agents`, `.codex/agents`,
`.opencode/agents`, `.claude/agents`, and kit skill views only where those scripts
actually generate tracked outputs. Record the exact generated diff. Do not hand
edit projections, unrelated user settings, or the frozen runner.

### CMP-01: authenticated projection handling

1. Reproduce retained-versus-live conflict using a disposable copy of the exact
   checkpoint and privacy-safe bundle. Check 77→80 ledger extension separately;
   it must remain Green. Preserve original evidence archives before extraction.
2. Classify only known projections. Validate model pointer schema, work identity,
   selected generation manifests/blobs, and every publication link back to the
   retained boundary. Check digests, safe paths/types, no symlinks, no cycles,
   no missing ancestors, and immutable retained generations/publications.
   Default ongoing carry-forward requires the existing guarded chain. Historical
   admission events or an older pointer without a publication token require an
   explicit reviewed adoption manifest binding both endpoints and all new bytes;
   do not silently weaken `guarded_publication_chain`.
3. Validate completion schema/workstream/candidate/scope and its referenced
   structured reports/digests. Historical failed completion may be preserved as
   a reviewed diagnostic projection; it cannot satisfy passing verification.
   Later replacement requires the exact verifier receipt/retained artifact digest
   used by the completion validator. New and replaced projections use the same
   validation. Reject unexplained files or replacements elsewhere.
4. Continue to authenticate historical TaskResult evidence from its retained
   checkpoint bytes, old contract, report lineage, and independent review. Only
   the known projection predicate changes. Never skip accepted-scope or
   historical-output checks to make CSH-01–09 carry forward.

### CMP-02: explicit adoption without circular admission

Add `inner-loop recovery-propose` (read-only) and `recovery-adopt` (explicit CAS)
through the existing CLI. Proposal binds: work/branch; observed revision and state
digest; checkpoint ref/commit; old coordinator; exact new source HEAD/tree;
accepted and historical contract pins/digests; ledger prefix/full digests;
immutable result/review/integration digests; new projection inventory; and an
ordered commit/path attribution from `9c62390` to the selected HEAD. Attribute
security changes, `6400154`/`e8414c4` escalation, evidence, plan, and subsequent
maintenance commits separately. Include the predecessor manifest/checkpoint and
all bytes necessary for independent replay. No future wildcard authorization.

An independent Sol/medium review binds the proposal digest and exact source /
reviewed tooling candidate. Adoption revalidates under `state_lock` with observed
revision and expected ref/HEAD CAS. Reuse `state_transaction`'s narrowly scoped
`reconciliation_validator` to permit only the reviewed source delta; generic
`require_safe` still runs with CMP-01 and all other protections intact. Do not
route this exceptional entry through writer/implementation admission that itself
requires recovery to have completed. The entry checks coordinator authority,
review identity, source cleanliness, branch, complete evidence and stale inputs.

The one state fold changes coordinator to the reviewed source baseline, increments
revision, and appends the bound recovery receipt. It leaves CSH-01–09 task state
and receipts unchanged and CSH-10 pending/attempt 0/history empty. Existing ledger
and historical results remain byte-identical. Publish a new checkpoint whose
`previous_checkpoint` is `c8ebe82…`; retain the old checkpoint/object closure and
bundle. Use existing checkpoint ref CAS then atomic cache replacement. Faults
before publication leave the old authoritative state; faults afterward restore
cache from the new checkpoint and exact retry succeeds without a second adoption.
A stale revision/ref/HEAD, any unexplained commit/path, or any changed input fails
before mutation. No environment bypass or generic force flag.

### CMP-03: milestone publication and clean gate

Define one allowlisted JSON schema with task/work identity, current status,
checkpoint/recovery provenance, source base/candidate SHA, attempt IDs/history,
run/test/case outcomes and digests, Red/Green classification, review decisions
including rejections and correction rounds, refactor notes, and integration
receipt. Include all retained versions of submissions/reviews, not only the latest
paths. Mark historical unattached runs explicitly; do not invent attempt IDs.
Public summaries contain no raw stdout/stderr, environment, credentials, or
unfiltered command output. Preserve full private evidence with hash references;
review the compact publication for secrets before committing.

The publication commit is found through Git history for the progress path; do not
embed a commit's own SHA in its contents. Store a receipt that maps source
candidate → progress blob digest → publication commit in the next checkpoint.
Deterministic rerender with no semantic change produces no commit/state revision.

Use one coordinator publisher for automatic `run`/`resume` safe-boundary hooks and
explicit `publish-evidence` recovery/backfill. Hold the state lock across snapshot,
preflight, staged-byte checks, Git commit and receipt fold; recheck HEAD/ref/input
identities immediately before effects. Refuse unrelated dirty/staged files,
symlinks/special/executable destinations, conflicting generated bytes, wrong branch,
concurrent source edits, and active external writer processes. Permit retry only
for the exact generated unstaged/staged bytes/modes. Never stash, reset, commit all
files, or drop an existing user's index. Crash before commit leaves retryable exact
files; crash after commit recognizes that commit and completes the receipt once.

Preserve source identity and FF integration: publish approved milestones only
after exact candidate verification/integration. Publish rejected/blocked milestones
only at a quiescent boundary before correction; the next candidate must descend
from publication HEAD and receive fresh review. If a separate task ref cannot
safely descend from that HEAD, retain the intermediate event in checkpoint history
and publish its summary at integration/block/interrupt instead of rebasing an
approved candidate. Record this deliberate boundary in docs. The driver never
admits the next writer until due publication succeeds; CLI failures are explicit,
not swallowed. In-place milestone commits may advance coordinator baseline only
with proof that the added delta contains the exact generated progress paths.

Current backfill explicitly supports integrated CSH-01–09 while CSH-10 remains
pending. CMP-05 first adopts the reviewed source baseline through CMP-02; it then
publishes progress records without requiring all tasks terminal. CSH-10 historical
unattached Reds/failed aggregate remain visible in its pending progress record.
Migration uses the authenticated current bundle plus checkpoint ancestry, never
only the older 47-/64-row archives.

Reuse source/runtime classification from `evidence.py`, extending it only with
exact supported cache paths. Shell clean check delegates to the new shared Python
checker. Normal staged changes and progress files are always source changes;
visible runtime exceptions require exact retained checkpoint bytes/types and a
valid matching state, including an empty known lock. Ignored runtime paths also
receive retention checks; `.gitignore` must not hide arbitrary forged evidence.
Keep arbitrary workstream Markdown/authorization records stageable. Do not ignore
all `inner-loop/evidence/`. Remove only enumerated current runtime cache files from
the index with worktree bytes/history preserved and an explicit reviewed inventory.
Never blanket `git rm --cached` over workstream directories.

New checkpoints/public progress must not introduce raw output to Git. Audit
`checkpoint._runtime_files` and its consumers: keep validated structured reports,
retain raw outputs in private storage with digest/custody references, and preserve
existing historical checkpoint bytes unchanged. Exercise restore/export/import
and `_valid_historical_output` compatibility; missing private raw custody blocks
claims depending on it. Do not rewrite old Git history to remove legacy outputs.

### CMP-04: real operational escalation

`e8414c4` establishes policy and Codex/Claude binding entries; it does not provide
live catalog/effort evidence, centralized decision dispatch, or complete stage
coverage. Finish these using `model-decisions.py`'s `runtime_request`, existing
runtime adapter capability evidence, and native agent tools. No second model
resolver or independent agent orchestration framework.

Add a small deterministic decision operation to the existing CLI: input decision
ID, scope/authority kind, confidence, current-session capability evidence, prior
assessments and policy; output `continue`, `consult` with the next verified native
model/effort, or `ask-human` with a precise reason. Coordinator executes `consult`
through exposed native tools/adapter, records actual model/effort and assessment,
then calls the same operation again. Failures/unverifiable identities are recorded
as unavailable and move to the next rung. Do not fake an assessment. Bind reuse
to the same material decision and evidence, not merely a model name.

Strict rule: consequential unresolved decisions continue autonomously only when
confidence is >90. At 90 or below, consult available rungs once in order: Codex
Sol/high → Astra/medium → Astra/high. Reuse an applicable existing assessment
from that rung or later rung; avoid cycles. Human authority/preference, scope
changes, explicit model restrictions, exhausted available rungs with material
uncertainty, or unsafe irreversible action remain human decisions. Consultation
does not substitute for Sol/medium independent review or any verification.

Validate both model availability and effort support using native exposed tool
metadata/current-session runtime evidence, then verify actual returned identity.
A YAML `picker`/`confidence_escalation` entry or CLI help alone is not availability
proof. Current Codex tool metadata exposes these models/efforts; confirm again
at execution. Claude's configured IDs remain candidates until native capability
proof; remove unsupported assertions from prose. Cursor/OpenCode currently have
no verified ladder: use verified native equivalents only if evidence supports
and records them; otherwise mark unavailable/exhausted. Do not invent equivalent
model names or prompt for a model at every gate.

Every canonical stage and task-loop instruction references the central policy;
only that policy states thresholds/ordering. Regenerate existing runtime views.
Preserve one Grill `Confirm model plan` / `Change selected models` interaction,
stage reuse and implementor handoff. Sol/high planning override stays local to
this task; Luna execution coordinator and Sol/medium reviewer assignments persist.
Record escalation evidence in existing work artifacts with decision identity and
actual settings; do not add another global model configuration file.

## Focused cases and verification

These case IDs belong to maintenance regressions, not the accepted CSH test plan.
Execute in disposable repositories/private runtime directories before live adoption.

| Cases | Required assertions |
| --- | --- |
| REC-01 | Reproduce current projection rejection; 77→80 ledger extension remains accepted; original retained files unchanged. |
| REC-02 | Valid bound new/replaced model-state and completion accepted; preserved failed completion still fails passing-completion predicates. |
| REC-03 | Tampered blob/publication/chain, cycle, missing ancestor, wrong work/candidate/scope, symlink/escape, unreviewed admission and arbitrary new file rejected. |
| REC-04 | CSH01–09 old-pin scope-compatible carry-forward passes without rewriting old results; changed accepted spec/scope/review/report still rejected. |
| REC-05 | Adoption preserves pending attempt0/history, CSH01–09 receipts, ledger prefix/full bytes, failed aggregate and old checkpoint. |
| REC-06 | Wrong reviewer/worker authority, stale state/ref/HEAD/proposal/digest, unexplained source commit or dirty/staged source rejects without effects. |
| REC-07 | Competing adopters: one CAS succeeds; old checkpoint retained and new checkpoint links it. |
| REC-08 | Crash before ref publication, after ref/before cache, and retry recover exactly once; export/import retains required source/contract objects. |
| REC-09 | First real CSH10 start follows adoption and increments attempt now; historical Reds never become fabricated attempts or new Red evidence. |
| MIL-01 | Deterministic one-file-per-task projection; no-op rerun changes no commit/revision; source candidate and publication commit stay distinct. |
| MIL-02 | Rejected/stale review versions, correction candidates, refactor notes, attempts and historical unattached runs survive rerenders/backfill. |
| MIL-03 | Dirty/unrelated staged/generated-byte mismatch, wrong branch, symlink/type/mode, source drift and concurrent writer reject without index/source loss. |
| MIL-04 | Exact precommit staged retry and postcommit/pre-receipt retry complete once; checkpoint provenance references correct commit/blob. |
| MIL-05 | Driver blocks next writer on publication failure; next base descends from publication; approved candidate still integrates exactly; safe separate-ref deferral tested. |
| MIL-06 | CSH01–09 backfill succeeds with CSH10 pending after adoption; arbitrary source advance without adoption remains rejected. |
| MIL-07 | Clean gate accepts only retained runtime bytes and known lock; staged runtime/progress/source, forged ignored bytes, missing/corrupt checkpoint and symlink remain dirty. |
| MIL-08 | Enumerated untracking preserves worktree/history and source docs; arbitrary evidence paths remain visible; repeat migration is harmless. |
| MIL-09 | Raw logs/output/secret canary excluded from all new public/checkpoint commits; private custody modes/digests and restore/export/import behavior verified. |
| LAD-01 | 90 consults; >90 continues; malformed/nonfinite/out-of-range confidence rejects. |
| LAD-02 | Ordered once-per-decision rungs, same-decision prior later-rung assessment reuse, changed evidence invalidation, no cycles. |
| LAD-03 | Unavailable catalog/model/effort, timeout, permission denial, wrong returned identity and unknown runtime move on or exhaust explicitly; bindings alone insufficient. |
| LAD-04 | Human authority/preference/restrictions preserved even above90; exhaustion with uncertainty asks human; no consultation grants scope approval. |
| LAD-05 | Native consultation request carries exact model/effort and assessment record; no invented runtime equivalent or coordinator self-attestation. |
| LAD-06 | All eleven stages/task-loop reference centralized policy and generated projections agree; reviewer remains Sol/medium. |
| LAD-07 | Single Grill confirm/change, stage decision reuse, latest/exact implementor and manual handoff regression tests stay Green; no new repeated model picker. |
| LAD-08 | Fixture-driven full consult→reassess→continue/exhaustion flow; one live native consultation smoke test records actual settings or explicit unavailability. |

Focused execution commands (do not run during this planning turn):

```sh
python3 -m unittest _ask.tests.inner_loop_recovery
bash _ask/tests/test-inner-loop-reliability.sh
python3 -m unittest _ask.tests.test_task_milestones
bash _ask/tests/test-check-clean-worktree.sh
python3 -m unittest _ask.tests.test_client_model_decisions _ask.tests.test_client_runtime_config
python3 -m unittest _ask.tests.test_client_orchestrator
bash _ask/tests/test-stages-inner-loop.sh
bash _ask/tests/test-sync-runtime-agents.sh
bash _ask/tests/test-sync-canonical-ask.sh
bash _ask/tests/test-install-kit-dry-run.sh
bash _ask/tests/test-install-kit-apply.sh
bash _ask/tests/test-askit-self-install.sh
python3 -m unittest _ask.tests.test_traceability_evidence _ask.tests.test_traceability_runner _ask.tests.test_engineering_model
```

Add focused tests to existing modules and one milestone module, rather than a new
test framework. Run narrower case selectors while correcting failures; after exact
candidate passes, repeat only when new changes invalidate that evidence. Any
new touched transaction/retention consumer needs its corresponding existing
regression. Compare accepted artifact digests before and after each maintenance
commit. Independent review binds exact candidate/tree and test receipts.
The mandatory `ask-kit` preset expands executable `_ask/tests/test-*.sh` and
traceability discovery; adding a Python file alone does not register a check.
Invoke `test_task_milestones` from the existing executable
`test-inner-loop-reliability.sh`. Preserve the preset and accepted CSH plan;
the other focused modules above remain explicit final verification obligations.

## Live recovery, completion, rollback, and handoff

- LIVE-01: Revalidate archived manifests, all 80 report digests, private raw
  custody, state/checkpoint identities and accepted artifact bytes. Commit and
  independently review the exact adoption proposal after all preceding source
  commits exist. Do not use a proposal bound to the earlier planning HEAD.
  First make a private manifest-bound snapshot of the entire checkout, Git
  metadata/source closure, accepted authority refs, checkpoint refs and private
  recovery/archive manifests. Verify archive member digests and preserve modes
  before any live transition. Existing older archives alone are insufficient.
  Keep the snapshot outside the repo with 0700 directories/0600 archives; exclude
  it from all publication and never display raw secrets. A Git bundle plus a
  private checkout/archive snapshot is sufficient; no second work branch.
- LIVE-02: Execute the supported CAS adoption once with exact observed identities;
  read-only reconcile must be ready using the reviewed product tooling. Check
  CSH01–09 unchanged; CSH10 pending/attempt0. The unchanged frozen runner may
  still reject newer projections; report this compatibility limit explicitly.
- LIVE-03: Publish CSH01–09 records and pending CSH10 history via reviewed publisher,
  with exact inventory migration. Verify normal Git records contain no raw
  output. Reconcile again; next candidate base includes these evidence commits.
- LIVE-04: Start CSH10 attempt now. Assess current accepted T38/T39 fixtures and
  preserve the historical real Reds as historical. Run actual existing journey
  tests; a currently passing case is Green, never made artificially Red. Diagnose
  any failure and reproduce before a focused repair. New source candidate gets
  fresh exact independent Sol/medium review and task final-Green evidence under
  current accepted contract. Do not reuse an old approval for a newer SHA.
- LIVE-05: Use supported reviewed tooling for candidate verification/integration,
  publish the integrated CSH10 record, then run real aggregate verification at the
  resulting exact branch HEAD. `ASK_WORK_ID=client-security-hardening ./ask verify`
  must execute the current CheckPlan and complete workstream traceability;
  task execution uses `./ask traceability run client-security-hardening --scope task
  --task-id CSH-10 --phase final_green --candidate-sha <exact-candidate>` with a
  private runtime output root when required. Assert recorded candidate SHA,
  all 40 accepted client-security case IDs, nonempty static checks and passing
  aggregate completion. This final whole-repository CheckPlan must include its
  complete existing mandatory suite, plus the focused recovery, reliability,
  engineering-model publication, model/orchestrator, clean gate and CLI
  sync/install regressions above; include new milestone tests in the mandatory
  test inventory rather than leaving them as a manual-only check. Inspect the
  actual collected inventory and run reports for omitted or zero-case modules;
  a fixture-only result is insufficient. Existing failed aggregate remains failed.
  Obtain independent Sol/medium review of the final exact source candidate,
  including cross-module effects and all three outcomes; a later source change
  invalidates that review and affected verification. Record the final result
  through the supported `record-result` command with
  the exact verified commit, and preserve verification/publication commit identity.
- LIVE-06: Final compact inventory names source candidate, independent review,
  task/aggregate receipts, progress publication commits, checkpoint and private
  raw archive manifest. Check clean status and accepted digests. Verify evidence
  completeness, old-history preservation, no raw/secret publication, private
  permissions, exact receipt/candidate identities, and generated/runtime
  consistency. Do not claim that the full check proves every possible regression;
  report any environment-dependent check that could not run. Product failure
  or stale identity blocks completion; report concrete missing evidence. Respect
  remaining human acceptance authority without inventing an implementation/model
  confirmation gate.

Rollback means stop admission, preserve new evidence, and fix forward or revert
an unadopted maintenance commit with a new commit. Never reset source, delete
ledger rows, rewrite prior results, or force the checkpoint back after publication.
Before an adoption CAS, old checkpoint is authoritative. After it, its linked
successor is authoritative and cache restoration/retry is the recovery path.
An evidence publication failure leaves source candidate/review valid; repair or
retry exact publication before another writer. Preserve private archives until
recovery, backfill and final completion have independently verified replacements.

Plan confidence: 94% subjective confidence in this bounded design. Remaining
implementation risks are native runtime availability/effort proof, current
projection-chain compatibility, and raw-output custody during checkpoint migration;
they have explicit failure cases and cannot be resolved by inventing evidence.
If exact source inspection or independent review lowers confidence to 90% or below,
consult the next available approved rung before interrupting the human, preserving
scope/authority limits. No model selection is required at each plan gate.

At the plan-ready handoff, report review findings/corrections, exact committed plan
SHA, execution task order, and the stop endpoint. Do not begin CMP-01 until the
human has switched the coordinator and explicitly continued implementation.
