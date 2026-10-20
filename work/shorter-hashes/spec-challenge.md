# Specification Challenge

## Model

- Model: `gpt-6.1-sol`; reasoning effort: `medium`, the previously submitted selection recorded in `models.yaml`. The runtime exposes no independent model-identity attestation.
- Runtime: Codex, independent Spec Challenge subagent.
- Parent model: not exposed; not inferred.
- Reviewer: `/root/shorter_hashes_challenge_r6`.
- Method: generated `kit-03-spec-challenge`, with `writing-for-agents` in embedded mode. This is a specification assessment, not implementation verification or plan approval.

## Specification

- Workstream: `shorter-hashes`.
- Exact reviewed commit: `9be2865e9c1b703a33d767ea3d86e9682c3602f3`.
- Canonical contract: `specs/current/shorter-hashes.json`, `ask-spec/v1`, revision **6**, all **18** criteria (`SH-01`–`SH-18`).
- Canonical JSON SHA256: `9945ef64c045d3fa06f882c7f1c915b4b94bca4a2408f4b139d413f62d2d89f3`.
- Proposal: `specs/proposals/shorter-hashes.md`.
- Proposal exact-byte SHA256: `4cd8f23b8a9edc21f0c0128885b6ba816c0fbe8eea389473b2777dc314c88dcd`.

Independently computed both digests from `git show <reviewed-commit>:<path>`. JSON uses Python `json.dumps(value, sort_keys=True, separators=(',', ':')).encode()`, matching `.agents/ask/verification/traceability/contracts.py`; Markdown uses the exact committed bytes.

Reviewed both contract documents, `intent.md`, `spec-change.md`, `engineering-model.json`, the saved model selection, `_ask/docs/spec-test-traceability.md`, the delegation/workflow policies, and existing acceptance/completion behavior in `traceability/evidence.py` and `traceability/completion.py`. The revision-5 challenge is retained at `9be2865e9c1b703a33d767ea3d86e9682c3602f3:work/shorter-hashes/spec-challenge.md`; its decision applies only to its own recorded revision-5 digests. This file records a new independent decision for revision 6.

The intent and engineering subject agree with the amended contract: numeric identities across spec/part, plan/item, task, and test families; immutable numeric revisions; separate integrity data; exact dependencies; selective reassessment; and project-wide impact with owner-scoped authority. Stable `SH-*` criterion labels are retained historical identifiers under the explicit transition rule, not evidence that new numeric runtime identities already exist. Proposal files and model/schema scaffolds supply no implementation or execution evidence.

## Ambiguities

No unresolved What/Why ambiguity blocks revision 6. The following design choices are explicitly assigned to Plan and must be made concrete before implementation:

1. **Parent context and revision allocation.** Specify each type's logical parent, inherited-context boundaries, revision encoding/allocation, and move mapping. A task consuming parts from two specs still has one ownership identity and two exact dependency edges. Updating an ancestor's revision alone must not rename it. The illustrative reference grammar and bare-number JSON example do not override the requirement for sufficient explicit or inherited version context.
2. **Item comparison and snapshot binding.** Define deterministic extraction and meaningful-content/binding comparison for every supported format, including global constraints. The same unchanged item revision may remain bound to its original exact snapshot after an unrelated edit; it need not be rebound to the newest commit. Candidate comparison uses an explicit snapshot. Changed meaningful content or dependencies require a fresh item revision.
3. **Discovery completeness.** Define authoritative owner/source enumeration, immutable snapshot selection, archived-source handling, and index freshness. A consumer present only on another workstream branch must be discovered. Unknown or unavailable declarations cannot establish an empty dependency set or complete impact clearance.
4. **Propagation stopping and evidence reuse.** Define the consumer-relevant contract used by reviewed retain decisions and their authority. A plan item's new upstream binding requires a new revision even when its payload is retained. Clearing descendants requires a reviewed equivalence/reuse decision; it cannot simply leave them silently bound to a substituted target. Multiple affected input paths must each resolve.
5. **Separate integrity publication.** Specify the separate file's versioned format, lifecycle, trust anchors, retention, and atomic publication protocol. Mutable indexes may advance; published item/revision entries may not change. A containing file can gain new immutable entries without making old entries mutable. Contract entries and later run records retain separate lifetimes.

