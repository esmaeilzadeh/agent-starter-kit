# Current continuation handoff: shorter-hashes

Updated 2026-10-29. This section supersedes the Task 6 starting-state and
pending-work claims in the historical handoff below. Resume the live workstream
at Task 9; do not restart Task 6 or treat this file's archived notes as current.

## Live state

- Branch: `agent/shorter-hashes`.
- Tasks 1–8 are integrated. Task 9 is active; Task 10 and final workstream
  verification/acceptance remain.
- Task 9 candidate: `9e381599cc11fabe26b8a0a3a8d92d076dcfd9d2` (`9e38159`).
- Commit `9e38159` fixes decision-only catalog context generation by applying
  the same normalized reference hashes in both `refs` and `owners[*].refs`,
  asserts generation stability after public decisions, fixes selection of the
  9/2 execution record from the public projection, and binds 9/1 tamper checks
  to the clean baseline candidate. Task 9/3 retains the changed-candidate and
  fresh-execution refusal check.
- The single final mapped Green for this candidate completed with failures.
  Runner: `cf5d501d1a904f4a9c53a238f272de64`; report SHA:
  `df8dca012b15e5ecda6918b49bad7532020b6cb10b7c1c786ac08e7dc47abd0c`; log SHA:
  `1f4d52b1fefcb438e3a300f809e929a239079294b0c25b07be90bc4f72ac6778`.
  The implementer inspected this report once and stopped. Do not rerun before
  addressing concrete findings below.
- Candidate-bound process-waiver SHA:
  `5b75b36681cf78fc41a6e2646271db974fc93479feed9a4642994f27f2d1bded`.
  Candidate-bound TaskResult SHA:
  `cdc2e19534c2db831219cee78d728b0b76b8a54bbce3b2c2da897c0dec816f41`.
- The runtime artifacts modified at the original handoff (`results/7.json`, inner-loop
  `state.json`, `references/integrity.json`, and `traceability/executions.json`)
  were preserved in commit `48a9486`. The access preflight and clean-tree check
  passed before recording the interview decisions below. Preserve these runtime
  records; their commit is not passing execution or task-acceptance evidence.

## Confirmed answer to the Task 9/3 escalation

The human selected the recommended answer in Q1 and confirmed the complete
understanding in Q2 of the 2026-10-29 interview, responding `rec` to each.
[ADR 0001](../../docs/adr/0001-revision-assessments.md) records the agreed behavior:
one assessment covers the P1 → P2 transition and both versions' relevant inputs;
each consumer's permission to retain an old pin is assessed separately. An
unresolved second input remains blocking. Use this answer when resolving the
fixture-versus-implementation question below. The exact code mechanism still
requires implementation and review evidence.

The interview authorized documentation only. No implementation, test execution,
candidate approval, integration, or acceptance occurred in this context.

## Reviewer questions and next evidence

The code reviewer previously rejected Task 9 candidate `51e3e87` for three
coverage gaps, then performed a bounded read-only review of `9e38159`. The
reviewer reports that prior findings are mostly addressed: 9/2 now includes a
legacy migration and retained run, 9/3–9/5 use public CLI paths, and 9/1 has
the specified tamper cases. The reviewer identified one additional coverage
gap: 9/2 uses `import_bundle()` directly instead of testing the public `refs
import` command in the same repository and clone. Final exact-candidate review
is not approved.

Green outcomes:

- 9/1 and 9/5 pass.
- 9/2 fails twice on projection shape: post-bundle run record lookup still
  expects `payload.candidate_sha`, though public show returns the full document
  under `payload.items`; select `run-17` by ID. Also replace direct
  `import_bundle()` calls with the public CLI import path and assert results.
- 9/4 fails because the retirement assertion expects `retired.payload.active`,
  though public show returns the full document's `items` array; select the
  retired item by ID.
- 9/3 persists decisions and confirms stable generation, but the public impact
  flow rejects the parent `alpha` decision with `comparison_incomplete` because
  it does not cover every declared dependent input. This leaves old/new item
  paths unresolved. Inspect the accepted 9/3 decision contract and public
  impact evidence to determine whether the fixture must submit the complete
  decision vector or the implementation fails to assess a valid complete
  decision. Preserve unresolved required inputs as blocking.

The reviewer was asked:

1. Does the new 9/2 test cover both a frozen legacy record and a historical
   execution record through the public projection/export-reload path, including
   refusal when dependency or authority is missing?
2. Do 9/3–9/5 exercise public impact, decision, and completion commands for the
   specified affected chains and branch-scoped consumers, including retained
   old pins, required re-execution, and unresolved second inputs?
3. Does 9/1 now cover every specified substitution/tamper refusal on the clean
   baseline without relying on a self-dirtying candidate mutation?
4. Is there any remaining acceptance or fixture-setup gap before exact-candidate
   review? What exact Green report evidence is needed to finish review?

Reviewer answers: the prior findings are mostly addressed; the public import
gap remains as above; no other significant gap was identified in changed cases.
Final review requires a successful Task 9 Green bound to the exact candidate,
all cases 9/1–9/5 passed, per-case source SHA equal to the candidate, successful
collection/exit status, and matching output digests. Reviewer will also bind the
matching TaskResult, base, final checkpoint identity/revision, and owned source
digests. No tests were run and no files were changed by the reviewer.

