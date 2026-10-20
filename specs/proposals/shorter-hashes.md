# Specification: Compact workflow references and integrity evidence

## Status

SPECIFICATION CANDIDATE — revision 7. This revision closes the behavioral gaps
identified when the revision-6 challenge was reopened: item equivalence,
propagation stopping, and coherent project discovery. The user authorized closure
with “continue till spec sealed”, then extended the stop point to a consolidated
plan and clear tasks. `work/shorter-hashes/spec-seal.md` records the exact reviewed
contract and closure decision once independent review is complete.

Specification closure does not supply complete-intent confirmation, an accepted
implementation/test-plan pin, execution evidence, or final workstream acceptance.
The scoped endpoint is planning readiness; implementation is outside this run.

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

### Numeric identities and revisions

New specs, spec parts/requirements, plans, plan items, tasks, and tests use
unpadded positive numeric local IDs qualified by their work, type, and related
parent identities. Each artifact/item has a separate positive numeric revision.
The stable logical ID identifies the item; the revision identifies its immutable
version. Published identities and revisions are never recycled or rebound.
Numeric components use numeric-aware sorting.

Parent prefixes express the declared ownership hierarchy. Dependencies remain
explicit edges: a plan or task may consume several upstream items without being
copied under every input. The Plan defines each type's parent context and exact
versioned syntax. A qualified reference must resolve one owner, type, parent
chain, item, and revision; local shorthand may inherit only explicitly declared
context. Cross-workstream references name the owner. Moving an item requires an
explicit historical identity mapping; it cannot silently retarget old references.

For illustration, a task could be qualified by work/spec/plan/task numeric IDs,
with a separate numeric revision. The user's `spec/<revision>` and
`spec/parts/<part>/<revision>` examples convey numeric version references, not a
required literal grammar. Ancestor logical IDs qualify identity; ancestor revision
changes do not by themselves rename or revise every descendant. Exact upstream
versions are pinned in dependency bindings.

A meaningful item-content or dependency-binding change publishes a fresh revision
for that item under the comparison rules below. Revision numbers increase within
the same logical identity; concurrent publication cannot reuse an existing number.
Unrelated edits, explicitly permitted presentation differences, and repository
commit changes alone do not increment its revision. A new binding publishes a new
revision even when the item's payload is retained. Historical revisions keep their
original source and bindings; they are not relocated to the latest snapshot.
Existing exact-byte approval/evidence semantics still apply.

Ordinary workflow references use these numeric identities and revisions. Hashes
remain integrity/source data resolved from a separate file. Explicit Git/hash
inspection may show scoped abbreviations: collisions expand, ambiguous inputs
fail, and exact Git operations receive full IDs. A six-character hash default is
not the domain-reference scheme. Legacy identifiers remain resolvable through a
stable mapping without rewriting historical records.

### Shared integrity records

An immutable accepted-contract record binds the exact spec, test plan, TaskGraph,
policy, and reviews required by the existing workflow. Later run/evidence records
have independent immutable lifetimes. Creating a log cannot edit an accepted
contract. Related records store short references instead of copying the full
contract digests and common metadata into every report or test case.

Store full checksums and exact Git source identities in a separate integrity file,
keyed by qualified numeric item/revision references. Ordinary spec, plan, task,
test, and report records reference numeric revisions rather than embedding hashes.
Resolve those references to immutable full integrity data for verification; a
number alone grants no authority. Shared context may store repeated full source
IDs once, and projections load only requested entries.

For committed artifacts, the integrity file binds each referenced item revision
to its exact Git snapshot, repository-relative path, stable item ID, and declared
content/binding comparison rules. Git retains immutable content and history; the
numeric revision is the public version reference. Git object identities can
supply committed-content integrity without requiring a second generated checksum
for every item. Existing byte-bound or canonical-JSON checks retain the full
digests their semantics require, in the separate file. Evidence outside Git retains
retrievable artifacts and full authoritative checksums, stored once per workstream,
algorithm, and semantics where safely reusable. Cross-workstream references name
the owner explicitly. Retain required Git objects and integrity entries for history.

