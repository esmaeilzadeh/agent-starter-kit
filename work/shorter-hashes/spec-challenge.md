# Specification Challenge

## Model

- Model: `gpt-6.1-sol`; reasoning effort: `medium` (submitted selection and `models.yaml`). The runtime does not expose an independent model-identity attestation.
- Runtime: Codex, independent Spec Challenge subagent.
- Parent model: not exposed by the runtime; not inferred.
- Reviewer: `/root/shorter_hashes_challenge_r5`.
- Method: formal `kit-03-spec-challenge`; `writing-for-agents` in embedded mode. No implementation, test execution, or plan approval is represented here.

## Specification

- Workstream: `shorter-hashes`.
- Target committed revision: `97b8e94e2e8a087bc34e163a38418f524a17c200`.
- Canonical contract: `specs/current/shorter-hashes.json`, `ask-spec/v1`, revision **5**, **18** criteria (`SH-01`–`SH-18`).
- Canonical JSON SHA256: `3c12c48254c2a93652b7f5085a6cb86d8c0a023fbecb416e4ba290644ccf0636`.
- Proposal: `specs/proposals/shorter-hashes.md`.
- Proposal exact-byte SHA256: `2741452e09df497f7657a518599aa1a2c6678b5c857a098d05400dce8e25ae82`.

Digests were computed from the target commit. JSON canonicalization uses Python `json.dumps(value, sort_keys=True, separators=(',', ':')).encode()`, matching the current traceability contract helper. The Markdown digest includes its exact committed bytes.

Reviewed the intent, proposal, complete JSON criteria, traceability contract, delegation policy, and existing authority/completion code. Relevant existing behavior is in `.agents/ask/verification/traceability/evidence.py` (`_accept_plan`, `load_accepted`, `source_digests`) and `completion.py` (candidate, contract, runner, source, and log binding checks). `_ask/scripts/status.sh` demonstrates existing discovery from workstream refs and archived sources; it does not establish that a complete dependency graph exists today.

The scope assessed includes the user's explicit refinements: Git snapshots and stable item identities; selective item reassessment even inside shared files; project-wide traversal across workstream sources; and workstream-owned reassessment and acceptance. `plan.md` is an unpopulated scaffold and no `test-plan.json` exists. Their absence at this stage is not evidence of missing implementation or a spec failure.

## Ambiguities

No unresolved ambiguity requires a What/Why decision in revision 5. The following boundaries need concrete Plan definitions, as the specification expressly requires:

1. **Discovery completeness.** Define the authoritative owner/source inventory, selected immutable snapshots, archived-workstream treatment, and stale-index detection. Counterexample: owner B consumes A's policy only on `agent/B`; reading the checkout or only A's outgoing edges misses B. SH-18 explicitly rejects that result as complete. A rebuildable index is an optimization, not authority.
2. **Item equivalence.** Specify stable extraction and equivalence rules for each inventoried format, including shared constraints and declaration bindings. Counterexample: editing a global paragraph leaves S1's local paragraph unchanged; a comparator that excludes the global dependency wrongly retains S1's consumers. SH-07/15/16 require meaningful content and all actual inputs to participate.
3. **Reassessment versus completion.** Define how retained eligibility is represented while current exact accepted-contract and final-candidate checks continue to apply. `load_accepted` currently rejects whole-contract changes without reviewed amendment; completion requires final green for its exact candidate. An item can remain unaffected without a historical run becoming a fresh run or the whole workstream becoming complete. SH-04/14/15/16 preserve this distinction; the Plan must not implement retention by bypassing these checks.

Exact schemas, paths, command flags, override ranges, tokenizer selection, and extraction algorithms are implementation-plan decisions. These are not missing user decisions or permission to weaken the specified outcomes.

## Missing failure cases

No uncovered failure case blocks the specification. The independent test-plan review should require explicit cases for these combinations, which are already covered by the cited criteria:

| Counterexample | Required observable outcome |
| --- | --- |
| A six-character prefix becomes ambiguous after another registration. | Reject the old ambiguous input; expand only colliding displays and preserve published identity (SH-01/08). |
| Another branch publishes the same local number; a reader supplies the wrong owner/type context. | Resolve only a sufficiently qualified immutable identity or return a scoped error (SH-02/08/18). |
| New contract is accepted, then Git garbage collection would remove an older authority record or source snapshot. | Retain required history/objects; unavailable objects refuse historical validation and verified-complete export (SH-05/07/10). |
| S1 changes beside unchanged S2 in one file; a shared policy also changes; a descendant has two inputs. | S2 stays eligible only for genuinely unrelated paths; all actual shared-policy and multiple-input paths remain unresolved until reassessed (SH-15/16/18). |
| One owner is unavailable while an index still lists its previous consumers. | Return incomplete analysis with unresolved scope; preserve known affected paths and refuse a project-wide completeness claim (SH-18). |
| A requirement is deleted while its test still supports another active requirement. | Assess and review the updated binding; preserve the shared test and historical runs, with distinct stale/retired states (SH-17). |
| A retain decision changes only a pointer, or a candidate asserts its own independent review. | Neither clears affected paths nor transfers acceptance; enforce attributable authority and evidence reuse rules (SH-04/15/16). |
| Publication stops between writing context and publishing its dependent record. | Readers see complete old/new state; retries preserve immutable targets (SH-13). |
| JSON omission conflates absent, null, and empty; normalization loses Unicode content. | Preserve values and distinguish states except for explicit versioned defaults (SH-09). |
| Short output saves tokens but every lookup loads a large manifest. | Include the manifest and all necessary responses in SH-12 totals; reject claimed savings if aggregate tokens or JSON bytes fail to decrease. |

