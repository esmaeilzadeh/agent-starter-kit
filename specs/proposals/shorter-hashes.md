# Specification: Compact workflow references and integrity evidence

## Status

PROPOSED — revision 5. The user requested this specification; intent confirmation,
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

For committed artifacts, Git supplies immutable history and content identity.
Store each full source commit once in shared snapshot context; dependencies use
short snapshot references, repository-relative paths, and stable artifact item IDs.
Separate generated file or item checksums are unnecessary for these bindings.
Evidence outside Git retains full authoritative checksums, stored once per
workstream and digest semantics where safely reusable. Cross-workstream references
name the owner explicitly. Retain required Git objects for historical validation.

For example, within a declared workstream, a report could contain:

```json
{"contract":3,"task":7,"run":4,"log":12,"status":"pass"}
```

This is an illustrative projection. The Plan defines exact versioned schemas,
storage paths, and resolver interfaces. Every reference must identify its work,
record type, and immutable target through explicit or inherited context. A bare
number without sufficient context is invalid.

### Item dependencies and Git history

The dependency graph's nodes are artifact items, such as a requirement, plan item,
task, or test definition. Each edge binds the source snapshot, file path, and stable
item ID reviewed by the dependent item. This applies to every actual dependency
including shared/global constraints, source, policy, and runner inputs. Ownership
labels and lookup links alone do not establish a dependency. The Plan inventories
these edges and defines deterministic item extraction and comparison per format.

Git owns item history; separate per-item revision counters and checksum histories
are not required. Stable IDs survive section movement and are never recycled.
File moves need an explicit path mapping; missing or duplicate IDs cannot be
resolved by guessing. Compare against an explicitly selected candidate snapshot,
not whichever commit HEAD happens to name during validation.

A different repository commit or file's last modifying commit is not an
invalidation decision. Compare the file's Git blob IDs at the recorded and
candidate snapshots as a fast unchanged-content check. If different, compare the
referenced item's meaningful content and declared dependency bindings using the
format's deterministic equivalence rules. Unrelated section edits and permitted
formatting/reordering leave that item valid. Intent approval and other explicitly
byte-bound checks retain their existing exact-byte semantics.

### Project-wide graph and workstream ownership

Dependencies form one logical project-wide graph. Each workstream owns and records
its artifacts and outgoing dependency declarations. An edge to another workstream
uses an explicit qualified identity: owner workstream, source snapshot, path, and
stable artifact item ID. Local shorthand is permitted only inside an explicitly
declared owner context. Identical local IDs in different owners remain distinct.
Shared project artifacts have a declared canonical owner and identity; consumers
reference that identity rather than creating unrelated local copies of it.

Impact analysis discovers committed dependency declarations across workstreams,
including consumers whose source is on another workstream branch rather than in
the current checkout. It resolves exact pinned sources and traverses actual edges
across ownership boundaries until the affected closure is accounted for. The
Plan specifies authoritative discovery and snapshot selection; a derived project
index must remain rebuildable and cannot confer acceptance authority.

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
old/new snapshots with the attribution, review, and coordinator authority required
for that artifact type:

- Retain: the dependent item still satisfies the changed input. Record a new
  revalidation binding; preserve its original review and content in Git history.
- Revise: change the dependent content or obligations, commit it, and reassess
  its consumers against the changed item.
- Retire: the item no longer serves an active obligation; retain historical access
  and remove it from the default active workflow.

Propagation can stop when a reviewed decision establishes that the dependent's
consumer-relevant content, obligations, and dependency contract are unchanged and
existing evidence reuse rules permit it. Record that decision before clearing
potentially affected descendants. If those conditions fail, continue reassessment.
A pointer/checksum update, unchanged payload alone, or a changed upstream commit
alone cannot establish validity or transfer approval. No historical record is
silently rebound.

For example, `S1 -> P1 -> T1 -> X1` and `S2 -> P4 -> T4 -> X4` are independent
chains. Editing only S1 marks P1 for reassessment and T1/X1 as potentially affected;
P4/T4/X4 remain eligible even if S1 and S2 share one file. If reviewed P1 still
satisfies the new S1 without consumer-relevant changes, eligible T1/X1 evidence
can be retained with the recorded decision. If P1 changes, reassess T1 and then
X1 as their actual inputs change. A global constraint affects every linked item.

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

Pinned Git snapshots resolve exact paths and item IDs. Missing objects, unsafe
paths, ambiguous item IDs, or absent snapshot records fail explicitly without
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
- Impact queries discover dependencies project-wide and return owner-qualified
  affected items, dependency paths, and any unresolved scope or targets.

## Constraints and invariants

- Human approval binds the exact intent; independent decisions retain attribution.
- Accepted obligations, candidate/source lineage, test assertions, logs, and runner
  identities remain verifiable. Short references alone grant no authority.
- Dependency binding and impact analysis operate on stable artifact items in Git
  snapshots. Changed direct inputs require reassessment; downstream impact is
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
| SH-03 | Shared Git snapshots replace redundant committed-artifact checksums; external evidence retains full digests. | unit, integration |
| SH-04 | Candidate-only substitutions cannot alter coordinator acceptance authority. | integration, e2e |
| SH-05 | Immutable contracts and later evidence have separate lifetimes and retained history. | integration |
| SH-06 | Byte and canonical-JSON digest semantics retain their invalidation rules. | unit, integration |
| SH-07 | Snapshot/path/item resolution and blob fast checks preserve exact content and item-level comparison. | integration |
| SH-08 | Scoped allocation, concurrent conflicts, malformed refs, and cycles fail safely. | unit, integration |
| SH-09 | Compact JSON preserves values, defaults, and deterministic validation. | unit, integration |
| SH-10 | Legacy reads, explicit migration, and export preserve provenance and authority. | integration, e2e |
| SH-11 | Selective agent projections resolve evidence without loading whole catalogs. | integration, e2e |
| SH-12 | Fixed representative workloads demonstrate lower total tokens and JSON bytes. | integration |
| SH-13 | Interrupted publication and retries preserve immutable references and clean source. | integration |
| SH-14 | Complete workflow still rejects stale or modified evidence and accepts valid evidence. | e2e |
| SH-15 | Every actual dependency binds stable items at exact Git snapshots and retains attributable revalidation history. | unit, integration, e2e |
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

## Open questions

Intent confirmation and formal independent Spec Challenge are pending. Exact
schemas, catalog paths, tokenizer, corpus revisions, and command flags are Plan
deliverables constrained by this spec; they are not claims of completed work.
Revisions 4 and 5 incorporate the user's Git-based item comparison, partial
invalidation, retirement, and project-wide traversal with workstream ownership.
Reconcile this proposed design with the source intent
before implementation approval; this edit records no such approval.
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