These choices have observable constraints in SH-02/03/05/07/08/13/15/16/18. Choosing schemas, file paths, parent grammar, command flags, or extraction algorithms within those constraints does not require a new user decision. Inability to satisfy the behavior requires Spec Change rather than weakening acceptance.

## Missing failure cases

No uncovered failure class requires a specification correction. The independent test-plan review must turn these concrete counterexamples into explicit cases and assertions:

| Counterexample | Required observable result |
| --- | --- |
| Spec 1/part 2, plan 1/item 2, and another workstream's item 2 share local numbers; a projection drops type, owner, parent, or revision context. | Resolve only sufficient declared context; otherwise return a scoped error. Numeric ordering places 2 before 10; zero, padded, and malformed new IDs are rejected (SH-01/02/08/11). |
| Task T consumes requirements under two specs; a generator copies it under each upstream parent or renames it when one ancestor revision advances. | One stable owned identity, explicit multiple-input edges, and no ancestor-only identity/revision churn (SH-02/15/16). |
| A published revision's integrity entry is deleted, its snapshot is changed, or an old revision is aliased to the latest entry. | Fail exact resolution; never substitute another version or current checkout. Required old entries and Git objects remain retrievable (SH-03/05/07/10). |
| Two coordinators read the same allocation state and publish the same scoped ID/revision with different content. A crash occurs after entry preparation but before reference publication. | Serialize or reject conflicting stale writes; readers see complete old/new state. Retry cannot mutate a published target or report a successful dangling reference (SH-08/13). |
| A candidate changes the integrity file, accepted-pin copy, or review attribution to make an altered contract appear accepted. | Coordinator-owned accepted-tests authority and registered decisions remain decisive; candidate files cannot grant authority (SH-04/14). |
| A new run adds logs and rewrites the old contract entry; an old object becomes unreachable after authority advances. | Separate immutable contract/run lifetimes; retain required historical entries/objects, or explicitly refuse unavailable historical validation/export (SH-03/05/10). |
| JSON keys/whitespace change, while a byte-bound intent or log receives an equally harmless-looking whitespace edit. | Preserve canonical-JSON equivalence only where declared; byte-bound approval/log evidence invalidates. Algorithms and semantics cannot be swapped (SH-06/09). |
| S1 and S2 share a file; only S1 changes. A global policy consumed by both also changes in a second fixture. | First fixture leaves S2's item revision and independent chain eligible. Second reaches all actual policy consumers; identical local payload alone does not establish independence (SH-07/15/16/18). |
| P's payload is unchanged after rebinding S1 revision 1 to revision 2; a pointer-only retain decision clears T, which also depends on changed Q. | P gets a fresh revision for the binding change; attributable review and reuse rules govern propagation stopping. Q's unresolved path still blocks T's new-context completion (SH-15/16). |
| A test remains eligible but its historical final-green run belongs to another candidate/contract; an implementer labels that run current after a retain decision. | Keep historical run bindings intact. Existing exact-candidate/contract/runner/source/log requirements still apply; execute again when reuse rules require it (SH-04/14/15/16). |
| A source document is unavailable versus a requirement absent from an available candidate document; the requirement's test also serves another active obligation. | Availability failure is not deletion. Actual deletion triggers reviewed assessment; preserve shared active dependents and history, distinguish stale from retired, and propagate resulting changes (SH-07/17). |
| B consumes A's shared policy only on B's branch; C is unavailable; an index contains an old B snapshot. | Discover committed sources outside the checkout, report B and paths with their owners, mark unresolved C/index scope incomplete, and transfer no write or acceptance authority (SH-18). |
| A legacy record lacks explicit item versions or a transferred export lacks coordinator authority/Git objects. | Preserve readable originals; require exact provenance for explicit mapping. Missing declarations are not proof of independence. Do not manufacture approval, numeric history, Red/Green, or verified-complete imports (SH-10/18). |
| Compact JSON conflates absent/null/empty, loses Unicode, or a projection omits the context needed for its next lookup. | Preserve values and schema-declared distinctions; deterministic normalization and sufficient context or a scoped failure (SH-09/11). |
| Numeric references reduce the displayed report, but new revision entries, cross-owner indexes, and repeated lookup responses exceed baseline cost. | Count all generated metadata JSON and all necessary agent inputs/lookup responses. Fail savings acceptance unless both aggregate token and byte totals decrease (SH-11/12). |
| Raw Git inspection encounters a newly colliding abbreviation after numeric publication. | Expand colliding displays, reject ambiguous input without rebinding, and supply full IDs for exact operations (SH-01/08). |

