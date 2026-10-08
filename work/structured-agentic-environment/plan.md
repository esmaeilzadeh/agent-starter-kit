# Plan: validated Engineering Model, then interactive workbench

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

### 4. Add semantic work and evidence projections

Add attributable decision resolution/reopening, semantic revisions, dependency invalidation/history, and derived task blockers/attention through the guard. Add controlled node/edge creation without raw consumer-side JSON editing.

Project identical IDs, references and snapshot identity into machine JSON and deterministic Markdown. Inspect canonical scenario Given/When/Then, mapped assertions/cases, implementation references and actual evidence provenance. Reuse existing traceability evaluation read-only. Missing local authority, missing/altered evidence and historical candidates remain explicit; no link or cached pass field grants current completion.

Create a bounded pilot using completed harness-review evidence plus a visibly labeled future-work decision, never an invented historical blocker.

Exit: CLI validate/inspect/resolve/reload journey works; mutation and evidence tamper tests pass; inspection writes no evidence or refs. Commit this working broader-model foundation before any UI implementation.

### 5. Build the interactive UI over validated state

Use a small native Streamlit workbench: work navigation, scenario/assertion/test/revision inspection, attention with reasons, and decision alternatives with actor/rationale. Both agents and UI consume the same published snapshot.

Decision submission calls the shared guard and retains the state identity originally displayed, including referenced specs. Incomplete input or concurrent edits produce action feedback; the UI does not implement domain validation or repair. A valid choice persists, shows its task consequence and survives a new session.

Exit: Streamlit integration plus a real two-session browser journey prove inspection, persisted decision→task consequence→reload, and stale-form rejection. Broken-document tests remain at document admission, not in UI business logic. No persistent preview server without asking.

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
