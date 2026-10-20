# Specification: Compact workflow references and integrity evidence

## Status

PROPOSED — revision 3. The user requested this specification; intent confirmation,
formal Spec Challenge, and an accepted implementation plan remain outstanding.
This document does not record approval or execution evidence.

## Goal

Reduce tokens consumed by workflow JSON, prompts, CLI output, and reports.
Improve readability second. Replace repeated integrity metadata with resolvable
references while preserving exact approval, review, source, and execution binding.

## Non-goals

- Change hash algorithms, truncate authoritative checksums, or weaken verification.
- Rewrite unrelated JSON, prose, or historical execution evidence.
- Introduce a project-wide mutable registry that grants acceptance authority.
- Infer missing approvals, test executions, or historical Red/Green evidence.

## Behavior

### Ordinary references

Ordinary Git/hash references use a repository default minimum of six hexadecimal
characters, with a validated per-work override. Hash displays and lookups declare
their scope. Only colliding references grow until they resolve uniquely; ambiguity
is an error. An existing abbreviated reference that becomes ambiguous is rejected
rather than silently rebound. Exact Git operations receive resolved full IDs.
Display prefixes never supply integrity evidence.

New task/test references use unpadded numeric local IDs and readable qualified
forms: `<work>/task/<task>` and `<work>/test/<task>/<test>`. Work may be inherited
from an explicit containing context; references across workstreams include it.
Legacy identifiers remain resolvable through a stable mapping. Published IDs are
never recycled or silently assigned a different meaning.

### Shared integrity records

An immutable accepted-contract record binds the exact spec, test plan, TaskGraph,
policy, and reviews required by the existing workflow. Later run/evidence records
have independent immutable lifetimes. Creating a log cannot edit an accepted
contract. Related records store short references instead of copying the full
contract digests and common metadata into every report or test case.

Each full checksum is registered once per workstream integrity catalog and digest
semantics. Revisions can reuse that entry. Unique output checksums still need a
full authoritative value. A transfer copy of an authoritative record is permitted;
downstream reports must not expand references into repeated full checksums by
default. Cross-workstream reuse names the owner explicitly.

For example, within a declared workstream, a report could contain:

```json
{"contract":3,"task":7,"run":4,"log":12,"status":"pass"}
```

This is an illustrative projection. The Plan defines exact versioned schemas,
storage paths, and resolver interfaces. Every reference must identify its work,
record type, and immutable target through explicit or inherited context. A bare
number without sufficient context is invalid.

### Dependency revisions

Every derived artifact revision binds the exact immutable revisions of all its
actual inputs. This rule applies to every existing dependency type: spec to plan,
plan to task, task to test, and other declared relationships involving test plans,
graphs, source, policies, runner definitions, reviews, or execution evidence.
The Plan inventories the actual dependency graph; examples do not impose a linear
pipeline or invent dependencies from ownership labels or ordinary lookup links.

A derived revision's canonical checksum covers its content and complete input
bindings, including their work/type/revision context. Shared checksum storage
preserves these directed edges. Placing artifacts together in a manifest does not
establish derivation. Adding, removing, or changing an input binding requires a
new derived revision and checksum, even when its substantive payload is unchanged.

When an input changes semantically, determine the affected downstream closure for
the new selected workflow context. Reject directly and transitively stale artifacts
until each affected dependency is resolved. Do not wait for an intermediate artifact
to be rewritten or its checksum to change before detecting downstream staleness.
Artifacts with multiple inputs require all their bindings to be valid; unaffected
branches remain eligible. Existing artifacts retain their original input bindings
and remain available for validation in their historical context.

To use changed inputs, regenerate or explicitly revalidate each affected derived
artifact in dependency order, publish a new immutable revision with the correct
bindings, and calculate its new checksum. Apply the review and coordinator acceptance
requirements already associated with that artifact type. Recomputing a checksum,
editing a catalog entry, or moving a current pointer cannot transfer derivation,
approval, or execution evidence to the new context.

For example, a recorded `spec/1 -> plan/1 -> task/1 -> test/1` chain remains valid
for its original context. Selecting `spec/2` makes the affected plan, task, and
test revisions stale for that new context. Rebuilding or revalidating the chain
produces newly bound revisions and checksums; changing only the spec's catalog
checksum cannot make the old chain current. A task-only change similarly affects
its dependent tests without changing unrelated tasks or upstream artifacts.

Test definitions and execution records are distinct artifacts. Historical runs
retain their exact test/source/runner/contract bindings. They cannot be relabeled
as new executions. Any reuse requires the existing evidence eligibility rules and
an explicit attributable decision where those rules require one; otherwise new
execution is necessary. Canonical-equivalent formatting changes retain existing
equivalence rules and do not require artificial semantic revisions.