For example, within a declared workstream, a report could contain:

```json
{"contract":3,"task":7,"run":4,"log":12,"status":"pass"}
```

This is an illustrative projection within declared item/revision context; the
numbers are not sufficient to distinguish multiple versions without that context.
The Plan defines exact versioned schemas, the separate integrity-file path,
parent rules, revision publication, and resolver interfaces. Every reference must
identify its work, record type, and immutable target through explicit or inherited context. A bare
number without sufficient context is invalid.

### Item dependencies and Git history

The dependency graph's nodes are artifact items, such as a requirement, plan item,
task, or test definition. Each edge references the qualified numeric source item
and exact numeric revision reviewed by the dependent item. The separate integrity
file resolves that version to its pinned source snapshot, file path, and stable
item ID. This applies to every actual dependency, including shared/global
constraints, source, policy, and runner inputs. Ownership
labels and lookup links alone do not establish a dependency. The Plan inventories
these edges and defines deterministic item extraction and comparison per format.

Git preserves source history; numeric per-artifact/item revisions provide stable
version references and resolve through the separate integrity file. Existing
revision entries are immutable. Stable IDs survive section movement and are never
recycled. File or ownership moves need an explicit historical mapping; missing or
duplicate IDs cannot be resolved by guessing. Compare against an explicitly
selected candidate snapshot, not whichever commit HEAD happens to name during validation.

A different repository commit or file's last modifying commit is not an
invalidation decision. Identical file blobs supply a payload fast path only;
external dependency declarations, applicable shared constraints, comparison-profile
identity, and exact-byte authority rules must still be checked independently.

### Normative item comparison

Compare two versions of one logical item using its payload and complete declared
input bindings. Payload includes all behavior-, obligation-, assertion-, and
lifecycle-bearing fields of that item. Bindings include each actual input's
qualified identity, exact revision, and dependency role, including global/shared
constraints stored outside the item's file. Ownership and ordinary lookup links
are not dependency bindings. Changing any input revision/role is a binding change,
even when that source revision is later judged equivalent for a consumer.

Every supported format has an immutable versioned comparison profile established
and independently reviewed before use. It specifies extraction boundaries and an
exhaustive list of permitted presentation exclusions/normalizations. By default,
all item fields participate; an unknown field is significant. Structured JSON
allows object-key order and serialization whitespace differences while preserving
array order, types, strings/Unicode, and absent/null/empty distinctions. Prose uses
exact extracted UTF-8 bytes unless its pre-reviewed profile expressly permits a
presentation normalization. Requirements, assertions, numeric values, dependency
bindings, and inherited/global obligations cannot be excluded as presentation.
Reordering separately identified independent items does not reorder one item's
semantic array. A profile cannot be changed after a source edit merely to call
that edit equivalent; profile changes require reviewed migration/reassessment.

For the same profile and logical identity, equal payload plus equal bindings means
no new item revision. A changed payload or binding requires a new revision and
reassessment through actual dependencies. If extraction, a profile, a binding,
or an applicable constraint is unavailable or unsupported, comparison is
incomplete: it cannot establish equivalence, retain eligibility, or clear impact.
Byte-bound intent approval and execution logs continue to use exact-byte checks,
even where a separate item's semantic comparison would ignore presentation.

These rules define “meaningful change”. Extraction code, storage fields, and
profile encoding remain Plan choices within these boundaries.

### Project-wide graph and workstream ownership

Dependencies form one logical project-wide graph. Each workstream owns and records
its artifacts and outgoing dependency declarations. An edge to another workstream
uses an explicit qualified numeric identity and revision, including owner and
parent context. Its integrity entry supplies the exact source snapshot, path, and
stable artifact item ID. Local shorthand is permitted only inside an explicitly
declared owner context. Identical local IDs in different owners remain distinct.
Shared project artifacts have a declared canonical owner and identity; consumers
reference that identity rather than creating unrelated local copies of it.

