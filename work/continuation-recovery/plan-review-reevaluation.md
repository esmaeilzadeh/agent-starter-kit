# Recovery plan review: re-evaluation

Date: 2026-10-22.
Reviewed source: `7abccc8` (`plan: preserve task execution across continuations`).
Request: re-evaluate the plan review; the stop after planning remains in effect.
Coordinator review: `/root`. Independent focused review:
`/root/review_continuation_recovery_plan`, covering object retention/transfer and
bootstrap. Both reviews inspected existing implementation, not only proposal
wording. This document supersedes the original no-blockers verdict.

## Verdict

REQUEST CHANGES. The recovery direction is sound, but the proposal has three
high-priority design gaps and an incorrect test-source mapping. They are
planning blockers: the earlier approval treated unresolved persistence and
execution boundaries as implementation details without checking concrete
failure cases. A planning-only endpoint still requires these gaps to be visible.

The user has authorized review, not implementation or a rewrite of the recovery
requirements. Findings below identify the necessary proposal corrections. No
task state, executable contract or authority ref was changed by this review.

## R1 — P1: retain source and authority objects, not just their identifiers

Location: `plan.md:21`–`34`; affected cases CR-T05 and CR-T14.

Checkpoint commits are parented by previous checkpoints and contain JSON naming
source/base/candidate and authority commits. That records identities but does
not make the named Git objects reachable. Artifact blobs alone do not retain
their source trees, nor does fetching the checkpoint ref transfer commits named
only in JSON.

Counterexample: checkpoint a Green candidate and its exact review; later remove
its temporary branch while revising the task. After reflog expiry/pruning, or a
transfer without shared local objects, the checkpoint and logs survive but the
source commit can be absent. Recovery detects missing objects and blocks, so the
proposed durable recovery does not hold. Historical accepted authority commits
can also become unreachable: current `traceability/evidence.py:65` parents each
new authority by its source commit, not by the preceding authority commit.

Required correction: define reachable retention of the entire required Git
object closure (sources, candidates, contract/authority commits, trees/blobs)
and its atomic relationship to checkpoint publication. Specify transfer of that
closure while preserving the difference between historical provenance and
current acceptance authority. Extend tests to remove temporary refs, expire
reflogs, prune in a fixture, and transfer into a repository without shared-object
shortcuts before revalidating original Red/Green/review evidence.

Attribution: independent focused review, confirmed by coordinator inspection of
checkpoint parent proposal and existing authority publication code.

## R2 — P1: define a bootstrap that can admit the repair tasks

Location: `plan.md:68`–`86` and CR-4 sequencing; `tasks.yaml`.

The proposal defers real-workstream migration to CR-4, after CR-1–CR-3, and says
to merge the repair tasks into one executable contract first. It does not
specify how that transition works with this branch's existing state and graph.

Concrete checks, using only in-memory copies of the committed graph:

```text
Active graph: ok
Supplemental graph: ok
Combined graph without a specified transition/dependency amendment: path_conflict
Repair IDs missing from current state: ['CR-1', 'CR-2', 'CR-3', 'CR-4']
```

The merged graph has shared paths with product Tasks 5/6 but no dependency
relations between them. `state.py:114` returns existing state unchanged;
`spawn_writer` at line 131 then indexes an absent CR task. In addition, the
contradictory-history guard added by CR-1 could block admission of CR-2 on this
very workstream unless a bounded repair context is defined. Validating the
supplemental graph alone missed these issues.

Required correction: define a reviewed bootstrap before CR-1 using the existing
coordinator capabilities, preserving original attempts/evidence while suspending
product scheduling. Specify the executable dependency graph, contract/authority
transition, insertion of repair-task state, exclusive writer ownership and
handoff. The repair context must work with its own guards without declaring
old product tasks integrated or discarding their evidence. Add a scenario that
starts with the actual blocked ten-task state and reaches CR-1 and CR-2 admission.
Full legacy adoption may remain CR-4; the minimal bootstrap cannot.