Cycle tests must distinguish actual dependency cycles from ordinary resolution/ownership links and retained historical records. Lookup or ownership alone is explicitly not a dependency. Missing targets, conflicting identities, unsafe paths, and cross-owner cycles require stable scoped failures rather than fallback.

## Over-constraint risks

The amendment adds allocation, revision history, integrity storage, migration, and cross-workstream discovery to an already broad dependency/evidence change. This scope follows the explicit user refinement and preserved revisions 4/5; treating the work as a formatter-only change would miss its approved destination.

Numeric revisions and a separate integrity file may increase storage and lookup cost. SH-12 deliberately requires lower aggregate metadata bytes as well as agent-input tokens, including all new metadata. This is a feasibility risk to test against the frozen corpus, not grounds to remove integrity or evidence requirements. Individual journey regressions are permitted only with disclosure; aggregate savings in both measures remain mandatory.

The contract fixes numeric identities/revisions and separate integrity storage but leaves concrete syntax, file layout, and comparison algorithms to Plan. It does not require a new global authority service, cryptographic identity authentication, or bulk historical rewriting. Existing coordinator attribution is cooperative repository authority, as the traceability contract states.

## Under-constraint risks

All 18 criteria declare `verification_mode: tests`. None claims a review-only exemption. Their Given/When/Then outcomes are observable, and the Markdown specifies these minimum evidence types:

| Criterion | Required types | Independent assessment of observability |
| --- | --- | --- |
| SH-01 | unit, integration | Assert default persisted/rendered numeric references, explicit context, collision rejection, and full-ID exact operations. |
| SH-02 | unit, integration | Exercise every named artifact/item family, numeric sorting, immutable revisions, moves, ancestor stability, and multi-input ownership. |
| SH-03 | unit, integration | Resolve separate integrity entries, shared sources, byte/JSON semantics, external artifacts, and missing/mutated mappings. |
| SH-04 | integration, e2e | Attempt candidate substitution through real coordinator and completion entry points, including independent-decision forgery. |
| SH-05 | integration | Add later runs and contracts, then reload old entries and evidence; assert lifetime and retention boundaries. |
| SH-06 | unit, integration | Assert canonical equivalence separately from exact-byte invalidation and reject semantic/algorithm substitution. |
| SH-07 | integration | Use real Git blobs/snapshots for unchanged and unrelated edits, meaningful changes, moves, unavailable sources, and actual deletion. |
| SH-08 | unit, integration | Exercise malformed/scoped references and real stale concurrent registrations, not only sequential allocator calls. |
| SH-09 | unit, integration | Compare normalized values and distinguish declared absent/null/empty/default behavior through round trips. |
| SH-10 | integration, e2e | Read real legacy fixtures and migrate/export/reload through workflow entry points without invented authority/history. |
| SH-11 | integration, e2e | Request selective projections, follow needed lookups, and demonstrate that default inputs omit the whole catalog without losing evidence access. |
| SH-12 | integration | Execute frozen equivalent journeys with the pinned tokenizer; include all metadata, context, lookups, and per-journey/aggregate totals. |
| SH-13 | integration | Inject interruption at publication boundaries; observe readers, retries, conflicting state, and fixture cleanup. |
| SH-14 | e2e | Execute valid and deliberately invalid workflows with real case results, review registration, and exact completion lineage. |
| SH-15 | unit, integration, e2e | Pin every actual dependency family, compare content/bindings, publish changed revisions, and preserve historical execution bindings. |
| SH-16 | unit, integration, e2e | Observe direct versus potential impact, independence, multiple unresolved inputs, reviewed stop decisions, and completion refusal/eligibility. |
| SH-17 | unit, integration, e2e | Exercise exclusive/shared deletion, reviewed retirement, historical retrieval, active views, and downstream binding changes. |
| SH-18 | unit, integration, e2e | Discover cross-branch owner sources, traverse actual edges, report unresolved scope, and preserve owner authority through workflow outcomes. |