Impact analysis discovers committed dependency declarations across workstreams,
including consumers outside the checkout. Every complete result is scoped to a
recorded authoritative owner/ref inventory and immutable source/candidate snapshot
vector. For this local cooperating-repository scope, the inventory enumerates all
local live `agent/<work-id>` coordinator refs, archived workstreams on the selected
integration/archive sources, and explicitly registered shared owners. Task refs
are not separate workstream owners. The inventory records the selected integration
and archive refs and their full source IDs. Local discovery cannot claim knowledge
of unfetched remote workstreams; such scope must be fetched/registered first or
reported outside the captured scope. Missing declarations in a known owner are
incomplete discovery, never proof that the owner has no dependencies.

Capture and record the entire ref-name/source-ID set and chosen source/candidate
vector as one consistent observation. Cooperating publishers serialize against
capture, or capture detects any intervening inventory/ref generation change and
retries or reports incomplete. Detect new/removed owner refs as well as advanced
ones; a mixed scan cannot report completeness. Every edge resolves its exact
pinned source even when that differs from an owner's selected current snapshot.
A derived index must match this captured inventory/vector and remain rebuildable.
Report that exact scope with affected owners/items/paths and unresolved targets.

A complete result speaks only for its recorded vector. Later publications do not
rewrite that historical result. New-context clearance/completion must match its
selected applicable vector and recheck the inventory generation before using the
result; changed relevant scope requires fresh analysis. Unavailable sources,
unsupported profiles, inconsistent capture, and stale indexes prevent complete
clearance. The Plan chooses inventory serialization and capture mechanics; it
cannot narrow the owner universe or accept a mixed snapshot as complete.

For example, changing a shared policy marks every direct consumer of that policy
for reassessment across the project, and traces their potentially affected
descendants. Changing one workstream's requirement reaches only its actual
dependents, including those owned by other workstreams. It leaves independent
requirements and plans eligible, even when they share files or local IDs.

Ownership limits writes, not impact visibility. Reports identify each affected
item's owner and exact dependency path. Reassessment and acceptance remain with
that owner's existing authority. Traversal cannot silently edit another
workstream, authorize its implementation, or clear its unresolved impact.

Missing owner declarations, unavailable dependency sources, stale project indexes,
or unsupported schemas cannot be treated as an empty dependency set. Report an
explicit incomplete analysis with unresolved owners/targets; do not claim a
complete project impact result or clear potentially affected paths. Apply cycle,
identity-conflict, deletion, and availability checks across workstream boundaries
as well as within one workstream.

### Partial invalidation and reassessment

A changed input item makes its direct dependents need reassessment. Traverse the
actual dependency edges to identify downstream items as potentially affected;
this impact set does not automatically require rewriting every descendant.
Unresolved affected paths cannot authorize completion in the new context.
Unrelated branches remain eligible. Multiple-input items require all relevant
inputs and affected paths to be resolved. Cycle and missing-target checks apply.

Reassessment proceeds in dependency order and records the outcome against exact
old/new numeric item revisions and resolved snapshots with the attribution,
review, and coordinator authority required for that artifact type:

- Retain: the dependent item still satisfies the changed input. Record the
  assessment and any new revalidation binding; a changed binding publishes a new
  item revision. Preserve the original version, review, and content in Git history.
- Revise: change the dependent content or obligations, commit it, and reassess
  its consumers against the changed item.
- Retire: the item no longer serves an active obligation; retain historical access
  and remove it from the default active workflow.

### Normative propagation-stop decision

A stop applies to named consumer edges within one captured analysis context.
The decision records the exact old/new upstream and dependent revisions, the
consumer revisions remaining eligible, every examined affected input path,
comparison-profile identities, review evidence, and the applicable owner-scoped
review/coordinator attribution. Missing authority or an unresolved relevant input
prevents clearance.

The consumer-facing contract comprises the item's externally relied-on outputs,
assertions, invariants, authority/reuse restrictions, and all applicable inherited
or shared obligations on that edge. Every obligation-bearing field participates
by default. Narrower interfaces require explicit, pre-existing reviewed dependency
declarations; a reviewer cannot invent an exclusion after an input changes.
A changed internal input-version binding creates a new item revision even when
this consumer-facing contract remains equal. Equality of local prose or code alone
never establishes equality of inherited obligations.