### Authority and identity

Contract references resolve through the existing coordinator-owned
`refs/ask/accepted-tests/<work-id>` authority and its retained accepted history.
Candidate-controlled JSON and short aliases cannot authorize new obligations,
change accepted content, or supply independent review decisions. Run and review
references retain the existing coordinator registration requirements.

The coordinator serializes registration and rejects conflicting stale writes.
Identical local IDs on different branches or in different workstreams must not
resolve to the wrong object. A conflict requires fresh allocation or an explicit
error; published references remain bound to their original target. Published
entries are immutable, although an authority index can advance atomically.

Checksums preserve their existing semantics: spec/plan contracts hash canonical
sorted compact JSON; byte-bound artifacts such as intent and logs hash their exact
bytes. Each catalog entry identifies the algorithm and digest semantics. Identical
digest strings with different semantics cannot imply interchangeable records.

A full pinned Git commit plus repository-relative path may replace redundant
tracked-file checksum fields only when the validator loads the exact object and
preserves the required byte or canonical-JSON comparison. Uncommitted execution
outputs retain full checksums in evidence records. Missing commits, paths, or
catalog entries produce an explicit failure; no consumer falls back to HEAD,
current files, or an unchecked value.

### JSON and agent context

Generated workflow JSON uses compact serialization and carries shared context
once per record group. It preserves values, required evidence, and distinguishable
states. Omitted fields require versioned defaults; absent, null, and empty values
cannot become interchangeable accidentally. Descriptive keys are preferred where
they do not defeat token savings. Semantic canonicalization remains deterministic.

Agent-facing projections return requested tasks, tests, status, and relevant
evidence references. They resolve additional records on demand and avoid loading
the entire integrity catalog by default. Failure diagnostics identify the missing
or conflicting reference and its scope. Detailed evidence remains retrievable.

### Coverage and compatibility

The Plan inventories each producer and consumer in these affected families:

| Family | Required treatment |
| --- | --- |
| Intent confirmation | Preserve exact intent-byte invalidation and recorded human choice. |
| Spec/test traceability | Deduplicate contract, policy, source, review, and execution bindings while retaining coordinator authority. |
| Inner-loop state and evidence | Preserve task, candidate, baseline, runner, lock, and integration identities. |
| Engineering snapshots and workbench | Resolve qualified references without losing historical snapshot or plan bindings. |
| Status, results, prompts, CLI reports | Show compact references and retain exact values for operations that require them. |

Every eligible hash surface must be mapped to ordinary abbreviation, shared
integrity reference, derivation from pinned Git content, or a justified full-value
exception. New readers support existing schema versions. New writers use explicitly
versioned formats. Unsupported versions refuse validation with a migration error.

Existing committed records remain readable without bulk rewriting historical
evidence. An explicit migration preserves original records and provenance, rejects
unresolved references, and cannot manufacture approval or execution history. Export
includes the referenced immutable records and required Git objects, or identifies
unavailable dependencies and refuses any claim of verified completeness.

## Interfaces

- Existing `./ask` workflow entry points retain their purpose and safety checks.
- The Plan specifies schema versions, configuration keys, reference resolution,
  selective output, and migration/export interfaces before implementation.
- New readers normalize legacy and new records to the same validation semantics.
- Any operation requiring integrity resolves full authoritative data internally.

## Constraints and invariants

- Human approval binds the exact intent; independent decisions retain attribution.
- Accepted obligations, candidate/source lineage, test assertions, logs, and runner
  identities remain verifiable. Short references alone grant no authority.
- Every derived revision binds all actual inputs. Semantic changes invalidate the
  affected downstream closure for the new context; unchanged historical bindings
  and unrelated branches retain their meaning. Checksum updates cannot restore
  eligibility or transfer approval/execution evidence.
- Immutable records remain reachable for historical validation and export.
- Records never include their own digest in the bytes being hashed. Reference
  cycles, missing targets, duplicate conflicting IDs, and unsafe paths are rejected.
- Registration and record publication are atomic for readers. Interrupted writes
  do not publish dangling references; retries cannot mutate published identities.
- Required artifacts and dependencies must exist before a success report is issued.

## Failure cases

Reject ambiguous prefixes, conflicting registrations, candidate-substituted
manifests, changed logs, stale accepted obligations, unavailable Git objects,
malformed versions, incomplete imports, cycles, unsafe paths, and interrupted
publication. Return a stable reason and scoped reference. Failed resolution cannot
be treated as successful verification, approval, or completion.

## Acceptance criteria

