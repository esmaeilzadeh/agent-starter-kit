# Plan: validated Engineering Model, then interactive workbench

## Current follow-up plan: tabular inspection and approval choices

Status: READY FOR HUMAN MODEL SWITCH. Stop after this planning checkpoint; the human will switch to Luna before UI implementation. This section supersedes the historical status/handoff below. Continue on `agent/structured-agentic-environment`; do not start another workstream. The approved intent is `intent.md`, with the exact human reply recorded in `intent-confirmation.json`.

### Completed approval-process checkpoint

Commit `a838212` adds `./ask confirm-intent --work-id <id> --choice approve|revise`. A submitted approval choice is stored as `ask-intent-confirmation/v2` with `human_choice: approve`, the complete-intent scope/prompt and intent digest. Requesting revisions cannot create or replace approval. Existing v1 text records remain supported; exact typed `approve` now works. Choice and text inputs are mutually exclusive. Missing/stale approval and non-affirmative recorded choices still fail the gate.

Grill/Implement sources, workflow policy, dispatcher help and generated bindings instruct agents to offer “Approve complete intent and assumptions” / “Request changes” through the runtime choice control. A preselected option is not submission. Record an explicit text reply exactly when the human uses text or choice controls are unavailable; do not ask for special spelling after a clear approval.

Targeted validation passed: `bash _ask/tests/test-check-workstream-confirmation.sh` covers legacy records, exact `approve`, approval choice, revision refusal without replacing the prior record, conflicting inputs, non-affirmative recorded choice and stale intent. `./ask check-workstream structured-agentic-environment` passed. Full Verify and independent review remain pending.

### Remaining sequence after the model switch

1. Recheck the clean checkout and current confirmation. EM-005/EM-006 already cover the workbench and selection safety; keep their accepted test-plan contract intact and add table/row-selection assertions to the already-mapped UI tests. Preserve canonical scenario/evidence authority and evidence history; disclose test chronology gaps.
2. Maintain the table/detail AppTest and browser cases added before the UI changes. Cover empty collections, long/nested values, missing/historical evidence, workstream changes, refresh and evidence-candidate replacement. Use disposable fixtures; do not mutate committed pilot data.
3. Replace text-list and JSON-first inspection with native read-only `st.dataframe` sections, readable column headings and hidden indexes. No editable-grid widgets, framework replacement, CSS, domain/schema changes or training-run viewer changes.

   | Section | Table columns | Selected-item details |
   | --- | --- | --- |
   | Tasks | ID, title from existing node map, status, lifecycle, blocker count | Full blocker IDs/reasons, task description/reference |
   | Engineering objects | ID, type, title, lifecycle, reference | Full description/reference/history, declared options, existing decision form |
   | Scenarios/planned tests | Scenario ID, title, canonical reference, availability, test count | Complete Given/When/Then, test/case IDs, runner/type/source references, assertions, nested evidence |
   | Evidence | Workstream, adapter status, candidate/current SHA, historical, current completion | Complete errors, criterion/test/outcome/provenance details; collapsed raw JSON for debugging |

4. Single-row selection opens each section's detail panel. Map selection to stable IDs using the displayed table's source rows, never a separately reordered list. Handle no selection/empty tables. Namespace/reset selection on workstream, displayed snapshot and evidence-candidate changes so an old row index cannot point to another item. Selecting a row must not recapture concurrent inputs or weaken stale-form protection. Keep workstream selection, refresh, candidate inspection and guarded decision submission.
5. Adapt tests that assert old text-list status or use the object selectbox to the table interaction. Assert actual table values and detail content, not widget presence alone. Retain decision persistence/new-session reload, stale spec-only rejection, refresh recovery, gitless roots and historical candidate inspection. Real-browser tests exercise row selection; AppTest cannot substitute for unsupported browser interactions.
6. Run the targeted UI and browser suites against disposable fixtures/temporary processes. Capture a screenshot of the implemented table/detail view for the final handoff. Remove only test-owned server/browser resources.
7. Commit meaningful slices on the current branch. Obtain independent candidate review, address findings, run `./ask verify`, and record candidate-bound results through `./ask record-result`. Prepare verification, review/context-audit and acceptance evidence. Human Accept is separate; this planning request authorizes no merge/push.

### Completion criteria, ownership and escalation

All four sections are readable tables; selecting a row opens the correct complete details; raw evidence JSON is collapsed by default. Missing/historical evidence remains honest and candidate inspection stays read-only. Existing refresh, validated snapshot display, attributed decision persistence and stale-state rejection continue to work. Approval uses submitted choices where available and accepts clear text approval without requiring special wording.

