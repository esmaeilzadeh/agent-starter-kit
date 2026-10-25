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
without a digest cycle. State, results and execution/review evidence are
runtime paths; keep source/TaskGraph/intent changes committed. These runtime
exceptions apply only to `work/<work-id>/inner-loop/{state.json,state.lock,
.state-*.tmp,results/**,evidence/**}`. They do not exempt the whole workstream.

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