After one focused repair of the listed 9/2–9/4 findings, run one mapped Green.
If 9/3 remains unresolved, stop and inspect the actual contract/evidence before
making another change or test run. After Green passes, obtain fresh independent
code and semantic reviews for that exact candidate, integrate Task 9 through the
supported scheduler, and proceed to Task 10. Finish with one appropriate
`./ask verify` and `record-result`; do not loop on waived Red expectations or
self-hosted hash/checkpoint integrity churn. Do not fabricate results or repeat
a run without a new code change and named failure.

## User-authorized process exception

For this workstream, the user explicitly waived a true Red prerequisite before
each test. Preserve actual run outcomes: a passing guard stays passing and a
setup failure stays a setup failure. The user also permitted temporary checksum,
checkpoint, and related workflow-state inconsistencies while changing the kit
itself. Preserve recoverable evidence and record reconciliation; final project
state must be stable and consistent, with applicable integrity and authority
checks working normally. Historical evidence retains its original identities.

Preserve actual Green, review, and integration evidence; record exceptions. A
failed Green is a real acceptance/setup result to inspect, not a reason to repeat
Red or checksum ceremony. If a bounded repair is needed, state the concrete
failure, repair it, and run one final focused Green. These exceptions do not
establish passing behavior or workstream acceptance.

---

## Historical handoff (Task 6 recovery; superseded)

The material below records the earlier Task 6 recovery and authorization context.
Its statements that Task 6 is pending or that Tasks 7–10 are all unstarted are
historical and must not be used as the current branch status.

# Implementer handoff: shorter-hashes

## Human direction and endpoint

The user directed this context to **decide and write a handoff only**. No further
implementation is authorized in this context. The implementation agent resumes
Task 6; Tasks 7–10 remain pending under the existing approved feature plan.

The user delegated implementor decisions when confidence is **above 90%**;
escalate concrete uncertainty at or below that threshold. They also explicitly
allowed temporary relaxation of kit process rules to avoid endless loops, with
actual stable system state required eventually. Use that permission for bounded,
attributable process corrections. Preserve approved scope, actual execution
results, integrity checks and historical evidence. Record exceptions rather than
fabricating approvals or repeatedly reopening settled decisions.

The approved intent bytes and confirmation remain unchanged. Do not restart
Explore/Grill or request complete-intent approval for these implementation details.
The earlier feature endpoint is verified and accepted work; this handoff does not
claim feature completion or authorize merging unfinished work.

## Exact starting state

- Branch: `agent/shorter-hashes`; ownership-amendment source: `9ca83ed`.
- Tasks 1–5 integrated; Task 6 paused with **no production implementation changes**.
  Task 6 test-only commits exist, ending at `9637cfe`.
- State revision **52**; Task 6 is `running`, attempt `6:attempt-2`.
- Task/coordinator base: `311d53278ab2f776b3c0ae5a11d759804fac0e02`.
- Current accepted contract: `5911780b48469d1027bc8bcdd3bbb35ebba3694a`.
- Accepted authority: `876094655bb8074493eea9faeff0bcb1f60d37de`.
- Current checkpoint: `f14b3bc8729a1be3000e11318d38f5af2a1c29f9`.
- Implementor assignment: **Luna, high effort**, as recorded in `models.yaml`.

The missing historical checkpoint/authority discrepancy was reconciled under
explicit user authorization. A new current checkpoint was created without
claiming to recreate the missing historical chain. Fresh executions at the actual
original candidates/contracts passed all **24 mapped cases across Tasks 1–5**.
Original results, ledger entries and attempt history were preserved. Independent
recovery review approved at 98%; normal recovery passed and Task 6 was reopened.
See `recovery-exception-authorization.md`,
`inner-loop/evidence/recovery-stable-2026-10-29.json` and
`inner-loop/evidence/reconstruction-review-2026-10-29.json`.

## Approved implementation decisions

1. **Preserve the raw v1 state cache.** `state.json` remains a compatible
   `ask-inner-loop-state/v1` projection. Engineering-model and workbench readers
   raw-decode that file outside Task 6 ownership. Compact the authoritative
   checkpoint artifact and normalize it back to v1 at checkpoint I/O. Preserve
   cache equality, CAS/revisions, one writer, interruption recovery, exact
   candidate/runner/log checks and fast-forward-only integration. Do not add a
   duplicate compact sidecar.

2. **Use the existing shared codec and trusted catalog.** Reuse
   `workflow_refs.codec` and `workflow_refs.store`, with the plan-fixed
   `work/<owner>/references/integrity.json` and its registered authority. The
   approved seam is to create an immutable Git snapshot of structured state,
   task/test or evidence records, register their qualified numeric revisions,
   persist typed references and compact metadata in the checkpoint envelope, and
   resolve through the trusted catalog when reading. Generated snapshot commits
   need not advance product HEAD. Preserve unchanged-item revisions and explicit
   owner/parent context. Merely wrapping repeated full hashes in an envelope is
   insufficient.

