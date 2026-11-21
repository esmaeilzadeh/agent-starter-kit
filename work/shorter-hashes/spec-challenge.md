# Specification Challenge

## Model

- Model: `gpt-6.1-sol`; reasoning effort: `medium`, the previously submitted selection in `models.yaml`. Runtime model identity is not independently attested.
- Runtime: Codex, independent Spec Challenge subagent.
- Parent model: not exposed; not inferred.
- Reviewer: `/root/shorter_hashes_challenge_r6`, continuing the independent review through revision 7.
- Method: generated `kit-03-spec-challenge`, with `writing-for-agents` in embedded mode.

## Specification

- Workstream: `shorter-hashes`.
- Exact reviewed commit: `90d1c4300fb18cb54d05bca32491f84a76645d17`.
- Canonical contract: `specs/current/shorter-hashes.json`, `ask-spec/v1`, revision **7**, all **18** executable criteria (`SH-01`–`SH-18`).
- Canonical JSON SHA256: `9bd9107a4d9490528178e2ac204c44926aa9b0e8675fd58f042e2a6fa2a77a3e`.
- Proposal: `specs/proposals/shorter-hashes.md`.
- Proposal exact-byte SHA256: `a9f8f6616ce215be0a6e2d6d84ddba8c907abb2caf0b46ada4f04bf4c9e02583`.

Independently computed both digests from the exact committed objects. JSON uses `json.dumps(value, sort_keys=True, separators=(',', ':')).encode()`, matching `traceability/contracts.py`; Markdown uses exact committed bytes. Reviewed every JSON criterion and its required evidence types, the complete proposal, updated intent, revision-7 amendment, earlier challenge and reopened findings, and the existing traceability authority/completion contract and relevant code. The intent and specification agree on the destination and the planning-only endpoint.

**The unconditional revision-6 PASS is superseded.** It incorrectly treated three behavioral gaps as implementation choices. Its original record remains at `9a3d25d:work/shorter-hashes/spec-challenge.md`. This decision reassesses the corrected revision-7 contract; it does not retroactively approve revision 6.

## Ambiguities

### Reopened behavioral findings

| Finding | Revision-7 normative closure | Independent counterexample assessment |
| --- | --- | --- |
| G1: meaningful equality | **Closed.** “Normative item comparison,” “Item dependencies and Git history,” SH-07 and SH-15 include all payload fields and actual exact input identities/revisions/roles by default. Only exhaustive, pre-reviewed versioned presentation exclusions are allowed. Unknown fields are significant; unavailable extraction/profile/binding/constraint context cannot establish equivalence. | An unchanged file blob with an externally changed binding must produce a fresh revision and reassessment. A timeout changing from 10 to 20 cannot be excluded as presentation or ignored because local prose is unchanged. JSON key order/serialization whitespace may compare equal, but types, arrays, values, Unicode and absent/null/empty distinctions remain significant. Blob equality is explicitly only a payload fast path. |
| G2: propagation-stop boundary | **Closed.** “Normative propagation-stop decision,” required decision examples, SH-15 and SH-16 define complete consumer-facing obligations, exact named revisions/paths/profiles/evidence/authority, new-context validity, and immutable old pins. | P2's internal input pin changes, so P2 is a fresh revision. That does not itself prove changed outward obligations or equivalence. T1 may keep P1 only under explicit reviewed validity in the captured new context with every input resolved and existing authority/reuse rules satisfied. Updating T's pin requires T2. Neither path relabels a historical execution. Changed inherited/outward obligations or unproven equivalence continue reassessment. A narrower interface must already have an explicit reviewed declaration; the reviewer cannot invent it after the change. |
| G3: complete project discovery | **Closed.** “Project-wide graph and workstream ownership” and SH-18 define the authoritative local live coordinator-ref, selected integration/archive, and registered shared-owner universe, exact immutable vector and capture generation. | A new/removed/advanced owner ref during capture must serialize, trigger retry, or make the result incomplete. A mixed vector cannot claim completeness. Missing declarations in a known owner cannot mean dependency-free. Results disclose the captured scope; new-context clearance rechecks the applicable vector/generation. Unfetched remote scope is expressly unclaimed unless fetched/registered. Historical results remain scoped to their recorded vector. |

