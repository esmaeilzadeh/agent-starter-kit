# Planning design for revising-workbench

PROPOSED implementation choices for [spec.md](spec.md), revision 2. This file
implements its vocabulary and constraints; it adds no acceptance authority.
Read this reference when implementing intake, selectors, migration or pilot proof.

## Versioned definitions and flow identity

Keep `validation.validate` as the shared entry. Dispatch on the exact model
schema, preserving the existing v1 parent/intent/lifecycle/reference rules.
V2 adds optional containment, `contributes_to` (task→story/scenario), `enables`
(feature→story) and the following explicit fields. Unknown fields still reject.

- Product key is `(model.work_id, node.id)`; retain baseline local node IDs.
- Task `execution` is `{work_id, task_id}`. Enforce uniqueness of this alias
  within its model; equal-looking local IDs supply no alias. Execution/readiness/
  verification projections retain separate named fields and their source owner.
- Active Scenario `case` is `{work_id, plan_digest, case_id}`. Here `case_id`
  selects the canonical test-plan test entry's `id` (for the pilot,
  `WB-evidence-identity`); that entry separately names the executable unittest
  selector in its own `case_id`. Display both with distinct labels. The canonical
  entry's `scenario` supplies concrete Given/When/Then. Draft without a case is
  inspectable with a missing-case limitation. `covers` requires exact selected
  case identity; criterion identity supplies only related-obligation information.
- For an explicitly reviewed alternate flow mapping, use an optional canonical
  test-plan `flow_mappings` registry of `{scenario_case, test_case, review}` entries.
  A case inside the containing plan uses `{scope:"local", case_id:<entry ID>}`
  with no containing-plan digest. Derive its qualified identity from the final
  externally reviewed enclosing plan's work ID and canonical digest. External
  selectors use `{scope:"external", work_id, plan_digest, case_id}` with the
  immutable target-plan digest. The mapping body is exactly `scenario_case` and
  `test_case`; normalize it as sorted compact JSON and hash those bytes, excluding
  the `review` envelope. `review` records that body digest and attributable
  independent APPROVED decision. Validate it in `flows.py` before projection;
  changed/unreviewed mappings or local selectors embedding their containing-plan
  digest reject. The outer reviewed plan binds the final registry and envelope.
  Neither containing-plan hashes nor review-including-itself hashes are embedded
  inside the plan. This is model coverage data, not new execution authority.
- Node `context` is a list of `{role, path, revision, selector}`. `role` is `spec`
  or `plan`; revision is an explicit commit or `snapshot` for captured current
  inputs. Record qualified source identity separately from execution identity.
- Node `source_context` is a list of `{path, revision, qualified_name, role,
  explanation}` for curated test/fixture/helper/global/import definitions.
  Curated explanations illuminate canonical assertions without editing them.
- Use the existing intent node as the optional Epic presentation, with a validated
  `definition` object holding user, purpose, outcome, scope and completion
  conditions. No intent means no recorded Epic. Stories/Tasks retain meaningful
  descriptions/outcomes. A workstream or branch never manufactures an Epic.
- A v2 `subject_association` records the qualified product/revision, bounded
  contribution, exclusions and execution owner. Foreign subject records are
  pointers resolved read-only in the owning model, never cloned product aliases
  or cross-model support edges. Keep optional external IDs/status availability
  as reference metadata without automatic joins or synchronization.

The reviewed migration proposal binds source model digest/schema/revision and
result model digest/schema, with an ID/reference preservation diff and independent
reviewer decision. Apply through the existing pre/action/post/publication guard.
Browsing never calls migration. An active historical v1 Scenario is still a v1
record; adoption of a v2 concrete-flow definition is explicit, not retroactive.

## Passage selectors and dependency discovery

Selector is a tagged JSON object; no free-form fuzzy query is accepted.

| Kind | Exact shape and resolution |
| --- | --- |
| Heading | `{"kind":"heading","path":["Work breakdown"]}`. Nonempty array of nonempty literal heading texts, normalized only by trimming outer whitespace/removing Markdown heading delimiters. Match the complete ancestor heading chain. Return heading through the next heading of equal/lower depth. Multiple matching chains stay ambiguous. |
| Plan task | `{"kind":"plan-task","heading_path":["Work breakdown"],"task_id":"WB-003"}`. Select exactly one Markdown table row under the uniquely matched heading, using its `Task ID` column; include the table header with the row. Zero/multiple rows stay unavailable/ambiguous. IDs are literal nonempty values, independent of product-node slug rules. |

Reject unknown kinds/keys, empty components, malformed structures, unsafe paths,
absolute/escaping/Windows paths and every symlink path component. Resolve only
regular repository files or regular committed blobs. Safe absent files and
well-formed zero/multiple matches remain admitted limitations. Surrounding text
comes from the same captured bytes/revision; no fallback heading or current file.

Extend snapshot discovery for all context/source-context/case/execution-owner
references, including missing targets. Identity includes source bytes or missing
state, selector, exact match count/state, dependency-discovery version and passage
rule version. Preserve one validated generation for all readers. Missing target
creation/deletion, linked-only edits, helper edits and unique-to-ambiguous changes
must invalidate identity even with unchanged file mtime.

