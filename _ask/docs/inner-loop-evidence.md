# Inner-loop candidate evidence and local state

Task lifecycle and finding classification are defined in
`.agents/ask/task-loop.md`; this document defines the state/evidence mechanics
that support that lifecycle.

This is the operating contract for future inner-loop results. Historical
`ask-task-result/v1` files remain review records; the runner refuses them for
new integrations. Implementation: `_ask/scripts/inner_loop/`.

## Worker submission

The coordinator starts one ready task and records its `base_sha` in state.
The worker commits its source changes, then writes
`work/<work-id>/inner-loop/results/<task-id>.json`:

```json
{
  "schema": "ask-task-result/v2",
  "work_id": "example",
  "task_id": "docs",
  "base_sha": "<full recorded task base commit>",
  "candidate_sha": "<full task candidate commit>",
  "tdd": null,
  "exemption": {
    "kind": "documentation-only",
    "reason": "Only explanatory prose changed",
    "reviewer_ack": true
  },
  "notes": ""
}
```

Behavior changes use `tdd: {seam, red: {command, output, exit_code}, green:
{command, output, exit_code}}` and `exemption: null`. Red is an integer nonzero
exit; green is integer zero; both carry captured output. This records TDD
history. For behavior tasks, also include the report from the pinned task
runner:

```json
"verification_report": {
  "schema": "ask-task-verification-report/v1",
  "candidate_sha": "<same full task candidate commit>",
  "run_id": "<pinned runner run ID>",
  "report_path": "work/example/traceability/runs/<run-id>/results.json",
  "sha256": "<SHA-256 of report bytes>"
}
```

The report reference does not replace the TDD history. Exemption kinds:
`documentation-only`, `generated-projections`, `non-behavioral-config`.

The candidate must descend from the task's recorded base. Use the coordinator
checkout by default, or a task branch recorded in state and eligible for FF.
Run the accepted task-scoped test runner after committing the candidate, then
place its report reference in TaskResult before requesting review. The
candidate SHA already exists, so TaskResult can bind the immutable report
without a digest cycle. Commit meaningful progress as one compact
`work/<work-id>/progress/<task-id>.json` per task using
`./ask inner-loop publish-evidence <work-id>`. The publisher reads authenticated
checkpoint history, preserves rejected reviews, correction submissions, attempts,
unattached historical runs and integration receipts, and excludes commands, raw
output and free-form private prose. Supporting digests retain links to full local
evidence, including notes. Git retains each public record's earlier versions.

The driver publishes after integration and before the next writer. Publication
failure blocks that writer. A running task, including a separate task ref, defers
publication until integration or explicit interruption; its intermediate evidence
remains checkpointed. Do not rebase an approved candidate for a progress commit.
The next writer starts from the publication commit; the source candidate SHA
continues to identify the tested/reviewed source. Publication receipts in the next
checkpoint map source, record digests and publication commit without a hash cycle.
Exact staged and postcommit retries complete once; an unchanged rerender creates
neither a commit nor a state revision. Pending tasks may be backfilled after a
reviewed recovery adoption; arbitrary source advances are rejected.

`./ask check-clean` accepts known runtime cache paths only when their bytes and
file types match a valid retained checkpoint and matching state cache. It checks
ignored runtime files too. Staged runtime files and all progress/source changes
remain dirty. Arbitrary authorization/review Markdown remains stageable. An empty
known state lock is permitted; forged, missing or corrupt retention is refused.
Use `inner-loop migrate-runtime <work-id> --inventory <json>` only with an explicit
reviewed `{checkpoint_sha, paths: {path: sha256}}` inventory. It removes only exact
retained runtime entries from the index, preserving worktree bytes and Git history.
Commit that migration with its inventory; do not blanket-untrack work directories.

Raw outputs stay in private repo-relative runtime caches and local checkpoint
refs. Keep raw-bearing exports/snapshots outside normal source commits and public
bundles, with directories 0700 and files 0600. Checkpoint capture/restore and
traceability verification keep their existing path contracts. Local checkpoint
refs are never automatically pushed. Missing matching raw output blocks dependent
verification; a public summary cannot substitute for it.