Internal binding versus outgoing contract is now explicit: changing a binding always creates a new version of its owner, while propagation depends on the fully reviewed consumer-facing contract, including inherited obligations. Retaining an old consumer pin is a recorded validity decision, not a substitution of its target. Existing completion requirements remain separately decisive.

### Exhaustive audit of earlier deferrals

Classification: **Covered** means behavior is already fixed by the cited rule. **Bounded** means an implementation choice remains, with the invariant stated below. **Open** would prevent sealing; none remains.

| Earlier deferral | Classification, authority and invariant |
| --- | --- |
| Parent context, reference grammar and explicit inheritance | Covered by “Numeric identities and revisions,” SH-01/02/08: one qualified owner/type/parent/item/revision; multiple inputs are separate edges; ancestor revisions alone cause no churn. Exact spelling and type-parent layout are bounded: they must preserve that unique ownership and reject insufficient context, not duplicate the item under its inputs. |
| Numeric allocation and revision encoding | Covered by SH-02/08: positive unpadded IDs, numeric ordering, immutable published targets, increasing revisions within one identity and serialized conflicting publication. Allocator code/encoding is bounded by those outcomes; revision reuse is forbidden. |
| Stable moves and historical path mappings | Covered by SH-02/07: explicit mappings and exact original source identities; no guessing or retargeting. Mapping representation is bounded because all old references must retain their targets. |
| Item extraction and meaningful equality | Covered by the G1 closure and SH-07/15. Extractor/profile encodings are bounded: exhaustive reviewed presentation exceptions cannot change values, obligations, actual bindings, unknown-field significance or incomplete-comparison refusal. Profile changes require reviewed migration/reassessment, not retrospective equivalence. |
| Shared/global constraints and dependency-family inventory | Covered by SH-07/15/16 and “Coverage and compatibility”: every actual input participates, including external declarations, source, policy and runner inputs. Ownership/lookup alone is not an edge. Inventory layout is bounded; omitting an actual family violates the contract. |
| Explicit candidate snapshot and unchanged-item source binding | Covered by SH-03/07/15: comparison uses selected immutable snapshots, no HEAD fallback; an unchanged item retains its original revision/source. Snapshot-selection interface is bounded; it cannot silently relocate historical entries. |
| Authoritative owner inventory, archive handling and source capture | Covered by G3, SH-18 and “Project-wide graph and workstream ownership.” Inventory format, generation tracking and capture technology are bounded: the full stated local universe, exact vector, new/ref removal detection and coherent observation cannot change. |
| Index rebuilding and freshness | Covered by SH-18: index matches captured inventory/vector, remains rebuildable, grants no authority, and stale/unavailable context prevents complete clearance. Index layout/lookup algorithm is bounded by those outcomes. |
| Retain/revise/retire, equivalence and propagation stopping | Covered by G2, SH-15/16/17 and both normative comparison/stop sections. Decision field names are bounded: exact versions, all paths, profiles, evidence, owner authority and reviewed new-context validity must remain representable and enforced. |
| Selective eligibility versus accepted-contract/final-candidate completion | Covered by SH-04/14/15/16, “Normative propagation-stop decision,” and `_ask/docs/spec-test-traceability.md`. An unaffected item does not complete a changed workstream. Old runs cannot become fresh final green. Adapters are bounded by exact candidate/contract/source/runner/log checks and existing evidence eligibility. |
| Integrity file path, format and partitioning | Covered behavior in SH-03/05: separate full integrity data, exact immutable item/revision targets, shared identities, distinct contract/run lifetimes and retained history. File path/serialization/partitioning is bounded; moving data cannot weaken resolution, integrity or authority. |
| Publication, locking, retries and concurrent allocation | Covered by SH-08/13 and “Constraints and invariants”: readers see complete old/new state, no successful dangling references, conflicting stale writes rejected, published targets immutable. Lock/transaction mechanics are bounded by these observable guarantees. |
| Producer/consumer and eligible-hash-surface inventory | Covered by “Coverage and compatibility,” SH-03/10/11/15: all named families and eligible surfaces must be accounted for, with justified full-value exceptions. Module/inventory organization is bounded; it cannot reduce coverage. |
| Authority and attribution per artifact/owner | Covered by SH-04/15/16/18, “Authority and identity,” delegation and traceability contracts. Missing authority prevents clearance. Record syntax is bounded; it cannot replace coordinator registration, independent decisions or another owner's authority with candidate fields. |
| Legacy formats, migration, export and source-only transfers | Covered by SH-10/18 and traceability migration/authority rules: readable originals, exact provenance, supported validation semantics, explicit unsupported/incomplete failure, required immutable objects and reviewed authority registration, no manufactured versions/approval/execution. Adapter/CLI/schema numbers are bounded by those outcomes. |
| Compact serialization, omitted defaults and projections | Covered by SH-09/11: versioned defaults, preserved values/distinctions, sufficient declared context, selective lookup and retrievable detail. Projection shape/field names are bounded; necessary context/evidence cannot be omitted to save tokens. |
| Baseline corpus, tokenizer, scripts and accounting | Covered by SH-12 and “Savings measurement”: preimplementation freeze, representative real artifacts, all three journeys, equivalent questions/evidence, same pinned tokenizer, all necessary inputs/lookups and generated metadata JSON, strict aggregate decrease in both units, disclosed regressions/exceptions. Exact corpus/tooling is bounded by those minimum contents and fixed accounting; bytes cannot substitute for tokens. |
| Test cases, source paths, TaskGraph scopes and runner selectors | Covered obligations: all 18 criteria are executable, required types below, traceability contract requires actual instrumented cases, independent semantic review, accepted pins and applicable Red/Green. Case/fixture layout is bounded; it cannot remove criterion assertions/types, replace executions with exit codes, or create review-only waivers. |
| Configuration keys, command flags and module seams | Bounded by “Interfaces” and the cited behavioral criteria: existing entry points retain purpose/safety; alternate names/layouts cannot change required resolution, authority, failure or completion outcomes. |