UI ownership: `_ask/ui/streamlit_app.py`. Verification ownership: `_ask/tests/test_engineering_ui.py` and `_ask/tests/test_engineering_ui_browser.py`, with fixture extensions only where necessary. Contract changes stay in the existing workstream/spec/test artifacts. The completed approval checkpoint owns only the dispatcher, recorder/test, workflow policy and stage-source/generated binding changes already committed.

Escalate if row selection requires model/schema changes, loses complete evidence, changes completion authority or cannot preserve captured-view freshness. Full verification and independent review remain pending. The tabular UI is not implemented at this checkpoint. Resume only after the human switches models and asks to continue.

## Historical foundation plan

## Status and stopping condition

PLAN ONLY. The human requested “continue till you give me a plan.” This document incorporates the subsequent validator requirements; feature implementation must not continue in this turn. The original interrupted scaffolds are non-executable drafts under `drafts/`, not delivered code or executed tests.

Exactly one specification: `specs/current/structured-agentic-environment.md`, revision 2 criterion contract in adjacent JSON. Decision provenance: `spec-change-validation-guard.md`. Independent challenge and exact contract identity are recorded in `spec-challenge.md` before handoff.

## Already available

- Completed harness-review supplies canonical criteria, reviewed test plans, assertion mappings, actual case evidence and completion policy. Reuse it; do not rebuild it or add a competing authority.
- Current task-fit Codex models and explicit efforts were independently reviewed and fully verified at `6745afe`; their prerequisite branch is incorporated into this work branch.
- Local `main` and `develop` already include the completed harness baseline. This plan stays on `agent/structured-agentic-environment`; no new merge/push to either integration branch is implied.
- No broader Engineering Model, document-state guard or interactive workbench is implemented. The existing structural contract checker is not the future document-state validator.

## Design commitments

Definitions remain revisioned with their code. Markdown, agent context and UI are projections. Existing criterion/test/code/evidence/runtime authorities remain separate and explicit. The shared document layer owns all structural validity and safe mutation; the UI consumes validated state and contains no graph/link repair logic.

Guard contract: **validate current state → stage action → validate resulting state → recheck freshness → publish stable snapshot**. A failed pre-check prevents action invocation. A failed post-check or stale input preserves the last stable generation. One action may stage several coordinated file edits; consumers never observe a partial multi-file state.

Scope is one local cooperating developer/repository pilot. Actor attribution is not authentication; local locks are not distributed transactions. Bootstrap and external edits are explicitly covered, not assumed valid. No numerical latency guarantee or performance advantage is claimed.

## Milestones and exit criteria

### 1. Fix the language-neutral model and validator contract

Define the types, stable IDs, legal relationships, cardinalities, lifecycle rules and external references in the specification. Document each fact's authority. Establish a machine interface for validation diagnostics, validated snapshot identity, action proposals and projections. Freeze the public interface, not a Python implementation.

Inspect existing schema/validation tooling and available toolchains. Benchmark the actual pilot plus reproducible 100/1,000/10,000-node graphs with recorded edges/file counts, valid/invalid links and cycles. Measure cold/warm p50/p95, peak memory and parsing/I/O/graph costs; later repeat for the complete pre/post path. Compare suitable existing fast tooling and a native implementation when warranted, without building several full production backends.

Exit: reviewed model/interface contract and recorded implementation/tool decision with workload and measurement rationale. If tool/language choice changes runner selectors or source bindings, independently review and amend the accepted test contract before implementation. No “Python only” restriction and no assumed native speedup.

### 2. Implement the independent document-state validator

Validate schema/field types, identity uniqueness, reference existence/type, relationship/cardinality rules, containment/dependency cycles and lifecycle consistency. Validate the relevant specification/reference closure, not only the engineering-model file. Return deterministic diagnostics naming offending IDs/paths; validation is nonmutating.

Use the selected fast tooling/language behind the shared interface. Keep full validation available. Add indexing or incremental work only where benchmarks justify it; compare every optimization against full validation, including global invariants and changed/deleted/new reference targets.

Exit: real assertion-red then green for valid models and negative invariant/reference cases, independently callable validator, reproducible baseline measurements. The UI has not started.

### 3. Enforce stable state before and after every action

Implement the shared local action guard. Capture the current dependency/input snapshot and validate it before invoking a state-changing engineering action. Stage edits in isolation; validate their resulting state. Recheck base identities under the single-writer/CAS rules and publish one validated immutable generation/manifest. Bind identity to input content/paths, dependency discovery and rule version; a model-only digest or file timestamp is insufficient.