A reviewed retain decision may stop propagation only when that complete
consumer-facing contract is unchanged, the dependent still satisfies the new
upstream obligations, every relevant input path is resolved, and existing evidence
reuse and accepted-contract rules permit the specific retained consumers. If any
condition is false or unproven, continue reassessment. A revised outward obligation
always reaches actual consumers.

Stopping does not mutate an edge or historical run. A retained consumer may remain
pinned to its original dependent revision only with explicit reviewed validity in
the new captured context. A consumer that updates its pin receives a new revision
for that binding change. Neither representation relabels old executions or waives
exact candidate/contract/runner/source/log requirements. A new final-candidate run
is still required wherever the existing completion contract requires it.

### Required decision examples

These examples are normative outcomes, independently of storage or algorithms:

| Change / evidence | Required decision |
| --- | --- |
| JSON key order/serialization whitespace changes; item values and input bindings are equal. | Same item revision under its JSON profile; byte-bound approval/log edits still invalidate their exact-byte evidence. |
| Unrelated item S2 changes in the same file as S1; S1 payload/bindings/constraints remain equal. | S1 keeps its revision and independent consumers stay eligible. |
| Item file blob is identical but an external dependency changes from input revision 1 to 2. | Publish a new item revision and reassess; blob equality cannot establish an unchanged item. |
| An inherited timeout changes from 10 to 20; local P prose still says “follow the requirement”. | The inherited obligation differs; P requires reassessment and an unchanged-prose stop is invalid. |
| P2 changes an internal binding, while review proves its entire consumer-facing contract equal to P1 and satisfaction of new inputs. | P2 is a fresh revision; a named T1 may retain its original P1 pin only with recorded new-context validity and all other inputs resolved. No edge or run is relabeled. |
| T changes its pin from P1 to P2, even with identical task text. | Publish T2; preserve T1 and its evidence. Reassess actual T consumers under the same rules. |
| A retain decision covers P, but T also has an unresolved changed input Q. | T remains unresolved; P's decision cannot clear Q's path. |
| Owner B exists only on another branch, or a new owner appears while inventory is scanned. | Include B in the coherent captured scope; serialize/retry capture or report incomplete, never complete from mixed refs. |
| An extractor/profile, owner declaration, integrity entry, or pinned object is unavailable. | Report incomplete/unavailable with exact scope; do not infer deletion, equivalence, independence, or successful clearance. |

For independent chains `S1 -> P1 -> T1 -> X1` and `S2 -> P4 -> T4 -> X4`, changing
S1 reaches only its actual dependents. A reviewed P successor can preserve named
T1/X1 eligibility under the stop rules above. A change to P's outward obligations
continues through T1/X1. A linked shared constraint reaches both chains.

Test definitions and execution records remain distinct. Historical runs keep
their exact test/source/runner/contract bindings; revalidation cannot relabel them
as new executions. Reuse must satisfy existing evidence rules and applicable
review/acceptance requirements; otherwise run new executions. This proposal does
not itself waive existing coordinator acceptance or completion checks.

### Deletion and retirement

Deleting an item triggers the same graph impact analysis. Stale means an active
item needs reassessment; retired means it is excluded from the active workflow
and retained only for historical reference. A missing source cannot count as a
satisfied dependency. Assess whether each dependent still serves another active
requirement before retiring it; shared tasks/tests may remain active after an
explicit reviewed dependency update. Propagate the resulting changes through
actual edges. Preserve deletion/retirement decisions, original bindings, and
historical evidence in Git; default active views exclude retired items and allow
explicit historical retrieval. Do not delete executable tests merely because one
supporting requirement was removed.

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

Comparisons preserve their existing semantics: canonical JSON equivalence for
structured contracts and exact bytes for intent approval and byte-bound evidence.
When checksums remain necessary for external evidence, their algorithm and digest
semantics are explicit; short references cannot replace integrity verification.