## Missing failure cases

The following audits **every earlier failure-case row** and the associated cycles paragraph. Each now has a normative outcome rather than an unqualified promise of later Plan work.

| Earlier concrete counterexample | Classification and required outcome |
| --- | --- |
| 1. Spec/part, plan/item and another owner's item share local numbers; projection omits context; 10 sorts before 2. | Covered, SH-01/02/08/11: sufficient declared qualification or scoped refusal; numeric ordering. Legacy IDs remain under explicit stable mappings; malformed new IDs do not become valid legacy records. |
| 2. Multi-input task copied under two specs or renamed when an ancestor revision changes. | Covered, SH-02/15/16: one ownership identity, explicit independent input edges, no ancestor-only churn. |
| 3. Integrity entry deleted, mutated, or old revision redirected to newest target. | Covered, SH-03/05/07/10: fail exact resolution; no substitution or rebinding; retain required historical entries/objects. |
| 4. Stale concurrent writers publish conflicting scoped revision; crash precedes reference publication. | Covered, SH-08/13: serialization/conflict refusal, complete old/new state, immutable retries, no dangling successful references. |
| 5. Candidate rewrites integrity file, accepted-pin copy or independent attribution. | Covered, SH-04/14 and “Authority and identity”: existing coordinator authority/registered decisions remain decisive. |
| 6. Later log rewrites accepted contract, or old Git object disappears after authority advances. | Covered, SH-03/05/10: independent immutable lifetimes and retained source/history; unavailable history refuses validation/verified-complete export. |
| 7. Equivalent JSON formatting versus whitespace edit to intent/log. | Covered, SH-06/07/09: declared canonical equivalence only for structured comparison, exact-byte invalidation for bound authority/evidence; no algorithm/semantics substitution. |
| 8. S1 and S2 share a file; one changes, or an external global policy changes while blobs do not. | Covered, G1, SH-07/15/16/18 and required examples: unrelated item retains revision; actual external constraint/binding change participates despite blob equality. |
| 9. P payload retained after changing S binding; pointer-only retain clears T while Q also changed. | Covered, G1/G2, SH-15/16 and required examples: fresh P revision, reviewed complete contract equivalence, immutable pins and every affected T path resolved. P's decision cannot clear Q. |
| 10. Old final-green run relabeled current after retain. | Covered, SH-04/14/15/16 and stop section: preserve exact original bindings, execute new final candidate wherever existing completion requires it. |
| 11. Unavailable document treated as deleted item; deleted requirement's test still serves another obligation. | Covered, SH-07/17: availability is not deletion; reviewed assessment protects shared dependents, distinct stale/retired states and retrievable history. |
| 12. B consumes policy only on another branch; C unavailable; stale index or new owner during scan. | Covered, G3, SH-18 and required examples: coherent full local inventory/vector, B discovered, C unresolved, no complete mixed result, generation recheck at use, no owner authority transfer. |
| 13. Legacy record lacks declarations/versions; export lacks objects or coordinator authority. | Covered, SH-10/18 and traceability migration contract: readable originals do not establish independence/new completion; exact provenance, explicit missing scope/migration/registration, no invented history. |
| 14. Compact JSON conflates absent/null/empty, loses Unicode, or leaves lookup context ambiguous. | Covered, SH-07/09/11: preserve semantic distinctions and sufficient context or scoped failure. |
| 15. New numeric revision records, integrity catalog/index and lookup responses outweigh displayed-report savings. | Covered, SH-11/12 and savings section: count all necessary inputs/responses and generated metadata JSON; both aggregate thresholds must pass with individual regressions disclosed. |
| 16. Raw abbreviation becomes ambiguous after another publication. | Covered, SH-01/08: scoped collision expansion and ambiguous-input refusal without rebinding; full IDs for exact operations. |
| Dependency cycles versus ownership/lookup links, unsafe paths and missing targets. | Covered, SH-07/08/15/16/18: only actual dependencies form impact edges; scoped failure for cycles/invalid targets, including cross-owner cases. Ownership/lookup alone does not invent a cycle. |