## Moving work to another machine

A normal clone or branch push transfers source and committed progress summaries.
It does not transfer `refs/ask/inner-loop/<work-id>`, accepted-test authority,
authority history, or the workflow reference catalog. Copying `work/` alone
does not restore those refs. Keep the source commit and checkpoint identity in
the committed handoff so the receiving machine can check both.

On the source machine, export the retained checkpoint to a private directory:

```sh
mkdir -p -m 700 /private/askit-transfer
./ask inner-loop checkpoint-export <work-id> --out /private/askit-transfer/work.bundle
git bundle list-heads /private/askit-transfer/work.bundle
```

The bundle includes the checkpoint's progress/evidence and source object closure,
the workflow catalog when present, `refs/ask/accepted-tests/<work-id>` and its
history. Export publishes a mode-0600 file atomically. Transfer that file through
a private channel, then on the receiving machine check out the handoff's source
commit and run:

```sh
./ask inner-loop checkpoint-import <work-id> /private/askit-transfer/work.bundle
./ask inner-loop status <work-id>
ASK_WORK_ID=<work-id> ./ask verify
```

Import validates the checkpoint and restores authority refs with the checkpoint
in one ref transaction. Conflicting local authority is rejected and preserved.
Status restores the retained runtime cache, including progress and raw outputs.
The bundle contains the last retained checkpoint, not newer unretained runs.
Retain new evidence through the normal reviewed checkpoint operations before
exporting it. Export again with current tooling if an older bundle omitted
accepted-test authority; do not recreate approvals on the receiving machine.

## Delegated review

The independent reviewer inspects the exact candidate, writes its decision in
an evidence artifact, and reports the verdict/boundary to the coordinator.
Review commits nothing. Under `_ask/policies/delegation.md`, the coordinator
records the delegated decision:

For broader-refactor suggestions, the same candidate-bound review artifact is
the durable handoff. Include stable slug, source task, reviewer/finding
identity, candidate SHA, affected responsibilities, proposed What/Why, and
publication status. Do not materialize a `.later` source card until every task
candidate is integrated and no writer or resumable candidate remains; dedupe by
slug and substance at publication.

```sh
./ask inner-loop record-review example docs \
  --reviewer review-agent-identity \
  --evidence work/example/inner-loop/evidence/docs-review.md \
  --verdict APPROVED --boundary ok
./ask inner-loop run example
```

`record-review` also accepts `REJECTED`, and boundaries `extras` or
`glob_too_narrow`; only APPROVED/ok can integrate. The canonical delegation
policy must exist. State binds the reviewer, policy, review artifact bytes,
TaskResult bytes, work/task/base/candidate and exemption reason. Changing any
bound input requires a fresh review record. Worker-supplied approval or
`reviewer_ack` alone has no integration authority.

This is cooperative protocol attribution, not identity authentication. A role
environment variable does not isolate a hostile process with repository access.
No new human acknowledgment is required for each delegated exemption.

## Candidate execution and integration

The run report is the output of the accepted task-scoped runner at the
committed candidate SHA. Add its run ID, path, candidate SHA and SHA-256 to
TaskResult before recording the independent review. During integration, the
coordinator validates the report against the task base runner, accepted test
plan, source digests and complete case inventory. It records that report in
state and writes a separate integration receipt without running the test
commands again. TaskResults without a report reference retain the compatibility
verifier path. Verifier upgrades remain checked by the previously accepted
verifier and their separate upgrade tests. Outer `09 Verify` and `10 Accept`
still apply.

The `integrate --task-ref` primitive only performs Git FF; it does not verify
or mark a task integrated. Use `run`/`resume` for the normal evidence-gated flow.

## Local concurrency and recovery

Cooperative local POSIX callers serialize transactions with an adjacent
persistent `state.lock` using `flock`. Keep that lock file in place. Initialization
returns existing state unchanged. CAS compares revisions under the lock;
a conflict means the caller must reload before deciding whether to retry.
At most one task can be running, including after arbitrary CAS mutations.