## Actions requiring passages

Keep the existing mutation/workflow guard and last-validated inspection authority.
Maintain a stage-local entrypoint registry and extend it in the introducing task.
RWB-102's context integration test executes only already-existing foundation
entries: semantic edit/batch/resolve/revise, model admit-with-action, task workflow
admission, inner-loop candidate admission/integration, traceability contract/review
operations and explicit repair/import boundaries. RWB-103 extends it with the real
subject-association path. RWB-108 extends it with real migration and representative
admission/completion gates. RWB-107/RWB-109 exercise the exposed UI decision path.
Their final union covers every adopted public entrypoint. Earlier tasks do not
require successor functions or synthetic future stubs for their final green;
existing wrappers remain responsible for their own gates.

| Action | Passage dependency |
| --- | --- |
| Inspect/navigate/context resolve | None. Display admitted limitations. Invalid input permits explicitly labeled untrusted diagnostics and last-validated inspection. |
| Resolve an existing decision/revise unrelated node | None by default; a decision carrying explicit contract context depends on that context. Safe absent Task context alone cannot disable this unrelated action. |
| Admit implementation for a selected planned Task | Its selected spec context and actual plan-task passage; refuse until both resolve uniquely. Unplanned Task inspection remains legal. |
| Publish confirmed subject association | The bound subject identity/context revision; any explicitly referenced contribution contract passages. A standalone proposal needs no invented ancestor passage. |
| Publish v2 migration | Its reviewed source/target definition identities and any context explicitly named as migration contract; existing unrelated optional gaps do not block. |
| Representative demonstration admission/completion | Both named baseline spec passages, exact WB-003 plan row, selected canonical flow and all necessary source/helper/fixture/evidence identities, plus valid successful human record. |
| Explicit repair/import | Validate the entire proposed replacement under the existing repair/import boundary; ordinary actions remain blocked on invalid current input. |

Declare required context by action argument/contract, not by silently treating all
context refs as globally mandatory. Never let a caller's label bypass pre/post
checks. The stage-owned registry tests execute each real entry available at that
stage, compare full/cached validation, and assert one ordered pre/action/post/
publication trace for each successful mutation and no action/publication on the
appropriate failure. RWB-108's representative passage case proves context refusal
and names remaining genuine-evidence/human prerequisites after context resolves;
it does not fabricate successful comprehension. The mandatory successful real
browser and human demonstration remains RWB-109.

## Actual fresh-context intake caller

The current kit stages are instructions, not a hidden executable coordinator.
Add `_ask/scripts/stage-intake.py` as their narrow read-only coordinator adapter.
The canonical 00/01 stage instructions invoke it with `--stage 00-explore` or
`01-grill` and a structured request file before selecting/creating execution work,
recording intent or delivery admission. Sync generated Codex skills and Cursor
commands/skills from those stages. Runtime agent configs already point to the
canonical stage files and require no new model mapping.

The adapter calls `engineering_model.context.resolve`, returns the qualified
subject/revision, relationships, contribution/exclusions, execution owner and
`resolved`, `needs_clarification`, `chooser` or `unavailable` disposition. Explicit
subjects win over a valid recorded association; materially conflicting owners or
explicit identities return clarification. Branch only locates execution records.
Inspection and resolution are read-only, including no admission-state publication.

Fresh-process tests drive this adopted adapter with no prior chat/session state,
probe its real resolver invocation and assert it precedes existing branch/intent/
admission boundaries. Replay both canonical stage intake contracts; assert stage
and generated instructions actually bind this caller. A resolver unit test or a
`./ask model context` parity test cannot satisfy this boundary. Protocol compliance
by an arbitrary external LLM is outside a deterministic test; the shipped adopted
caller and its stage binding must both be exercised and independently reviewed.

`./ask model context` exposes that shared resolution for inspection. After a human
confirms an association, use a semantic `associate_subject` batch through the
existing guard and record its bound context in intent. Material edits to complete
intent invalidate its confirmation and follow the existing workflow. The adapter
does not create a fresh-work orchestration command, branch, intent or assignment;
parked fresh-work automation remains outside this plan.

## Genuine representative evidence access

Use exactly the sources/identities in spec.md's Representative Story table,
including source candidate `70dd295aacff869857081a94870d02fcbf4d640c`, red run
`111e0f24d5e448c387cd1558b864b18e` and final-green run
`799924ec199b4717a3eabf4fb39a1bdc`. Resolve the canonical case from the inspected
old plan digest; select the original `test_engineering_workbench_evidence.
WorkbenchTests.test_results_match_work_test_run_and_contract` executable selector
without renaming or reassigning that historical record to this work.

Find required report/log paths through the original TaskResult and execution
ledger, and evaluate their full digests, contracts, reviews, sources and accepted
authority through the existing evidence evaluator. TaskResult output text alone
is insufficient. Read spec/plan at their declared revisions, and test helpers at
the selected historical test revision, including `setUp`, `_report`, `_ledger`,
`_blob_digest`, `git`, `write`, `commit`, fixture values and imported boundary.
Current fixture-generated observations never replace the genuine execution.