Canonical Given/When/Then criteria are in `specs/current/shorter-hashes.json`.
They are proposed contract metadata, not an accepted pin. All require executable
evidence; no review-only exemptions are declared.

| Criterion | Observable requirement | Planned evidence types |
| --- | --- | --- |
| SH-01 | Scoped prefixes, configurable minimum, collision expansion, exact Git resolution. | unit, integration |
| SH-02 | Stable readable task/test IDs and work qualification. | unit, integration |
| SH-03 | Shared full checksums and metadata replace repeated downstream copies. | unit, integration |
| SH-04 | Candidate-only substitutions cannot alter coordinator acceptance authority. | integration, e2e |
| SH-05 | Immutable contracts and later evidence have separate lifetimes and retained history. | integration |
| SH-06 | Byte and canonical-JSON digest semantics retain their invalidation rules. | unit, integration |
| SH-07 | Pinned Git derivation resolves exact content and fails on unavailable dependencies. | integration |
| SH-08 | Scoped allocation, concurrent conflicts, malformed refs, and cycles fail safely. | unit, integration |
| SH-09 | Compact JSON preserves values, defaults, and deterministic validation. | unit, integration |
| SH-10 | Legacy reads, explicit migration, and export preserve provenance and authority. | integration, e2e |
| SH-11 | Selective agent projections resolve evidence without loading whole catalogs. | integration, e2e |
| SH-12 | Fixed representative workloads demonstrate lower total tokens and JSON bytes. | integration |
| SH-13 | Interrupted publication and retries preserve immutable references and clean source. | integration |
| SH-14 | Complete workflow still rejects stale or modified evidence and accepts valid evidence. | e2e |
| SH-15 | Every existing dependency type preserves exact immutable input bindings and requires a new derived revision/checksum when bindings change. | unit, integration, e2e |
| SH-16 | Changes invalidate the affected downstream closure, including multiple-input nodes; unrelated branches and historical contexts remain valid. | unit, integration, e2e |

### Savings measurement

Before implementation, the Plan freezes a baseline corpus, its source commit,
tokenizer name/encoding/package version, and deterministic workload scripts.
Token counts use the same tokenizer on both sides; byte counts are reported
separately and cannot stand in for token counts.

The corpus covers: resuming a small workstream; reviewing a multi-task workstream
with repeated contract/source digests; and verifying completion with historical
runs and detailed logs. It includes representative committed traceability and
inner-loop artifacts, not only synthetic repeated hashes. Baseline and new
workloads answer identical questions with equivalent evidence access.

Count all agent-visible inputs and lookup responses required for each journey,
including any manifest loads. Count all generated metadata JSON, including shared
catalogs, when measuring storage. Report each journey and aggregate totals.
Acceptance requires strictly fewer aggregate tokens and metadata JSON bytes than
baseline; disclose any individual regressions and retained full-value exceptions.
Removing required evidence or skipping necessary lookups cannot count as savings.

## Open questions

Intent confirmation and formal independent Spec Challenge are pending. Exact
schemas, catalog paths, tokenizer, corpus revisions, and command flags are Plan
deliverables constrained by this spec; they are not claims of completed work.
If the fixed benchmark cannot demonstrate savings, revise the design before
implementation is accepted.

## Source intent

`work/shorter-hashes/intent.md`, committed at `06daf1e`.
The prior independent design challenge supplied the authority, lifetime,
digest-semantics, availability, and measurement counterexamples addressed here.

## E2E

Applicability: `applies`

Journeys: create and accept a contract through the coordinator; register task/test
references; execute and review runs; query compact status and evidence; verify
completion; reload old contract revisions; and export/reload an evidence bundle.
Repeat with a candidate-only substituted manifest, modified log, stale contract,
same local IDs in different works, conflicting registration, and missing Git object.
Exercise spec-to-plan, plan-to-task, task-to-test, and other actual dependency
edges; change a root, an intermediate task, and one input of a multiple-input
artifact. Reject stale descendants before intermediate checksums are refreshed,
then rebuild/revalidate the affected chain and confirm unrelated branches remain
eligible. Historical execution records retain their original bindings.

Observable outcomes: short references resolve to the exact intended records,
legitimate workflow outcomes match the baseline, altered or unavailable evidence
refuses completion, and the fixed workloads meet SH-12.

Environment/data: isolated temporary Git repositories and worktrees with local
coordinator authority refs, legacy and new record formats, repeated/full digests,
deliberate prefix collisions, source changes, and execution logs. No external
service is required for workflow validation.

Reset: remove only fixture-owned repositories, worktrees, and runtime records;
release their locks and processes. The real workstream remains on its original
branch with a clean worktree and committed source artifacts.
