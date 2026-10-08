# Harness reliability

## Status

CURRENT — prepared under the user's instruction to commit and continue without further permission requests.

## Intent and scope

Source: work/harness-review/intent.md and the reliability handoff. Repair R1/R2. This specification supersedes the TaskResult and concurrency clauses in inner-loop-hardening for future integrations; archived v1 results remain historical evidence.

## Evidence contract

Future TaskResult uses schema ask-task-result/v2 with work_id, task_id, base_sha, candidate_sha (full Git commits), existing TDD or typed exemption, and notes. At spawn record the coordinator SHA as task base. Candidate must descend from that base. Only the running task may integrate.

TDD retains seam, red/green command, output and integer exit_code (red nonzero, green zero); it is history, not executed verification. Typed exemptions are documentation-only, generated-projections or non-behavioral-config, with nonempty reason and reviewer_ack exactly true. Both routes require coordinator-recorded APPROVED review with boundary ok, reviewer identity, canonical delegation-policy pointer and an existing review artifact. The record binds work/task/base/candidate, the TaskResult bytes, review artifact bytes and exemption reason. A worker result cannot acknowledge itself. The coordinator may record REJECTED decisions; they cannot integrate.

Before integration, reject mismatched/missing identity, stale result/review, unsupported exemptions, wrong task status, non-descendant candidates, non-FF HEAD, and dirty source. Runtime state/results/evidence paths may change on the coordinator; other tracked or untracked source changes are refused.

Coordinator snapshots its CheckPlan runner and imports from the recorded task/coordinator base commit and executes them against a clean detached worktree of the exact candidate, not worker-provided commands or VerifyResult. The committed candidate CheckPlan must contain mandatory checks; existing isolation checks apply. Bind output to identity, CheckPlan digest, candidate, command/check identities, results and evidence location. Missing, failing or malformed execution output prevents integration. Candidate worktree must stay clean with HEAD unchanged after checks. Record failures as evidence without marking integrated.

Fast-forward only to the resolved immutable candidate SHA; require coordinator HEAD to equal candidate and verified tree before the state fold. No cherry-pick/rebase or redundant second verification when FF gives the exact tested tree. Record base/candidate/resulting SHA, checks and evidence path in state. Existing outer Verify and Accept remain.

## State concurrency and recovery

Support overlapping cooperative local POSIX processes. Persistent adjacent lock file uses process-safe advisory flock. Serialize the entire read/compare/mutate/invariant/write sequence. cas_init is idempotent and must never overwrite existing state. Validate at most one running writer inside every state transaction. All writes use a same-directory temporary file, flush/fsync it, and os.replace; no partially visible JSON. Readers need no lock. OS releases locks after process death; stale temporary files are harmless and are not promoted. Atomic replacement does not promise persistence across every filesystem/power failure.

Integration holds the state lock through validation, candidate verification, Git FF and the state fold. Resume repair also takes the lock. If a process dies after FF but before state replacement, the old state remains readable; retry may reverify and fold the exact same candidate. External/manual Git mutations and hostile repository writers are outside cooperative locking; detect drift where possible and escalate.

## Acceptance criteria

1. Wrong work/task/base/candidate and stale result or review artifact are rejected with a useful reason.
2. Bare green fields cannot replace executed mandatory candidate checks; a failing/empty plan leaves task unintegrated.
3. Exemptions require supported kind, attributable coordinator review, policy and reason; bare reviewer_ack is refused.
4. Successful in-place and FF integrations record consistent candidate/result/check lineage; source/ref drift and non-FF combinations are refused.
5. Two real processes applying the same revision cannot both succeed. Concurrent starts cannot leave two running writers.
6. Concurrent initialization preserves existing state. Readers observe complete JSON throughout updates; interruption before replacement preserves old readable state.
7. Resume/cancellation preserve revisions and single-writer invariants, including retry after FF-before-fold interruption.
8. Existing shell checks and full ./ask verify pass. Do not infer security or comparative performance from these tests.

## E2E

not_applicable: CLI/disposable-Git contract journeys belong to ask-kit. Test data: temporary repositories/state files. Reset: remove fixture directories after processes stop. No production datastore or external service.
