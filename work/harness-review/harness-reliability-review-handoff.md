# Agent Starter Kit reliability review handoff

Review basis: 8 October 2026, Asia/Tehran

Repository: https://github.com/esmaeilzadeh/agent-starter-kit

Branch inspected: `origin/agent/inner-loop-hardening`

Commit inspected: `9602217d6e0f7d63dc9251ba8bd1673eb7d8f694`

## Purpose and conclusion

The harness is a promising way to improve Codex reliability on substantial, multi-session repository work. Its durable intent, explicit semantic-change process, task boundaries, verification runner, and result provenance address common sources of drift and premature completion claims.

This assessment is based on source inspection, not a comparative evaluation or a completed security audit. Two concrete implementation concerns deserve follow-up: integration evidence is accepted from reported fields, and the state revision update is not an atomic compare-and-swap operation. Improvements should preserve the existing low-interruption workflow and human authority over consequential decisions.

This handoff proposes work; no repository changes, test execution, or fixes were performed for this review. Branches may have moved since inspection. Compare current source with this revision before implementing.

## Existing strengths to preserve

| Mechanism | Expected benefit |
| --- | --- |
| Intent, spec, and plan lineage | Keeps goals and constraints available after long conversations or session changes |
| Explicit Spec Change | Makes semantic changes visible instead of changing requirements to suit implementation |
| Independent Spec Challenge | Provides another opportunity to identify misunderstanding and contradictions |
| Workstream artifacts and commit references | Supports recovery, attribution, and inspection of results |
| Defaults-OK with autonomous continuation | Allows execution without repeated blanket approvals |
| Executed CheckPlan | Gives verification a concrete command-based meaning |

In `.agents/ask/verification/run.py`, the runner executes configured commands, records exit codes and a commit SHA, and refuses an empty CheckPlan or zero mandatory checks. These are observed behaviors. Whether the configured checks establish sufficient correctness depends on the project and its CheckPlan.

## Finding R1 Bind integration evidence to the candidate code

Priority: high reliability concern; exploitability and end-to-end impact require validation.

Source: `_ask/scripts/inner_loop/driver.py`, particularly `check_integrable()` and `integrate_ready()`.

### Observed behavior

`check_integrable()` accepts TDD evidence when the reported red exit code is nonzero and the reported green exit code is zero. Alternatively, it accepts an exemption when its `reviewer_ack` field is truthy. `integrate_ready()` reads the result JSON, calls this check, and proceeds to integration.

The inspected check does not itself execute the reported commands or bind their results to the candidate commit. The acknowledgment field alone does not establish who reviewed the exemption or what authority they had. This is a finding about the inspected integration path; inspect the result producer, integration helpers, and other callers before concluding that no additional protections exist anywhere.

### Failure scenarios to validate

- A result from an older commit remains present after the task branch changes.
- A worker submits passing exit-code fields without corresponding executed verification.
- An exemption contains an acknowledgment but no attributable review decision.
- Task verification passes, but the integrated combination fails the required checks.

### Proposed change

Define an evidence contract containing work ID, task ID, exact candidate commit, relevant base revision, command/check identity, result, and evidence location. Use an appropriate coordinator-controlled execution or verification path rather than relying only on worker-supplied fields.

Before integration, validate that the evidence belongs to the candidate being integrated. Execute the required checks at a clearly defined boundary. If integration changes the tested tree, perform the required verification on the integrated result as well. Do not duplicate expensive checks when already trusted evidence applies to exactly the same candidate tree and environment.

Keep TDD history distinct from verification: a failing red test demonstrates a development step; successful required checks against the candidate establish its verification status. The exemption route should carry an attributable reason and acknowledgment from the reviewer authorized by existing policy. Do not introduce a new human approval for every exemption if existing policy delegates that authority.

### Acceptance checks

1. Evidence for a different task, workstream, or candidate revision is rejected with a specific reason.
2. Bare reported green exit codes do not substitute for the defined trusted execution evidence.
3. A valid exemption is traceable to its reason, reviewer, and applicable policy; an unsupported acknowledgment is rejected.
4. Required check failure prevents the task from being marked integrated through the normal path.
5. Successful integration records a consistent relationship among candidate, resulting commit, checks, and task result.

Decide whether the runner reruns checks or consumes trusted produced evidence before writing tests. The acceptance checks describe outcomes, not a mandatory implementation.

## Finding R2 Make state updates atomic under concurrent callers

Priority: high if overlapping coordinator processes are possible; otherwise document and enforce the single-process assumption.

Source: `_ask/scripts/inner_loop/state.py`, particularly `cas_apply()`, `cas_init()`, and `spawn_writer()`.

### Observed behavior

`cas_apply()` reads the JSON state, compares its revision with the caller's observed revision, mutates the document, and writes it using `Path.write_text()`. There is no lock or atomic transaction around that sequence in the inspected function.

Two callers could read the same revision and both pass the comparison before writing. Direct file replacement also lacks protection against partially written state if execution is interrupted. `spawn_writer()` checks for an existing running task before invoking the update, so its single-writer invariant depends on coordination across the read and write.