3. **Keep checkpoint integrity and catalog authority distinct.** The existing
   manifest retains its exact artifact checks; it does not become a competing
   numeric-reference registry. Retain the catalog, trusted authority identity,
   source objects and provenance in checkpoint export/import. Missing, tampered,
   wrong-owner or inconsistent catalog/closure data must refuse. Candidate or
   cache bytes cannot establish their own authority. Preserve historical v1
   checkpoints and normalized evidence semantics.

4. **Apply the narrow source-dirt integration correction.** Task 6 may modify
   `.agents/ask/verification/traceability/evidence.py` only to classify this
   owner's generated `references/integrity.json` and
   `references/integrity.json.pending` as runtime metadata in `source_changes`.
   Preserve every other source check and trusted-catalog validation. The lock
   lives in Git metadata; no broader directory or lock-file exemption is needed.
   This source was already bound to both Task 6 cases. Its addition to Task 6
   ownership is committed and independently approved, but **not yet registered**.

These decisions exceed the delegated confidence threshold. Routine implementation
and fixture corrections need no further human choice. Escalate changes to feature
meaning, acceptance criteria, trust guarantees or a genuinely unresolved design
boundary.

## Pending registration: do once before production work

The original Task 6 source-binding amendment is already registered: checkpoint
and recovery readers bind both cases, and the attempt controller binds `6/1`.

The later ownership correction is committed at
`9ca83ed8ace0410339ea67880bebb27601f52fd6`; `plan.md` and the TaskGraph now include
the exact traceability source-dirt seam above. Its independent approval is:

- Reviewer: `/root/task6_plan_review`.
- Evidence: `inner-loop/evidence/task6-catalog-runtime-plan-review.json`.
- Decision: APPROVED, 97% confidence.
- Test-plan digest unchanged:
  `7470b02a5d97dab68e93c416a416f9810208b8ee0a5392a269479313bc5d36e7`.
- New TaskGraph digest:
  `3c8e40f7501dffc72feec3a476e9dcbfabfdce11726d93fdde08487792ad942f`.

Preserve attempt 2, interrupt it using the supported operation, register this exact
reviewed amendment with `traceability accept-plan --revision 9ca83ed`, commit the
accepted pin, and reopen Task 6. Keep the coordinator/task base attributable to
the reviewed metadata and retained Red tests. The coordinator `cas_apply` API can
advance the base with an explicit mutator; the CLI `cas-apply` is a no-op mutation.
Do not discard the existing Red test commits or manufacture a new Red merely
because ownership changed. Spec, mapped cases, source bindings and test-plan
semantics did not change in this amendment. If kit ceremony cannot represent the
already-authorized correction, use one documented bounded reconciliation under
the user's exception and restore normal checks afterward.

## Actual Task 6 test evidence

The definitive current Red is:

- Candidate: `9637cfec3d967d7d71ca5ef3c760b1947cd59d18`.
- Run: `6dc8863d8a5b456eafff0f40a1ee0df0`.
- Report: `traceability/runs/6dc8863d8a5b456eafff0f40a1ee0df0/results.json`.
- Both `6/1` and `6/2` failed with **behavior_assertion**, and the coordinator
  retained the run in its checkpoint.

Case `6/1` currently fails because checkpoint storage is v1 JSON rather than the
shared envelope. Case `6/2` reaches a missing numeric test-reference assertion;
its real disposable task-scoped runner already selects only the mapped case,
checks exact candidate/runner/log identities and rejects a tampered log.

Earlier run `7b08742352c941f9a8e940279a815f21` contains a fixture setup error and
is retained as diagnostic history, not valid Red for `6/2`. The initial `6/2`
roundtrip check was a passing compatibility guard. Those outcomes were not
relabeled. Fix/run fixtures locally before expensive pinned runs.

No Task 6 Green, production changes, integration or final verification exists.
Complete meaningful mapped behavior assertions, run relevant existing inner-loop
reliability/recovery regressions, obtain independent exact-candidate review, and
retain actual Green/integration evidence. Avoid repeated full-suite runs without
new changes or a concrete unresolved concern.

## Practical notes

The prior pinned-skill preparation exited 1: the optional frontend fetch failed,
and the generated Cursor TDD view/override was absent. The canonical repository
TDD override is `_ask/skills/tdd-override.md`; use available canonical instructions
and the user's procedural exception rather than looping on unrelated installation.
`./ask sync` passed. Run the access preflight and inspect current Git/state before
resuming; the handoff commit itself follows the source revisions listed above.

Normal recovery repeatedly reads a large retained snapshot. Process-local
memoization of immutable checkpoint reads reduced coordinator overhead without
changing validation predicates; clear that cache after each mutation. No production
performance refactor was introduced for this.

Work-branch pushing is authorized. The reconstructed checkpoint and accepted-tests
refs were also published, so retain and synchronize their closure when advancing
metadata. Preserve authority history and handle concurrent ref updates explicitly.
Final workstream verification, acceptance, Tasks 7–10 and integration into develop
remain unfinished.