The publication unit is the complete document snapshot, including coordinated spec/model edits. Readers use that generation's bytes. Ordinary working-file writes may be visibly uncommitted, but cannot become consumer authority before the guard succeeds. Define crash/interruption recovery around the publication pointer; never claim several independent file renames form an atomic transaction.

Connect managed spec saves and workflow-action admission to the guard for the adopted pilot. A document-layer change observer validates external spec saves; startup and read/action entry freshness checks recover from missed events. If external writes leave invalid state, block ordinary actions; show only an explicitly last-validated, noneditable snapshot until explicit repair/import is validated. Bootstrap validates the starting repository before admission. This does not silently migrate other workstreams or replace existing completion/approval policy.

Exit: tests prove pre-check prevents action invocation; post-check prevents invalid publication; linked-spec-only changes invalidate results; concurrent/crashed multi-file changes never expose mixed state; observer/startup/freshness checks cannot reuse stale validation. Rebenchmark complete pre/post actions.

Guarded entry points for the adopted pilot:

| Entry point | Required integration |
| --- | --- |
| Proposed `./ask model edit` | Spec-file change batches, atomic node-plus-required-edge creation, graph/lifecycle changes and decision actions all share one pre/action/post/publication path. |
| Proposed `./ask model admit` | Admit coordinator implementation/review actions from a validated snapshot; verify resulting state before publishing their document changes. This does not authorize otherwise forbidden actions. |
| `./ask inner-loop run/resume` and integration | Check document admission around the adopted workstream's action execution and candidate publication; preserve existing single-writer/task/evidence rules. |
| `./ask verify`, result-pass recording, acceptance check | Invoke the same document guard alongside existing checks, with no caller flag or direct command bypass. |
| Proposed `./ask model watch/validate/show/ui` | Public observer and startup/read admission detect external changes and stale identities; readers use validated generations, not domain rules embedded in UI code. |

Include a successful public guard journey asserting exact once-only pre/action/post/publication order and captured input/result identities. Also exercise every state-changing entry point directly against invalid/stale state. Read-only navigation is admission to validated data, not an extra semantic mutation. Raw filesystem writes remain untrusted working changes until admitted.

### 4. Add semantic work and evidence projections

Add attributable decision resolution/reopening, semantic revisions, dependency invalidation/history, and derived task blockers/attention through the guard. Add controlled node/edge creation without raw consumer-side JSON editing.

Create nodes and mandatory edges in one batch. Keep IDs/types stable; explicitly define allowed lifecycle transitions. Options edit only on an open decision, with prior choice/options retained in resolution history. Test rejected/retired assumptions and retired decisions as blocking prerequisites. Test upstream decision changes and newly added/removed dependencies reopening dependent resolutions transitively; no retired object silently unblocks work. Declared task lifecycle remains distinct from proved completion.

Project identical IDs, references and snapshot identity into machine JSON and deterministic Markdown. Inspect canonical scenario Given/When/Then, mapped assertions/cases, implementation references and actual evidence provenance. Reuse existing traceability evaluation read-only. Missing local authority, missing/altered evidence and historical candidates remain explicit; no link or cached pass field grants current completion.

Share the complete nonmutating evaluation path from the existing completion module, including static receipt/CheckPlan identity, runner identity and all log digests. Normal completion commands retain their current-candidate/source-cleanliness rules and report writing. Historical inspection binds checks to that candidate's revision. Tests tamper behavior and static logs/receipts and remove accepted authority; assert artifacts/refs stay unchanged during inspection. Do not call a report-writing operation from the projection or duplicate a partial evaluator.

Create a bounded pilot using completed harness-review evidence plus a visibly labeled future-work decision, never an invented historical blocker.

Exit: CLI validate/inspect/resolve/reload journey works; mutation and evidence tamper tests pass; inspection writes no evidence or refs. Commit this working broader-model foundation before any UI implementation.

### 5. Build the interactive UI over validated state

Use a small native Streamlit workbench: work navigation, scenario/assertion/test/revision inspection, attention with reasons, and decision alternatives with actor/rationale. Both agents and UI consume the same published snapshot.

Decision submission calls the shared guard and retains the state identity originally displayed, including referenced specs. Incomplete input or concurrent edits produce action feedback; the UI does not implement domain validation or repair. A valid choice persists, shows its task consequence and survives a new session.

