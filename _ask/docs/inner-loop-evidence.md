# Inner-loop candidate evidence and local state

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
history. It does not substitute for candidate verification. Exemption kinds:
`documentation-only`, `generated-projections`, `non-behavioral-config`.

The candidate must descend from the task's recorded base. Use the coordinator
checkout by default, or a task branch recorded in state and eligible for FF.
Prepare TaskResult after committing the candidate: its own full SHA cannot be
embedded in that same commit. State, results and execution/review evidence are
runtime paths; keep source/TaskGraph/intent changes committed. These runtime
exceptions apply only to `work/<work-id>/inner-loop/{state.json,state.lock,
.state-*.tmp,results/**,evidence/**}`. They do not exempt the whole workstream.

## Delegated review

The independent reviewer inspects the exact candidate, writes its decision in
an evidence artifact, and reports the verdict/boundary to the coordinator.
Review commits nothing. Under `_ask/policies/delegation.md`, the coordinator
records the delegated decision:

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

The coordinator snapshots its CheckPlan runner and Python imports from the recorded
coordinator base commit, then runs them against a clean detached worktree at the
immutable candidate SHA. Candidate changes to the verification implementation
do not replace the gate checking that candidate. The committed candidate CheckPlan and expanded
presets identify required commands. Worker-reported green codes and preexisting
VerifyResult files are not consumed as executed verification.

Outputs go into `inner-loop/evidence/verify-*/`: `output.log`,
`verification.json` and `integration.json`. Evidence includes candidate/base,
result digest, effective CheckPlan digest, runner base/digest, tree SHA, commands, exit codes and
paths. Failed checks, an empty mandatory plan, changed source or stale inputs
leave the task unintegrated. The coordinator revalidates inputs after checks,
then fast-forwards to the pinned candidate SHA and records the resulting SHA
and evidence in state. FF yields the exact tested tree, so no redundant second
run is required. Outer `09 Verify` and `10 Accept` still apply.

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