Attribution: independent focused review and coordinator's read-only graph/state
comparison. No admission or state mutation was attempted.

## R3 — P1: settle checkpoint ownership across the locked, pinned verifier

Location: `plan.md:36`–`42`, `60`–`64`, `85`–`86`; CR-2/CR-3 boundary.

The plan requires checkpoint publication under the coordinator lock and hooks
at traceability run publication, while preserving the existing pinned verifier.
The current call flow has two relevant constraints:

1. `driver.py:97` holds `state_transaction` through `verify_candidate`. At
   `evidence.py:280`, the coordinator waits for a verifier subprocess. That
   subprocess calls `run_tests` (`verification/run.py:82`), whose publication
   currently uses its separate execution-ledger lock (`adapters.py:75`). A new
   synchronous run-publication hook that acquires the coordinator state lock
   waits for its parent, while its parent waits for it. Merely ordering the
   different locks does not resolve this same-lock parent/child cycle.
2. `snapshot_runner` (`inner_loop/evidence.py:195`) copies only the base
   revision's `.agents/ask/verification/*.py`. The proposed checkpoint module
   lives under `_ask/scripts/inner_loop/`, outside that trusted snapshot. Direct
   imports by a copied adapter would be unavailable unless the dependency is
   included; importing from the live candidate to compensate would undermine
   the stated pinned-runner boundary. The older pinned verifier also lacks new
   hooks when the first hook-adding candidate is verified.

These are counterexamples to unspecified hook placements, not a claim that the
unimplemented checkpoint hook currently deadlocks. The proposal must select a
concrete safe ownership boundary before implementation.

Required correction: choose who publishes/finalizes checkpoints for standalone
test runs, nested integration verification and legacy pinned runners; define
the supported handoff, crash boundaries, lock ownership and trusted dependency
snapshot. Add an end-to-end integration case with checkpointing enabled in the
real pinned verifier, plus interrupted standalone-run and ledger-finalization
cases. Do not rely on a direct `run_tests` test or an unbounded subprocess wait
to establish absence of deadlock.

Attribution: coordinator source/call-flow review. The initial review explicitly
deferred lock order and finalization, but missed this architectural boundary.

## R4 — P2: correct exact source bindings in the test mapping

Location: `test-plan.json`, CR-T10–CR-T16; `plan.md:90`–`95`.

CR-3's mapped source lists contain `evidence.py`, `state.py` and `driver.py`, but
omit the adapters/CLI where its new milestone hooks and admission behavior are
planned, along with recovery/checkpoint helpers on which the cases depend.
Recorded source identity would not account for all relevant production changes.

CR-T15/16 use `work/shorter-hashes/continuation-recovery/**` as a source path and
bind operational `state.json`. The actual runner reads every source path as an
exact file (`adapters.py:66` and `evidence.py:102`); it does not expand these
globs. A runtime state mutated during adoption is fixture/output evidence,
not a stable production-source binding. Converting the proposal's JSON shape
alone cannot make this mapping executable.

Required correction: bind the exact production and assertion-source files
needed by each case. Store immutable fixture definitions separately from
operational state/results and reference those fixture sources where relevant.
Replace wildcard entries with concrete file identities. Include source binding
and runner filtering in the executable-contract validation before approval.

Attribution: coordinator comparison of every mapped source list against owned
implementation paths and the runner's exact-file digest behavior.

## Review scope and next endpoint

The original scheduler reproduction and core requirements remain useful. This
review does not establish how the original runtime state was lost; it confirms
that the proposed recovery needs the corrections above. The distinction between
real historical execution and current integration eligibility remains valid.

Only the supplemental graph was previously validated; that check was accurate
but insufficient. The combined graph/state check above was read-only. No new
production tests were added or executed, and no aggregate verification,
implementation, checkpoint adoption or product completion is claimed.

Next planning action: revise the proposal and test mapping to resolve R1–R4,
then obtain independent review of the amended artifact identities. Implementation
and product resumption remain outside the explicit stop-after-plan endpoint.