## Over-constraint risks

The graph, migration, authority, and lifetime requirements make this substantially broader than a display-format edit. They are nevertheless supported by the user's explicit refinements. SH-12 protects the primary goal: a larger graph implementation is unacceptable if the frozen representative journeys fail the aggregate token and metadata-byte comparisons. Readability alone cannot satisfy acceptance.

The specification appropriately leaves storage design open: it requires neither a new authoritative global registry nor per-item checksum/revision histories. Git snapshots can supply committed content identity, while remaining checks preserve their declared byte or canonical-JSON semantics.

Strictly lower aggregate totals permit individual journey regressions, which must be disclosed. This is an explicit acceptance rule, not a hidden requirement that every journey improve. The Plan may not substitute byte savings for token savings.

## Under-constraint risks

Every criterion declares `verification_mode: tests`; none claims review-only authority. The proposal supplies required evidence types. They are suitable for a later independently reviewed test plan, subject to concrete assertions and cases:

| Criteria | Required types | Independent assessment |
| --- | --- | --- |
| SH-01/02/03 | unit, integration | Cover formatter/resolver semantics and persisted producer/consumer behavior, including external evidence. |
| SH-04 | integration, e2e | Candidate substitution must fail through coordinator and actual completion entry points. |
| SH-05 | integration | Reload retained accepted revisions after later registrations and object-retention operations. |
| SH-06 | unit, integration | Test canonical equivalence separately from exact-byte invalidation. |
| SH-07 | integration | Exercise real Git blobs/snapshots, same-file independent items, explicit moves, and deletion versus unavailability. |
| SH-08/09 | unit, integration | Exercise identity/default validation plus conflicting writers and serialization round trips. |
| SH-10/11 | integration, e2e | Legacy/migration/export and selective lookup behavior must pass through real workflow interfaces. |
| SH-12 | integration | Freeze deterministic journeys and tokenizer before implementation; measure complete equivalent inputs and all generated metadata. |
| SH-13 | integration | Inject publication interruption and conflicting retry; check observed state and fixture cleanup. |
| SH-14 | e2e | Run valid and deliberately invalid complete workflows with actual case execution and coordinator review registration. |
| SH-15/16/17/18 | unit, integration, e2e | Cover graph decisions locally, committed multi-owner sources, and resulting eligibility/completion outcomes. |

Canonical criterion IDs are stable, Given/When/Then behavior is observable, and all 18 have a defined evidence path. The absence of case IDs, task scopes, runner selectors, and executable fixtures is expected before Plan. This challenge does not approve those future obligations or supply a plan-review decision.

Legacy records without item declarations must not be interpreted as proven dependency-free. SH-10 migration and SH-18 incomplete-analysis behavior cover this case. The Plan must enumerate which historical formats can be read directly, which need explicit migration, and which lack enough provenance for new completion. Migration may supply scaffolds, never invented approval or execution history.

## Recommended clarifications

No spec revision is required by this challenge. Carry these concrete obligations into Plan:

1. Inventory every eligible producer/consumer and every actual dependency family; map each to a versioned format, authority source, resolver, and migration behavior.
2. Define complete cross-workstream source discovery and a consistent snapshot set; test unavailable and newly advanced owner sources without falling back to checkout state.
3. Specify item extraction, move mapping, global-constraint edges, and attribution for retain/revise/retire decisions. Distinguish immutable record references from logical impact edges when checking cycles.
4. Show how selective eligibility coexists with reviewed accepted-contract amendments and exact execution lineage. Retain historical evidence without relabeling it as new execution.
5. Freeze the SH-12 baseline, corpus, tokenizer, and equivalent workloads before production changes; include lookup costs, shared metadata, and disclosed per-journey regressions.
6. Prepare and independently review the actual test plan, TaskGraph scopes, and executable case assertions; pin their exact contracts under coordinator authority before implementation.

These are Plan deliverables already required by revision 5. Any design that cannot meet them must return through Spec Change rather than lowering the criteria.

## Challenge verdict

**PASS** for the exact revision-5 JSON and Markdown digests above.

Independent review found no remaining specification blocker. Revision 5 preserves the primary token goal, full integrity and exact-operation semantics, coordinator-owned authority, selective item validity, and project-wide impact visibility with owner-scoped decisions. The counterexamples above have specified observable outcomes; their concrete implementations and proof remain Plan work.

This decision makes the specification eligible for subsequent workflow gates. It records no human intent confirmation, accepted test plan, implementation authorization, execution evidence, or final acceptance. In particular, the current intent approval status and the proposed graph scope must be reconciled through the existing intent/workstream gate before implementation proceeds.