Qualified numeric item/revision references resolve through the separate integrity
file to pinned Git snapshots, exact paths, and item IDs. Missing revision entries
or altered integrity mappings fail without treating another version as equivalent.
Missing objects, unsafe paths, ambiguous item IDs, or absent snapshot records fail explicitly without
falling back to HEAD, current files, or unchecked values. A missing item in a valid
candidate document enters deletion handling; an unavailable document/object is an
availability error and cannot be inferred to mean deletion. External execution
outputs retain full checksums and retrievable artifacts.

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

Every eligible hash surface must be mapped to a numeric item/revision reference
with separate integrity data, derivation from pinned Git content, explicit raw
Git/hash inspection, or a justified full-value verification exception. New readers support existing schema versions. New writers use explicitly
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
- Impact queries discover dependencies project-wide and return owner-qualified
  affected items, dependency paths, and any unresolved scope or targets.

## Constraints and invariants

- Human approval binds the exact intent; independent decisions retain attribution.
- Accepted obligations, candidate/source lineage, test assertions, logs, and runner
  identities remain verifiable. Short references alone grant no authority.
- Dependency binding and impact analysis operate on parent-qualified numeric
  artifact/item identities and exact numeric revisions resolved to Git snapshots. Changed direct inputs require reassessment; downstream impact is
  potential until resolved. Unrelated items and historical bindings remain valid.
- Clearing affected paths requires an attributable decision under existing reuse
  and acceptance rules; snapshot/checksum edits cannot transfer evidence.
- Impact traversal crosses workstream boundaries through declared dependencies;
  ownership remains scoped to the workstream and never limits impact discovery.
- Retired items are excluded from active views and remain historically accessible;
  shared dependents require assessment before retirement.
- Immutable records remain reachable for historical validation and export.
- Records never include their own digest in the bytes being hashed. Reference
  cycles, missing targets, duplicate conflicting IDs, and unsafe paths are rejected.
- Registration and record publication are atomic for readers. Interrupted writes
  do not publish dangling references; retries cannot mutate published identities.
- Required artifacts and dependencies must exist before a success report is issued.

## Failure cases

Reject ambiguous numeric/parent/version context, missing or rebound revision
entries, ambiguous raw-hash prefixes, conflicting registrations, candidate-substituted
manifests, changed logs, stale accepted obligations, unavailable Git objects,
malformed versions, incomplete imports, cycles, unsafe paths, and interrupted
publication. Return a stable reason and scoped reference. Failed resolution cannot
be treated as successful verification, approval, or completion.

## Acceptance criteria

Canonical Given/When/Then criteria are in `specs/current/shorter-hashes.json`.
They define specification obligations; coordinator test-plan acceptance is a
separate pin. All require executable
evidence; no review-only exemptions are declared.

| Criterion | Observable requirement | Planned evidence types |
| --- | --- | --- |
| SH-01 | Numeric item/revision references are the workflow default; explicit raw Git/hash inspection preserves collision and exact-ID rules. | unit, integration |
| SH-02 | Stable parent-qualified numeric spec/part, plan/item, task, and test IDs with immutable numeric revisions. | unit, integration |
| SH-03 | A separate integrity file maps numeric item revisions to shared exact Git sources and full required digests. | unit, integration |
| SH-04 | Candidate-only substitutions cannot alter coordinator acceptance authority. | integration, e2e |
| SH-05 | Immutable contracts and later evidence have separate lifetimes and retained history. | integration |
| SH-06 | Byte and canonical-JSON digest semantics retain their invalidation rules. | unit, integration |
| SH-07 | Numeric revisions resolve exact snapshot/path/items; blob checks and item comparison avoid revisions for unrelated edits. | integration |
| SH-08 | Scoped allocation, concurrent conflicts, malformed refs, and cycles fail safely. | unit, integration |
| SH-09 | Compact JSON preserves values, defaults, and deterministic validation. | unit, integration |
| SH-10 | Legacy reads, explicit migration, and export preserve provenance and authority. | integration, e2e |
| SH-11 | Selective agent projections resolve evidence without loading whole catalogs. | integration, e2e |
| SH-12 | Fixed representative workloads demonstrate lower total tokens and JSON bytes. | integration |
| SH-13 | Interrupted publication and retries preserve immutable references and clean source. | integration |
| SH-14 | Complete workflow still rejects stale or modified evidence and accepts valid evidence. | e2e |
| SH-15 | Every dependency pins a numeric item revision and exact Git source; binding changes publish revisions and preserve attributable history. | unit, integration, e2e |
| SH-16 | Partial invalidation distinguishes direct reassessment from potential downstream impact and supports reviewed propagation stopping. | unit, integration, e2e |
| SH-17 | Deletion triggers impact assessment; retirement preserves history and protects shared active dependents. | unit, integration, e2e |
| SH-18 | Project-wide impact traversal follows qualified dependencies across owners, preserves workstream authority, and reports incomplete discovery. | unit, integration, e2e |

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

