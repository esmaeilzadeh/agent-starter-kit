# Workflow reference surface inventory

This inventory is part of the consolidated planning contract for spec revision 7.
The scope is actual workflow records, agent context, reports, and exact dependency
bindings; no file is converted by blindly replacing hexadecimal strings. The
table names the authoritative producers/readers and the task that integrates
their boundary. All new runtime formats are future task deliverables.

| Family / existing source | Producer and consumer boundary | Required treatment | Task |
| --- | --- | --- | --- |
| Intent confirmation: `_ask/scripts/intent-confirmation.py` | Writes and validates recorded human choice against intent bytes. | Store exact-byte full digest once in integrity data; resolve numeric evidence reference before validating; retain exact-byte invalidation and original human choice. Legacy confirmation remains readable. | 5 |
| Canonical contracts and obligations: `.agents/ask/verification/traceability/contracts.py`, `coverage.py`, `evidence.py` | `contracts_at`, `json_at`, canonical digest and accepted-plan registration/reload. | Typed envelope normalization yields existing canonical contract values before checks. Spec/part and plan/item identities/revisions map to exact source/path/items. All real input bindings participate; candidate catalogs cannot establish accepted-tests authority. | 3, 5 |
| Registered execution and review: traceability `adapters.py`, `evidence.py`, `service.py`, `completion.py`, `cli.py` | Executes selected cases, persists reports/ledger/log bindings, registers semantic review, checks current/historical completion, writes results. | Deduplicate full contract/source/runner/log/review digests into immutable separate integrity entries; ordinary records/projections use numeric references. Keep exact case/runner/source/contract/log lineage, actual TDD history, and independent coordinator registration. | 2, 5 |
| Static verification: `.agents/ask/verification/run.py` | Captures candidate/CheckPlan/runner/static-log identity and aggregates completion. | Normalize compact records and preserve every exact verification requirement; full verification remains an executable completion gate. Internal full-value trust bootstrap is explicitly excepted below. | 5 |
| Inner-loop runtime: `_ask/scripts/inner_loop/state.py`, `evidence.py`, `driver.py`, `integrate.py`, `allowlist.py` | Reads/writes CAS state, task evidence, selected runner output, recovery and FF integration receipts; emits per-task prompts. | Work/plan-qualified numeric task/test versions and selective context; compact versioned records resolve full candidates, runner and log data internally. One writer, CAS, allowlists, lock/retry and FF-only behavior remain unchanged. No outside-task case receives current task evidence. | 6 |
| Engineering capture/admission: `_ask/scripts/engineering_model/snapshot.py`, `admission.py`, `canonical.py`, `identities.py`, `validation.py`, `workflow.py`, `migration.py` | Captures source closure and canonical definitions, validates generation/model admission, applies legacy migration. | Resolve numeric source/item versions at the capture boundary, retain exact original source/plan bindings, and register all actual shared/global inputs. Preserve strict unknown/missing/schema behavior. Existing model node IDs are legacy identities with stable mappings. | 3, 7 |
| Engineering evidence/agents/UI: `projection.py`, `context.py`, `evidence.py`, `flows.py`, `actions.py`, `workbench_sources.py`, `workbench_evidence.py`, `readable_tests.py`, `readability.py`, `benchmark.py`, workbench readers | Formats selected model/task/test/review/evidence and loads details/history on demand. | Default selected projections carry sufficient numeric context; explicit integrity detail resolves full records on demand. Preserve actual captured source/status/review meaning. Internal content-addressed bytes remain integrity data; visual/UI redesign is excluded. | 7 |
| Workstream inventory and results: `_ask/scripts/status.sh`, `record-result.sh`, `ask`, `_ask/scripts/ask-complete.sh` | Discovers committed live/archived sources and shows lifecycle/result/source refs. | Use coherent authoritative coordinator/archive inventory with exact generation/vector; keep status and historical results readable; add refs commands/completion and compact source/version displays. Ordinary ownership/link references alone create no impact edge. | 4, 8 |
| Shared project inputs: protocol policies, spec clauses, runner and source inputs already consumed by the above | Each consumer declares exact referenced items and inherited/global constraints. | Comparison/dependency profiles include all actual input bindings, explicit owner/version, and relevant shared obligations; unknown owners/formats make analysis incomplete. Read sources on their pinned refs rather than checkout. | 3, 4, 5–8 |
| New integrity/graph/decision/projection data: `.agents/ask/workflow_refs/*` | Public reference facade and refs CLI. | Separate per-owner integrity file; immutable append-only item/revision entries; coherent project vectors; reviewed retain/revise/retire; migration/export/import; compact selective output. Metadata and necessary lookups count in the frozen benchmark. | 2–4, 8–10 |
| User/agent documentation: `_ask/docs/workflow-references.md`, root `README.md` | Explains canonical grammar, inherited context, exact integrity inspection, supported failures and migration. | Document the delivered interfaces and limitations; no normal workflow requires a full catalog read. Existing unrelated prose and historical examples are retained. | 8, 10 |

## Full-value exceptions and exact semantics

These exceptions are required integrity/operation data, never shortened values
used to verify content. Each is reported in the final measurement.

1. Git plumbing receives resolved full commit/blob IDs for exact `show`,
   `cat-file`, ancestry, retention, authority CAS and fast-forward operations.
   Normal domain references use numeric identity/revision instead.
2. The coordinator-owned accepted-tests authority and minimum catalog trust
   bootstrap retain the full digests required to authenticate their exact
   registered data under the existing cooperative authority model. This avoids
   asking candidate-controlled reference data to establish its own acceptance.
   Full values may occur in that authority bootstrap and the separate integrity
   file; they are not copied into ordinary reports or agent projections.
3. Existing canonical contract digests and exact-byte intent/log checks resolve
   full authoritative values before validation. Their algorithm and semantics
   remain explicit; hash display prefixes and numeric references prove neither.
4. Original execution logs, source files, legacy approval/execution records and
   content-addressed historical object bytes/filenames remain intact for audit.
   They are not bulk rewritten. New outer records and default displayed
   references use the numeric scheme. Internal content-addressed names remain
   storage addresses, not the domain-ID API.
5. An explicit raw Git/hash inspection or `refs show --integrity` can display full
   data. Any abbreviated raw inspection declares its scope, grows on collision,
   and refuses ambiguous input. Full integrity-detail responses count whenever
   the frozen question requires them.

## Comparison and dependency profile boundary

Supported first-release profiles are `structured-item/1` and `prose-item/1` as
fixed in the plan. Stable item IDs define extraction boundaries; explicit edges
include declared global constraints, source, policy, runner, and every actual
input relationship. JSON key order/serialization whitespace are presentation;
arrays, values/types, Unicode and absent/null/empty distinctions are significant.
Prose defaults to exact extracted bytes. Item-file blob equality does not bypass
bindings stored elsewhere. Unknown fields participate; unavailable profiles,
constraints, targets or declarations prevent equivalence and complete clearance.

The inventory describes support families, not a declaration that historical
records already contain enough item/dependency provenance. Legacy reads remain
available. Explicit migration registers only mappings supported by actual source
evidence, starting a new published item-version history without inventing prior
item revisions. Unknown historical dependencies remain unresolved for new-context
completion. Every unclassified hash/dependency surface found during a task is
reviewed into the inventory/contract before new work or a completeness claim.