The traceability adapter runs code in a detached candidate where untracked old
runtime logs may be absent. Tests use explicit `ASK_RWB_RETAINED_ROOT` pointing to
the original repository as a read-only retained-evidence/source authority. UI
loading separates current candidate model/code from that qualified historical
inspection root. No tests admit or edit that root; use source snapshots for read-only
historical display and temporary repositories for all write journeys. Record
before/after source/evidence/ref identities. Missing report/log/ref/review authority
fails the mandatory genuine pilot cases with its exact prerequisite. Do not create
fake old authorities or update the old work's accepted ref to obtain green.

A source-only transfer may need separate reviewed local registration of preserved
historical authority according to traceability policy. That is a prerequisite
outside the product inspection operation, never automatic browsing or a test
fixture standing in for history. The new work always receives its own reviewed
spec/TaskGraph/test-plan pin; none of these historical records approves it.

## Human record and final candidate

Use a versioned `ask-workbench-comprehension/v1` runtime record under
`work/revising-workbench/traceability/readability/`. It records candidate SHA,
model snapshot digest, qualified Task/Scenario/Test and canonical plan-case key,
inspected source revisions, spec/plan selector+byte digests, test/helper/fixture
source digests, retained report/log/contract identities, exercise timestamp,
returning-human identity, independent assessor identity, `chat_assistance: false`
and ten individually attributable answer/assessment entries. The ten prompts ask
for purpose, spec context, plan context, concrete flow, setup, action, expected
observation, assertion, actual outcome and applicability. Each entry retains the
human's answer, pass/fail, assessor reason and evidence link. Preserve failed
attempts; all ten must pass in a fresh matching record for success.

Freeze candidate source (including candidate documentation) before the exercise.
Run the representative browser journey, let the returning human answer from the
workbench without chat assistance, then record the independent dispositions.
`ASK_RWB_HUMAN_RECORD` supplies that runtime record to the immutable-candidate
completion test. The automated test checks binding/gating; it cannot generate
answers or certify comprehension. Missing/failed/stale record blocks demo and
workstream completion. Relevant definition/context/source/helper/fixture/evidence
changes invalidate it and require a new exercise. Escalate an unresolved failure
for a scope decision only through Spec Change, without silently marking it pass.
Runtime evidence archival cites the tested source SHA and does not redefine it.

## RWB-102 explicit caller wiring amendment

Keep one shared guard. Extend its admission inputs with an explicit selected
product Task or qualified execution Task, validated against the captured model.
Execution aliases resolve only by the declared `(work_id, task_id)` pair; equal
node IDs, branch names, labels, tracker references and an ambient running task do
not establish an association. Reject contradictory or malformed supplied
identities before action. A caller with an explicit selected Task cannot opt out
of its required spec and plan-task passages by relabeling its action. Generic
unrelated semantic/decision operations retain their own admission semantics and
remain possible despite safe optional context gaps.

Thread selected task inputs where the real caller already possesses them:
inner-loop driver selection/integration, integration and review CLI/direct
boundaries, task-scoped traceability run/completion/review, the verification
workflow bridge and explicit model admit-with-action. Add explicit CLI arguments
only where the public operation needs a subject input it previously lacked.
Retain backward compatibility for v1 and truly unselected inspection/unrelated
actions. Current generic contract-review operations continue validating full
canonical inputs without manufacturing a product-task association.

Tests enumerate actual adopted foundation entrypoints and execute their success,
invalid/stale and required-context refusal paths through temporary owned repos.
The trace binds ordered pre-check/action/post-check/publication to captured input
and result identities; nested validation must preserve one logical outer action
and publication. Caller labels, fake traces, mocked actions standing in for real
entrypoints, call-stack introspection and global running-task inference cannot
satisfy this registry. Existing explicit recovery boundaries retain their own
replacement validation; no nonexistent import command is introduced.

The verification runner change is limited to carrying the explicit selected
identity through `workflow_context`; immutable-base candidate verification,
coordinator authority, case instrumentation, CheckPlan execution, integrity and
FF-only integration remain enforced. Direct coordinator evidence/review helpers
must retain the same task identity and guard semantics as their CLI wrappers.
Independent review must assess both this scoped tooling amendment and the
resulting actual caller tests before task integration.

## RWB-103 foreign-observation publication amendment

The shared publication helper is part of the existing action safety boundary.
For subject association, capture the foreign owning-model observations alongside
the local snapshot and carry them through recovery and publication. Recheck them
after local recovery writes, after generation staging, before publication event
creation, and immediately before replacing the current pointer. If a foreign
input changes after local writes, restore the prior local bytes, clear the
recovery journal, and leave the current pointer unchanged. The real association
test must inject a foreign save after the local write and assert refusal,
rollback, and no publication. This is an ownership/completion-evidence
amendment to RWB-103; it does not change the product criteria or test registry.