Exit: Streamlit integration plus a real two-session browser journey prove inspection, persisted decision→task consequence→reload, and stale-form rejection. Broken-document tests remain at document admission, not in UI business logic. No persistent preview server without asking.

Include a valid referenced-spec amendment (with required linked-definition metadata updates) while model bytes and the selected open decision remain unchanged. Rerun must retain the originally displayed identity; submission rejects without writes, and explicit refresh then permits the valid choice. This distinguishes real input freshness protection from rejecting an already-resolved decision. Inspection covers both missing and historical evidence.

### 6. Independently review, verify and hand off

Review the final candidate against criteria EM-001–007, ownership/authority, pre/post admission, published-snapshot integrity, assertion adequacy, provenance and CE-01–06. Address concrete findings without weakening the contract. Capture final native/tool benchmark results without claiming unmeasured usability benefits.

Run full `./ask verify`, candidate-bound semantic coverage review, `./ask check-workstream ... --acceptance` and exact-SHA `record-result --result pass` after implementation. Prepare human Accept with remaining risks and run instructions. Implementation tests/benchmark evidence do not exist at this plan-only handoff.

Exit: independently approved implementation and actual full verification, eligible for human Accept. No automatic merge/push or feature acceptance from this plan.

## Affected modules and seams

- Canonical definitions: `specs/current/` and the adopted `work/<id>/engineering-model.json`.
- Shared document-state validator/action/snapshot interface: kit-owned implementation location chosen after tool selection; likely thin dispatcher under `_ask/scripts/`, with native sources only if selected.
- Read-only evidence adapter: reuse `.agents/ask/verification/traceability/`; preserve its completion policy and coordinator authority.
- CLI dispatch/completion and documented workflow change hooks; standalone validation/change-observation entry points.
- UI: `_ask/ui/streamlit_app.py` and narrowly scoped dependencies, only after milestones 2–4.
- Tests: `_ask/tests/`, isolated fixture helpers and benchmark artifacts. Python unittest drivers are runner-compatible orchestration, not a requirement that validator internals be Python.

## Verification contract

`test-plan.json` maps every criterion/type to named future cases. Core invariant/semantic cases cover isolated logic; integration covers actual files, guard ordering, concurrency, authority and provenance; public CLI/browser journeys cover complete outcomes. Guard cases specifically include invalid pre-state, invalid candidate, referenced-spec-only changes, external saves/missed events, bootstrap admission, cache/full parity and publication races.

Unit/type assignments must describe the selected implementation's real test seam. If a subprocess wrapper is only integration coverage, do not relabel it a unit test to satisfy metadata; amend bindings or add genuine native-core unit coverage before pinning that implementation contract.

Every new behavior needs actual assertion red at an immutable revision and final green; import/setup failures and placeholder-file existence assertions do not prove red. Record actual native/tool executions through supported named test drivers; unmapped opaque native-suite summaries cannot replace per-case evidence.

E2E applies: isolated guard/CLI journeys and temporary local Streamlit/browser interaction. Use only test-owned repositories/directories/processes; no committed pilot or production data mutation. Bootstrap capability/dependency failures must be clear, not silently skipped. Pin versions and verify the browser/client pairing during implementation; local Playwright 1.13.0 is observed, not asserted compatible with every browser API.

## Models and effort

| Job | Assignment |
| --- | --- |
| Complex domain/guard planning, implementation and review | Sol / high |
| Adversarial contract challenge | Astra / high |
| Clear bounded adapters, UI wiring or test scaffolding when delegated | Luna / medium |
| Deterministic check execution | Luna / low |

The parent coordinates one branch and one committing writer. Independent challenge/review remain separate contexts, same GPT family; no cross-family diversity claim. Workstream overrides in `models.yaml` promote complex stages; actual bounded delegation may use the cheaper assignment.

## Escalation and non-goals

Escalate if the pilot requires a different authority, changes canonical domain invariants, replaces completion/approval policy, needs distributed/authenticated writes, changes the public contract, or cannot meet an agreed performance budget without a scope change. No latency budget has been agreed; do not invent a promised threshold or use speed to excuse skipped validation.

Not included: complete IDE/control room, database, multi-host infrastructure, production deployment, broad test-runner migration, all-workstream adoption, automatic document repair, autonomous execution from UI, badges/points, measured productivity claims, or merges/pushes to main/develop.

## Current handoff

Deliver this reviewed plan and stop. A planning structural check or static repository test pass must not be presented as a working validator, tested guard, UI completion, benchmark result or human feature acceptance.