Additional reopened combinations are covered: unknown field changes are significant; unavailable profiles cannot prove equality; profile identity changes require reviewed migration/reassessment; identical blobs do not bypass external bindings; narrower interfaces cannot be invented retrospectively; changed outward/inherited obligations continue reassessment; old-pin retention never updates the edge; a new consumer pin always creates a new revision; and new/removed refs are detected during capture. No open failure class remains from the reopened review.

## Over-constraint risks

| Earlier risk | Classification and disposition |
| --- | --- |
| Scope grew beyond display formatting to allocation, history, dependencies, migration and project discovery. | Covered by intent and SH-02/03/10/15–18. These are explicit destination requirements; narrowing to a formatter would violate scope. Implementation modularity remains bounded by them. |
| Numeric revisions, integrity storage and graph metadata may erase savings. | Covered by SH-12 and savings accounting. This remains a feasibility risk, not an unanswered behavioral rule: failing either strict aggregate threshold prevents implementation acceptance and requires design revision. A seal does not prove savings. |
| Every individual journey might be required to improve. | Covered by SH-12: strict aggregate improvement in both tokens and JSON bytes; disclose individual regressions. There is no per-journey improvement rule. |
| Specification might require global authority service, identity authentication, arbitrary new checksums or bulk historical rewrite. | Covered by Non-goals, SH-03/04/10 and existing cooperative authority contract. Separate integrity data and exact verification are required; those extra mechanisms are not. Storage/transport implementation is bounded by retained authority and provenance. |
| Concrete reference grammar or per-item redundant checksum scheme could be imposed prematurely. | Bounded by numeric/qualification/revision and integrity invariants, SH-01/02/03/07. Different syntax and Git-backed content integrity are permitted only with identical immutable-resolution and verification outcomes. |

## Under-constraint risks

Every criterion declares `verification_mode: tests`; none claims review-only authority. Required types and observable evidence were independently checked:

