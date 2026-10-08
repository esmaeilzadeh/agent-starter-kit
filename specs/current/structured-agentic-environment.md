# Specification: Engineering Model and local workbench

Status: CURRENT. Human-selected sequence: broader model first, interactive UI second. Canonical observable criteria: adjacent JSON contract. Source intent: `work/structured-agentic-environment/intent.md`; source thesis: its `source-handoff.md`.

## Authority and scope

A revisioned `work/<id>/engineering-model.json` owns broader engineering definitions and references. Existing canonical criterion JSON, accepted test plans, code, coordinator review/execution evidence and inner-loop runtime remain their own authorities. The model stores references, not competing Given/When/Then or test outcomes. Markdown, machine context and UI are projections. There is no editable “verified” field or UI shortcut to existing acceptance/integration gates.

The first pilot is this workstream, using harness-review as an actual read-only traceability example plus an explicitly labeled pilot future-work decision. Model creation/validation and controlled editing must work before UI implementation starts. One local cooperating developer; Git remains the change review/history mechanism. No authenticated authorization or multi-host concurrency guarantee is claimed.

## Definition contract

Schema `ask-engineering-model/v1`: work_id, positive integer revision, nodes and edges. Stable node IDs are unique nonempty slugs within the model. Node types: intent, requirement, feature, story, scenario, decision, assumption, task, implementation, test, test_run, risk, evidence. Every node has a nonempty title and a type-specific definition lifecycle. Generic nodes use draft/active/retired; decisions open/resolved/retired; assumptions unverified/confirmed/rejected/retired; tasks planned/active/done/retired; risks open/mitigated/retired. Definition lifecycle never asserts execution outcome.

`contains` expresses intent→feature/requirement/task/decision/assumption/risk, feature→story/requirement/scenario/task/decision, story→scenario/task/decision, requirement→scenario. Exactly one intent is required. Every non-draft feature/requirement/story/scenario/task has exactly one legal parent. Each test covers at least one scenario via test→scenario `covers`. Implementation→scenario/task `implements`; test_run→test `executes`; evidence→test/test_run `supports`. `depends_on` is legal from task to task/decision/assumption and decision to decision/feature/requirement/scenario/assumption. Reject broken references, illegal types/edges, duplicates, containment/dependency cycles, contradictory lifecycle/resolution and unexpected fields. Standalone validation reports precise stable codes and IDs, including malformed JSON/schema/field types; it never mutates.

Active requirement/scenario references select an existing canonical criterion; tests select an existing test-plan case. Implementation references are safe repository-relative source paths, optionally symbols. Evidence/run references are safe repository-relative JSON paths; unavailable runtime evidence is visible missing evidence, not a malformed engineering definition. Resolve paths inside the repository, including symlink checks. Reference-only test/evidence nodes carry no mutable outcome. Draft requirement/scenario nodes may await a canonical reference.

Decisions have at least two unique option IDs/labels. A resolution records option_id, nonempty actor/rationale, UTC timestamp. Resolved state requires a valid resolution; open state has none. History preserves prior resolutions/reopening/invalidation. Actor attribution is cooperative local input, not authentication.

## Semantic editing interface

One shared module provides load/validate, snapshot/project and mutate. Commands add_node, add_edge, resolve_decision, reopen_decision and revise_node cover this slice. Revisions of semantic title/description/reference retain stable IDs; editing a node reopens resolved decisions that transitively depend on it and records why. Dependencies propagate task blockers; resolution/reopening changes derived attention/task readiness, not existing execution or acceptance evidence. Planned/active tasks with unresolved decision/assumption or unfinished task prerequisites are blocked; the graph is acyclic.

Every mutation requires the expected canonical model digest. Under an exclusive local lock, reload current bytes, compare digest, apply command to a copy, validate the whole candidate, then atomically replace and increment revision exactly once. Invalid command, invalid candidate, missing actor/rationale or stale digest leaves definition bytes unchanged. CLI and UI call this module, never edit the JSON directly. Changes remain visible uncommitted Git changes; the app neither commits nor spawns work.

## Projections and evidence

Machine JSON and deterministic Markdown expose identical object IDs, hierarchy, references, unresolved decisions, dependency reasons and derived task readiness. Projections preserve source/model digests and evidence revision identity. Scenario inspection reads canonical Given/When/Then and planned assertions/cases, source references, required test types, actual retained outcomes and provenance. A declared link is explicitly not proof of behavior.

The read-only evidence adapter reuses the existing traceability completion evaluator and coordinator binding checks rather than trusting a cached pass field. Missing local accepted ref, missing or malformed reports, changed logs/bindings and stale contracts are visible unavailable/invalid evidence. Historical candidate evidence is explicitly historical relative to the inspected checkout; it cannot establish current completion. Inspection must not write completion files, advance refs, run tests or call acceptance. No new completion policy is introduced.

## Interactive UI

Use a small native Streamlit workbench, dependency optional for core CLI/model use. Work selector, engineering object/scenario inspector, source/assertion/test/revision detail and attention/blocked-task reasons are primary. A decision form offers the model's alternatives, actor and rationale, then submits through the shared digest-bound mutation interface. Success survives reload/new session. Missing fields, invalid model and stale session are actionable errors. Pin the digest displayed when a form was loaded; a rerun must not silently accept a concurrently changed definition. Provide refresh/reload to inspect a conflict.

The UI is a local technical direction surface, not points/badges or a generated document approval queue. Unresolved decisions and evidence failures cause attention items; resolving one shows its actual task consequences. No custom CSS, arbitrary source editing, production deployment or automatic execution.

## Observable acceptance

- EM-001: Standalone validation accepts representative broad typed models and rejects malformed fields, duplicate/broken identities/references, illegal relationships/cardinality, cycles and lifecycle conflicts with precise diagnostics.
- EM-002: Shared semantic mutation persists attributable decisions, propagates blockers/invalidation and history, increments revisions; stale/invalid edits and concurrent stale writers preserve data.
- EM-003: Read-only scenario/evidence inspection reuses current authorities, shows actual assertions/outcomes/provenance, differentiates historical/missing/invalid evidence, and cannot turn a link or tampered pass field into current completion.
- EM-004: Public CLI validation, JSON/Markdown projections and decision-edit journey share the same model and digest; CLI errors are useful and nonmutating.
- EM-005: UI navigates work/scenario to canonical assertion/test/evidence detail and exposes honest missing/historical states; malformed input yields useful errors without a traceback-only page.
- EM-006: UI attention/decision journey persists a reasoned choice and derived task change across reload; stale forms reject concurrent changes and invalid submissions do not write.

## E2E

Applies. CLI journey in disposable fixtures, UI integration via Streamlit AppTest, real temporary browser E2E for work/scenario inspection and persisted decision→unblock→reload plus stale-form protection. Browser/server and data are test-owned, local, reset by teardown; never mutate the committed pilot from tests. Required test types and exact cases are in the independently challenged test plan. Full repository Verify and candidate-bound independent semantic review remain mandatory. These checks establish behavior, not comparative usability/productivity.