Complete state files are flushed to a same-directory temporary file and
atomically replaced. Readers see complete old or new JSON. Process death
releases the lock; abandoned `.state-*.tmp` files are harmless and never
promoted. This does not promise multi-host locking or universal power-loss
durability.

Integration holds the same lock across verification, FF and state replacement.
If interrupted after FF, retry/resume revalidates the exact candidate and folds
its state; runtime-only dirt does not trigger a reset to the old base. A
concurrent cancellation/update waits and may report a revision conflict.
Source/Git repair preserves runtime paths even when they are tracked: it clears
operation metadata, moves the coordinator ref and restores source paths only.
An in-place TaskResult invalidated by that repair is refused until resubmitted;
its recorded review and state revision are retained. External/manual Git writers
remain outside this advisory coordination model.

Checkpoint recovery keeps retained execution evidence byte-identical and accepts
only append-only execution-ledger rows. A changed model-state pointer is carried
forward only when the selected generation and every publication since the retained
boundary validate as a guarded edit; ordinary admissions and unlinked files need
an exact reviewed adoption. A changed completion projection must match retained
passing verifier evidence or reproduce as a canonical failed report. Preserved
historical failure diagnostics are not passing evidence and require reviewed
adoption when their original contract is no longer current.

### Reviewed recovery adoption

Use `recovery-propose` to create a read-only proposal, then retain its exact
bytes and the independent review under `work/<id>/inner-loop/evidence/` before
`recovery-adopt`. The review binds the proposal digest, source candidate, and
continuity digest. For this workstream, record the approved native reviewer as
`gpt-6.1-sol (medium)` with `reviewer_model: gpt-6.1-sol` and
`reviewer_effort: medium`. The command accepts only those exact proposal and
review files as untracked evidence; other staged, changed, or untracked source
blocks adoption.

Reviewed adoption does not waive projection checks. Completion reports still
pass the completion validator, and model-state pointers, selected generations,
blobs, and publication records must remain structurally valid and match the
reviewed inventory. The adoption receipt stays authoritative through descendant
checkpoints when the coordinator advances from the adopted source commit.
Ordinary inspection, CAS, and writer admission gain no authority from proposal
files on disk.

## Structured spec-to-test gate

Normal integration also validates the task subset of the accepted JSON spec/test
plan through `_ask/docs/spec-test-traceability.md`. The pinned coordinator runner
must support `ask-traceability/v1`; otherwise integration reports `migration_required`.
Candidate-bound traceability records live under `work/<work-id>/traceability/`
and are preserved with other runtime paths on recovery. Task success cannot
substitute for final workstream completion. Existing R1/R2 history stays archived.

## Legacy reconciliation proposal

The legacy audit reads the selected product commit from Git and records runtime
artifacts found only in the current checkout as `checkout_only`. It does not
rewrite the legacy state, accepted-tests authority, test classifications, or
task schedule. A proposal binds the audit and exact preimages; validation refuses
a moved product ref or authority, an active task, an unsupported verifier, or
an independent review that does not bind the proposal bytes.

Task review evidence is checked against its retained file digest and candidate.
Older state does not record who persisted the review, so the audit reports
`independence_unverifiable` instead of treating a reviewer name as proof of
independence. Candidate changed paths come from the exact Git base-to-candidate
diff; unrelated checkout changes are excluded.

```sh
mkdir -p work/continuation-recovery/adoption
./ask inner-loop legacy-audit shorter-hashes \
  --ref refs/heads/agent/shorter-hashes \
  > work/continuation-recovery/adoption/audit.json
./ask inner-loop legacy-proposal \
  --audit work/continuation-recovery/adoption/audit.json \
  > work/continuation-recovery/adoption/proposal.json
./ask inner-loop legacy-validate-adoption \
  --audit work/continuation-recovery/adoption/audit.json \
  --proposal work/continuation-recovery/adoption/proposal.json
```

Validation only checks whether a separately reviewed proposal still matches its
preimages. It does not apply the proposal or start product work.