## Open questions and closure boundary

No behavioral question is intentionally delegated to Plan. Item equality,
propagation stopping, and complete discovery have normative rules and required
decision examples above. An implementation unable to satisfy those outcomes must
return to Spec Change rather than choose a different meaning.

Plan chooses encoding, module layout, commands, locking/capture mechanisms,
supported profile implementations, and frozen benchmark tooling/corpus. Each
choice must preserve the specified outcomes; the independent challenge must cite
why each remaining deferral is bounded. The benchmark's feasibility remains an
implementation acceptance risk: failing strict aggregate savings requires a design
revision, never a claim that a sealed specification proves savings.

The exact independent challenge and closure receipt live under
`work/shorter-hashes/`. A spec seal records the committed source/digests and zero
open behavioral blockers; it is not complete-intent approval, an accepted test-plan
pin, implementation evidence, or workstream acceptance. The authorized stop is a
consolidated plan and clear tasks.

## Source intent

`work/shorter-hashes/intent.md`, reconciled with this amendment. Prior intent:
`6bbcde91ed31276d56d3b74df94d2e31e6d9fc96:work/shorter-hashes/intent.md`.
The numeric correction is recorded in `work/shorter-hashes/spec-change.md`.
The revision-7 closure in `work/shorter-hashes/spec-change-r7.md` records the user's
“continue till spec sealed” and extended planning scope. Neither substitutes for
complete-intent confirmation before implementation.
The prior independent design challenge supplied the authority, lifetime,
digest-semantics, availability, and measurement counterexamples addressed here.

## E2E

Applicability: `applies`

Journeys: create and accept a contract through the coordinator; register numeric
spec/part, plan/item, task, and test references with parent context and revisions;
execute and review runs; query compact status and evidence; verify
completion; reload old contract revisions; and export/reload an evidence bundle.
Repeat with a candidate-only substituted manifest, modified log, stale contract,
same local IDs under different parents or works, conflicting revision publication,
a changed/missing integrity entry, and missing Git object. Resolve an older numeric
revision after publishing a newer one; verify that unrelated edits do not advance
independent item revisions and changed dependency bindings do advance their owner.
Exercise spec-to-plan, plan-to-task, task-to-test, and other actual dependency
edges; change a root, an intermediate task, and one input of a multiple-input
artifact. Change one item in a file containing unrelated items; mark only direct
dependents for reassessment and identify potential downstream impact. Exercise
both reviewed propagation stopping and actual downstream revision. Delete a
requirement with exclusive and shared dependents; verify explicit retirement,
active-view filtering, and historical retrieval. Unresolved affected paths refuse
completion; unrelated branches remain eligible. Historical runs keep their bindings.
Include a shared policy consumed in multiple workstreams, a dependency chain
crossing workstream branches, duplicate local IDs with distinct owners, and an
unavailable owner declaration. Confirm project-wide discovery reaches actual
dependents outside the checkout, preserves each owner's authority, and reports
incomplete traversal when dependency sources cannot be loaded.

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