The types are adequate minimum obligations. Plan still needs explicit case IDs, assertions, accepted TaskGraph scopes, source paths, supported instrumented runner selectors, and independent review bound to exact contract digests. A happy-path resolver test, JSON `pass` field, opaque command exit, or review prose cannot substitute for these obligations or actual case execution.

Existing `evidence.py` anchors accepted obligations to `refs/ask/accepted-tests/<work-id>` and validates current contract digests. `completion.py` checks coordinator-recorded review, exact candidate final green, spec/plan digests, source bindings, runner identity, logs, static checks, and Red/Green eligibility. Revision 6 expressly preserves those authorities. Selective item eligibility must coexist with them: an unaffected item does not establish that an entire changed workstream has completed, and a retain decision cannot relabel historical execution. The Plan must show this distinction in executable cases.

Legacy compatibility includes unsupported-schema refusal and explicit migration requirements. A reader can preserve historical access without qualifying that history for new completion. Source-only exports must retain or re-register coordinator authority under the existing reviewed process; copied candidate metadata alone cannot authorize it.

## Recommended clarifications

No scope-preserving correction to the revision-6 specification is required. Carry these existing obligations into concrete Plan deliverables:

1. Inventory every eligible hash surface and actual dependency family; identify versioned writer/reader formats, full-value exceptions, authoritative owner, and legacy behavior.
2. Specify numeric ownership grammar, explicit inheritance, immutable revision allocation, stable move mappings, separate integrity-file lifetimes, retention, concurrency, and crash recovery. Demonstrate sufficient context for every ordinary reference.
3. Define format-specific item extraction and equality including global constraints and bindings. Preserve unrelated revisions while publishing meaningful changes; never retarget an old revision to a new source.
4. Specify consistent cross-workstream source discovery and incomplete-analysis behavior, including archived/branch-only consumers, stale indexes, unavailable owners, and cycles.
5. Define attributable retain/revise/retire transitions and reviewed propagation stops without weakening exact accepted-contract or final-execution checks. Distinguish retained item eligibility, reusable history, and newly executed evidence.
6. Freeze the baseline source/corpus, tokenizer/package version, equivalent journey scripts, and accounting boundaries before production changes. Include numeric revision metadata, integrity files, graph/index metadata, and necessary lookup responses in the totals.
7. Prepare and independently review the test plan and exact TaskGraph obligations under coordinator authority before implementation. No schema scaffold or this challenge supplies that decision.

## Challenge verdict

**PASS** for the exact revision-6 canonical JSON and Markdown digests recorded above.

No specification blocker or intent/spec conflict was found. The approved numeric hierarchy/revision correction is represented across all named families while preserving exact dependencies, immutable history, full integrity, coordinator authority, selective reassessment, cross-workstream visibility, migration, and the primary savings goal. Concrete counterexamples have specified outcomes; proving them remains future work.

Complete-intent confirmation is still absent and the implementation plan/test obligations are not accepted. Those are separate workflow gates, not evidence that this specification has failed or that implementation is authorized. This decision grants no human approval, plan acceptance, execution evidence, workstream completion, or final acceptance. The authorized task ends with this independent challenge; no later stage is advanced here.