The environment-role check is a protocol check for cooperative callers, not an access-control boundary. Whether stronger isolation is needed depends on the threat model; do not expand scope into a security sandbox without a requirement.

### Proposed change

Choose and document the supported concurrency model. If multiple processes can touch the same state, serialize the full read, revision comparison, invariant validation, mutation, and write with a process-safe lock or transactional store.

For file-backed state, write a complete replacement to a temporary file on the same filesystem and atomically replace the state file while holding the lock. Atomic replacement prevents partial-file visibility but does not alone prevent lost updates. Put the running-writer invariant inside the protected transaction. Consider initialization races and specify crash recovery behavior. Select durability guarantees appropriate to the project rather than assuming atomic replacement guarantees persistence after every possible failure.

### Acceptance checks

1. Two concurrent updates based on the same revision cannot both succeed.
2. Concurrent attempts to start different tasks cannot create two running writers.
3. Readers observe valid complete state during writes.
4. Interruption before replacement leaves the previously committed state readable.
5. Existing resume, cancellation, and integration flows preserve revision and task-state invariants.

Use actual subprocess contention to check concurrency. A sequential stale-revision test alone does not reproduce the race.

## Review recommendation R3 Validate human intent independently

This is a design recommendation, not a demonstrated code defect.

Intent, spec, tests, and review can all inherit one misunderstanding. Agreement between generated artifacts does not establish agreement with the developer's original intention.

Use the companion `decision-review-harness-note.md` to add small behavioral and design decisions to existing stages. Ask for some expectations independently of the spec's proposed answers; map original requirements and consequential commitments to decisions and evidence; expose missing behavior as unspecified; reopen affected decisions when their assumptions change.

Preserve defaults-OK and existing escalation semantics. Do not require another blanket spec or plan approval. Keep whole-system walkthroughs alongside local cards so individually sensible choices do not conceal an incoherent design.

Pilot acceptance: a deliberately omitted requirement is surfaced, an unsupported assumption remains visibly unconfirmed, a changed accepted requirement uses Spec Change, and previously confirmed decisions do not cause repeated approval requests.

## Review recommendation R4 Scale artifact depth to task size

This is a usability recommendation requiring a pilot.

Keep the kit's required artifacts, authority boundaries, and verification checks. Allow brief artifacts for small changes and deeper reasoning for migrations, integrations, and architectural work. Define proportional depth using consequence, uncertainty, and reversibility rather than line count alone.

The existing process already seeks to avoid repeated approvals. Measure whether artifact preparation and model selection still impose unnecessary effort on small tasks before changing policy. A brief artifact must contain the required information, not merely an empty heading.

## Evaluation proposal R5 Measure whether the harness helps

The claim that this harness improves Codex performance remains an expectation. Evaluate comparable tasks with and without the harness, recording model/runtime, repository baseline, task, verification conditions, and human assistance. Include small corrections, medium features, interrupted work, and consequential integrations. Use equivalent acceptance checks for both conditions.

| Measure | What to record |
| --- | --- |
| Requirement fidelity | Missed constraints, semantic drift, and independently assessed acceptance failures |
| Correctness | Defects or regressions found by meaningful checks |
| Human effort | Review and clarification time plus unnecessary interruptions |
| Recovery | Successful resumption and time spent reconstructing state |
| Provenance | Whether results can be traced to code, spec, and executed verification |
| Delivery effort | Total elapsed time and resource use, interpreted alongside quality |

Use repeated comparable tasks when feasible; one successful demonstration cannot establish a general improvement. Establish baselines before inventing percentage improvement targets.

## Suggested work sequence

1. Reinspect current branch code and trace the complete evidence-production and integration path.
2. Decide the evidence trust boundary and supported state concurrency model.
3. Implement R1 and R2 with targeted failure and concurrency tests through normal kit workstreams.
4. Pilot interactive decision review using the companion note.
5. Evaluate correctness and developer effort before expanding the process.

Sequence related changes according to existing git-flow, clean-tree, commit, and workstream rules. Do not silently start competing branches or weaken acceptance criteria to unblock implementation.

## Copyable continuation prompt

```text
Review this handoff against the current origin/agent/inner-loop-hardening
branch. The inspected basis was 9602217d6e0f7d63dc9251ba8bd1673eb7d8f694.
Treat findings as hypotheses to confirm against the full call paths.

First trace TaskResult production, integration, verification, and state
mutation. Confirm whether candidate-bound evidence and concurrency guards
already exist outside the inspected functions. Report corrected findings
if the branch changed or other protections invalidate an assumption.

Follow the kit workflow for any implementation. Preserve defaults-OK,
human semantic authority, existing E2E contracts, one committing writer,
required verification, and commit/result lineage. Resolve only load-bearing
design questions with the developer. Use targeted tests for stale evidence,
failed checks, concurrent writers, and interrupted state writes. Record
executed evidence and remaining limitations; do not report a fix from
source inspection alone.
```

## Scope of this review

Inspected source includes stage and delegation contracts, workflow policy, `inner_loop/driver.py`, `inner_loop/state.py`, `inner_loop/allowlist.py`, `.agents/ask/verification/run.py`, and the verification wrapper. The review is selective. It does not establish the absence of other defects, successful execution of the branch, or a measured reliability improvement.