| Criterion | Required types | Necessary observable proof |
| --- | --- | --- |
| SH-01 | unit, integration | Default numeric references; sufficient context; scoped raw collisions and full-ID exact operations. |
| SH-02 | unit, integration | Every named item family; numeric sorting; increasing immutable revisions; moves; multi-input ownership and ancestor stability. |
| SH-03 | unit, integration | Separate exact integrity data; shared sources/external evidence; missing/mutated revision mappings fail. |
| SH-04 | integration, e2e | Candidate substitutions and self-declared approval fail through coordinator/completion interfaces. |
| SH-05 | integration | Later runs/accepted revisions do not mutate old entries; historical targets remain exact/retrievable. |
| SH-06 | unit, integration | Canonical equivalence versus exact-byte invalidation and explicit digest semantics. |
| SH-07 | integration | Real Git snapshots/blobs; external bindings despite identical blobs; reviewed profiles; unknown fields; unrelated edits; moves; deletion versus unavailability. |
| SH-08 | unit, integration | Scoped/malformed IDs, real conflicting stale registrations, cycles and immutable targets. |
| SH-09 | unit, integration | Compact versioned round trips preserve Unicode/types/defaults/absent-null-empty distinctions. |
| SH-10 | integration, e2e | Legacy reads, provenance-preserving migration, export/reload and explicit incomplete/unsupported refusal through real entry points. |
| SH-11 | integration, e2e | Selective projection and necessary lookup responses avoid default whole-catalog loading while preserving context/detail. |
| SH-12 | integration | Frozen equivalent real-artifact journeys with pinned tokenizer, complete accounting and both strict aggregate thresholds. |
| SH-13 | integration | Interrupted publication with readers, conflicting retries and fixture cleanup. |
| SH-14 | e2e | Real valid/invalid workflows with executed cases, registered review and exact candidate/contract/source/runner/log lineage. |
| SH-15 | unit, integration, e2e | Every actual dependency family, payload/binding comparison, exact old/new revisions and attributable history without execution rebinding. |
| SH-16 | unit, integration, e2e | Direct/potential impact, independent and multi-input chains, full stop decisions, old pin versus new pin, and eligibility/completion refusal. |
| SH-17 | unit, integration, e2e | Exclusive/shared deletion, reviewed dependency updates/retirement, active filtering and historical retrieval. |
| SH-18 | unit, integration, e2e | Cross-branch/archived/shared-owner discovery, coherent generation capture including new refs, stale/unavailable scope, freshness on use and owner authority. |

The evidence types are adequate minimum obligations, not execution evidence or an accepted test plan. Actual case assertions/selectors/source mappings, TaskGraph scope and independent test-plan review remain necessary under `_ask/docs/spec-test-traceability.md`. A `pass` field, scaffold, opaque command exit, or this document cannot supply those proofs. Existing instrumentation, Red/Green and review rules remain authoritative.

The earlier authority/reuse risk is covered: `evidence.py` anchors accepted obligations to coordinator-owned accepted-tests authority, and `completion.py` verifies registered review, current contract digests, exact final-candidate/source/runner/log identities and applicable execution history. SH-04/14/15/16 explicitly preserve them. Retained item eligibility is neither an accepted-contract amendment nor a fresh final-green run.

The earlier migration risk is covered: SH-10/18 and the migration/authority contract preserve readable history while refusing unsupported or insufficient provenance for new completion. Missing declarations are not proof of a dependency-free owner; missing authority cannot be replaced by an exported candidate file. No historical review-only exemption, approval, numeric revision or Red/Green evidence may be invented.

## Recommended clarifications

No additional normative correction is required for revision 7. G1/G2/G3 are closed by explicit rules and required decision examples, rather than deferred as unresolved behavior. The tables above identify the remaining bounded implementation choices and the outcomes each must preserve. They do not authorize alternate equality, stop, discovery, authority, migration or savings semantics.

Any later finding that cannot satisfy these rules returns through Spec Change. Benchmark feasibility and implementation correctness remain to be demonstrated; specification closure cannot establish either.

## Challenge verdict

**PASS — zero open behavioral blockers for the exact revision-7 JSON and Markdown digests above.**

This independent review supports sealing that specification for consolidated planning. It supersedes the earlier unconditional revision-6 PASS and closes the three reopened gaps against revised normative text. Every earlier deferral, failure-case row and risk has been classified with its binding outcome or bounded mechanism choice.

This decision supplies no complete-intent approval, accepted implementation/test-plan pin, implementation readiness, execution evidence, workstream completion or final acceptance. It neither drafts Plan nor authorizes production implementation. Those claims require their own existing workflow gates and evidence.
