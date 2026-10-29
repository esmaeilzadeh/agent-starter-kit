# Consolidated implementation plan

## Specification and authorization

Requirements baseline: **sealed specification revision 7**, canonical
`specs/current/shorter-hashes.json`, with normative Markdown at
`specs/proposals/shorter-hashes.md`. The exact source/digests and independent
closure are in `spec-seal.md` and `spec-challenge.md`. This plan derives from
that one spec; it does not reopen its equality, stop, discovery, authority, or
savings outcomes. Plan seal requires independent approval of this document,
`test-plan.json`, `inner-loop/tasks.yaml`, and the frozen benchmark/inventory.

**Authorized endpoint: verified and accepted workstream.** On 2026-10-21, the
user approved the Task 5 classification proposal and directed completion through
acceptance (“go till and all accepted”), superseding the earlier plan-only stop.
The implementation must use this sealed specification, the independently
reviewed updated test plan, and the TaskGraph evidence rules below. The exact
endpoint direction is recorded in `continuation-authorization.md`; it changes
execution scope while preserving the previously approved intent bytes and their
confirmation. The continuation reconfirmation bug and process correction are
recorded in `continuation-reconfirmation.md`.

## Concrete interfaces and storage

Use one shared Python package, `.agents/ask/workflow_refs/`, shipped with the
portable protocol. Its public boundary exposes `register_revision`,
`resolve_version`, `compare_items`, `capture_project`, `assess_impact`,
`record_decision`, `project`, `migrate`, and `export_bundle`/`import_bundle`.
Existing consumers receive normalized legacy-shaped values at their I/O
boundaries; validator/completion policy remains the authority for acceptance.

| Concern | Fixed planning decision |
| --- | --- |
| Identity | Canonical text is `<work>/spec/<s>[/part/<p>]@<r>`, `<work>/spec/<s>/plan/<p>[/item/<i>]@<r>`, `<work>/spec/<s>/plan/<p>/task/<t>[/test/<x>]@<r>`. All numeric components are positive, unpadded decimal. Test ownership nests under task; plan/task ownership chooses one declared spec/plan while all other inputs remain edges. |
| Auxiliary identities | Contracts, policies, snapshots, reviews and runs use `<owner>/<kind>/<id>@<revision>`; child logs use `<owner>/run/<run>/log/<log>@<revision>`. Each type declares its ownership context. `record-run` uses the explicitly registered shared owner `repository-runs`, separate `results/references/integrity.json`, and `refs/ask/references/repository-runs`; conflicting owner registration refuses rather than merging histories. Full provenance is resolved on demand. |
| Inherited context | JSON records may use `{id: 2, revision: 1}` only inside explicit owner/type/parent context. Full forms cross owner boundaries. A task scope uses the local string ID from this graph; the container supplies work and plan 1. Existing SH-* and historical IDs retain stable mappings. |
| Revision allocation | Allocate a number greater than every published revision of the same logical identity, with serialized CAS. Reserve/abort may leave gaps; published targets never change. Explicit reparent/move maps preserve old identities and history. |
| Integrity file | `work/<owner>/references/integrity.json`, `ask-reference-catalog/v1`, stores immutable qualified item/revision entries, exact source commit/path/item/profile and full required digests with algorithm/semantics. Full repeated snapshot identities are shared once. |
| Authority | Catalog publication is coordinator-registered under `refs/ask/references/<owner>` and validated against its anchored immutable entries. It cannot accept test obligations or independent review. `refs/ask/accepted-tests/<owner>` remains decisive. The minimum full digests in this trust bootstrap are a justified full-value exception; normal reports never load that authority data by default. |
| Compact formats | New persisted records use `ask-workflow-envelope/v1`: explicit payload schema/context and typed numeric references. Normalize to the existing versioned contract values before existing validation. Bare/unsupported envelopes refuse. Hash replacement uses typed schema fields, never regex over prose or logs. |
| Publication/capture | One persistent repository lock in the Git common directory, `ask-locks/references.lock`, serializes cooperating catalog publication and inventory capture. Atomic file replacement and authority CAS use a recoverable pending journal. Generation changes include additions/removals/ABA ref changes. Readers never accept partial references. `start-work` owner creation and inner-loop integration join this protocol. External unsupported ref writers cause incomplete capture unless consistency is established. |
| Project scope | Capture exact local `agent/<work>` coordinator refs, selected `develop` integration and `main`/default archive source, and explicit shared owners. Exclude task refs. Record immutable vector/generation; indices are derived. Old results remain historical; selected new-context use rechecks scope. |
| Profiles | `structured-item/1` preserves all JSON values/types/arrays and ignores only JSON key order/serialization whitespace. `prose-item/1` uses exact extracted UTF-8 bytes. Stable IDs delimit items; shared/global obligations are separate actual input edges. Unknown fields participate. No semantic text guessing. |
| Review decisions | Immutable decision records name old/new revisions, consumer pins, profile IDs, every affected input path, exact captured context, evidence, and applicable owner reviewer/coordinator attribution. Stops follow the spec decision table, with no automatic edge/run rebinding. |
| Public commands | `./ask refs show <qualified-ref> [--integrity]`, `impact --source <capture> --candidate <capture>`, `decide --evidence <file> --recorded-by <actor>`, `migrate <work>`, `export <work> --out <bundle>`, and `import <bundle>`. Default show/status returns selected numeric projections; exact integrity is on demand. Stable errors include malformed/ambiguous/missing/version_unsupported/comparison_incomplete/discovery_incomplete/conflict/authority_missing. |
| Import/export | Bundle original records, immutable catalogs/decisions, required Git objects and authority provenance. Source-only transfer requires reviewed coordinator re-registration before new verified completion. No history rewriting or fabricated versions/approval/Red-Green. |

The proposed formats are future runtime deliverables. This planning commit uses
the existing `ask-spec/v1`, `ask-test-plan/v1`, and task graph contracts so the
current validators can independently accept the implementation obligations.

## Producer/consumer consolidation

The complete planned surface and exception mapping is `surface-inventory.md`.
Normalize at actual read/write boundaries instead of sprinkling display-only
shortening into callers. Existing canonical JSON and exact-byte helpers continue
to verify resolved full values. In particular, a new envelope/catalog must not
permit candidate values to establish their own trust anchor.

## Work breakdown

One committing writer on `agent/shorter-hashes`; execute tasks in the explicit
order below. The full linear dependency chain intentionally serializes shared
file ownership and limits integration uncertainty. Each row is one reviewable
outcome; its tests belong to exactly that task. No task is a deferred decision.

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | Reproduce the frozen baseline and comparison fixtures | none | `.agents/ask/workflow_refs/benchmark.py`; `_ask/tests/test_workflow_refs_baseline.py` | 1/1, 1/2 | Executed assertion Red → Green, task-scoped mapped cases, attributable independent candidate review, applicable regression checks, explicit Refactor outcome and FF integration receipt. |
| 2 | Publish and resolve numeric identities, immutable integrity entries, and compact envelopes | 1 | `.agents/ask/workflow_refs/__init__.py`; `.agents/ask/workflow_refs/identity.py`; `.agents/ask/workflow_refs/store.py`; `.agents/ask/workflow_refs/codec.py`; `_ask/tests/test_workflow_refs_identity.py`; `_ask/tests/test_workflow_refs_store.py`; `_ask/tests/test_workflow_refs_codec.py` | 2/1, 2/2, 2/3, 2/4, 2/5, 2/6, 2/7, 2/8, 2/9 | Executed assertion Red → Green, task-scoped mapped cases, attributable independent candidate review, applicable regression checks, explicit Refactor outcome and FF integration receipt. |
| 3 | Compare complete artifact items and declare exact dependencies | 2 | `.agents/ask/workflow_refs/compare.py`; `.agents/ask/workflow_refs/profiles.py`; `_ask/tests/test_workflow_refs_compare.py` | 3/1, 3/2, 3/3 | Executed assertion Red → Green, task-scoped mapped cases, attributable independent candidate review, applicable regression checks, explicit Refactor outcome and FF integration receipt. |
| 4 | Capture coherent project graphs and apply reviewed impact decisions | 3 | `.agents/ask/workflow_refs/project.py`; `.agents/ask/workflow_refs/impact.py`; `_ask/tests/test_workflow_refs_project.py`; `_ask/tests/test_workflow_refs_impact.py` | 4/1, 4/2, 4/3, 4/4, 4/5, 4/6, 4/7 | Executed assertion Red → Green, task-scoped mapped cases, attributable independent candidate review, applicable regression checks, explicit Refactor outcome and FF integration receipt. |
| 5 | Integrate traceability and exact approval/authority checks | 4 | `.agents/ask/verification/traceability/**`; `.agents/ask/verification/run.py`; `_ask/scripts/intent-confirmation.py`; `_ask/tests/test_workflow_refs_traceability.py` | 5/1, 5/2, 5/3 | Executed assertion Red → Green, task-scoped mapped cases, attributable independent candidate review, applicable regression checks, explicit Refactor outcome and FF integration receipt. |
| 6 | Integrate numeric references into the inner task loop | 5 | `_ask/scripts/inner_loop/**`; `_ask/tests/test_workflow_refs_inner_loop.py`; `.agents/ask/verification/traceability/evidence.py` | 6/1, 6/2 | Executed assertion Red → Green, task-scoped mapped cases, attributable independent candidate review, applicable regression checks, explicit Refactor outcome and FF integration receipt. |
| 7 | Integrate engineering snapshots and selective agent context | 6 | `_ask/scripts/engineering_model/**`; `_ask/tests/test_workflow_refs_engineering.py` | 7/1, 7/2 | Executed assertion Red → Green, task-scoped mapped cases, attributable independent candidate review, applicable regression checks, explicit Refactor outcome and FF integration receipt. |
| 8 | Expose refs commands, compact reports, and explicit migration/export | 7 | `.agents/ask/workflow_refs/__main__.py`; `.agents/ask/workflow_refs/cli.py`; `.agents/ask/workflow_refs/projection.py`; `.agents/ask/workflow_refs/migration.py`; `_ask/scripts/references.sh`; `_ask/scripts/status.sh`; `_ask/scripts/record-result.sh`; `_ask/scripts/ask-complete.sh`; `ask`; `_ask/docs/workflow-references.md`; `README.md`; `_ask/tests/test_workflow_refs_cli.py`; `_ask/tests/test_workflow_refs_migration.py`; `_ask/scripts/record-run.sh`; `_ask/scripts/start-work.sh`; `_ask/tests/test-record-run-writes-manifest.sh`; `_ask/tests/test-start-work-*.sh` | 8/1, 8/2, 8/3, 8/4, 8/5 | Executed assertion Red → Green, task-scoped mapped cases, attributable independent candidate review, applicable regression checks, explicit Refactor outcome and FF integration receipt. |
| 9 | Prove complete multi-owner workflows and failure behavior, including transition-wide decision coverage | 8 | `.agents/ask/workflow_refs/impact.py`; `_ask/tests/workflow_refs_fixture.py`; `_ask/tests/test_workflow_refs_e2e.py`; `_ask/tests/test-workflow-references.sh` | 9/1, 9/2, 9/3, 9/4, 9/5 | Executed assertion Red → Green, task-scoped mapped cases, attributable independent candidate review, applicable regression checks, explicit Refactor outcome and FF integration receipt. |
| 10 | Demonstrate aggregate savings and publish the acceptance report | 9 | `.agents/ask/workflow_refs/benchmark.py`; `_ask/tests/test_workflow_refs_savings.py`; `work/shorter-hashes/benchmark/results/**`; `_ask/docs/workflow-references.md` | 10/1 | Executed assertion Red → Green, task-scoped mapped cases, attributable independent candidate review, applicable regression checks, explicit Refactor outcome and FF integration receipt. |

### Task boundaries and exit conditions

**Task 1.** Read the frozen Git corpus and exact tokenizer; produce reproducible raw question/context/lookup transcripts and unique-file metadata totals. Verify every file hash and refuse absent tooling/data. This task establishes measurement, not claimed savings.

**Task 2.** Implement exact identity/context grammar, numeric allocation, separate trusted catalog, append-only revisions, persistent lock/CAS, atomic publication/recovery, canonical/byte semantics, legacy normalization and compact JSON. Keep accepted-tests authority separate.

**Task 3.** Implement the frozen format profiles, extraction and complete input sets; preserve unknown fields and exact source paths, detect external binding changes despite equal blobs, and return unchanged/changed/incomplete without source fallback.

**Task 4.** Capture authoritative ref inventory/vector under cooperating publication lock and generation checks; traverse edges across owners, implement normative retain/revise/retire and incomplete states, and preserve old pins/history.

**Task 5.** Normalize envelopes at traceability I/O boundaries, deduplicate persisted digests through trusted catalogs, register dependencies/reviews/runs and keep exact-byte intent approval, accepted-tests pins, exact candidate/runner/log checks and TDD history. Cases 5/1 and 5/2 are regressions and need current Green evidence; 5/3 is new and needs behavior-assertion Red plus Green. No old execution is relabeled.

**Task 6.** Use compact state/evidence encoding and qualified task/test identities while preserving state generations, CAS, one writer, exact candidates, interruption recovery, existing runner filtering and fast-forward-only integration. Task 6 also owns the narrowly scoped runtime classification in `.agents/ask/verification/traceability/evidence.py`: exclude only this work owner's generated `references/integrity.json` and `references/integrity.json.pending` from source-dirt checks, retaining trusted-catalog validation and every other source check. This prerequisite source is already bound to both mapped cases; Task 5 is integrated and execution remains serialized.

**Task 7.** Normalize compact input snapshots and exact source captures, preserve admission and canonical validation, project selected task/test/review context with inherited numeric IDs, and keep historical UI/context evidence readable. No new UI visual design.

**Task 8.** Wire public refs show/impact/decide/migrate/export/import interfaces, qualify errors, count lookup responses, export original records/objects/authority provenance, refuse incomplete verified imports and preserve legacy status/result behavior. Convert new record-run outer JSON/registry/report provenance into numeric run references with separate full integrity data while retaining metrics/notes and dirty/missing-SHA/HEAD/config refusals. Register repository-runs as an explicit shared owner; preserve original history. Make start-work owner-ref creation participate in the same publication lock/generation protocol while preserving its develop/clean/no-explore-map behavior. Adapt the relevant existing shell regression expectations to inspect resolved provenance. Inspect remaining raw digest sites against the surface inventory.

**Task 9.** Exercise actual CLI/coordinator/worktree workflows for accepted contracts, executed tests, registered review, legacy history, retain/revise/retire, incomplete cross-owner discovery, migration/export, tampering and crash recovery; add the new suite to existing static shell-test discovery. The existing 9/3 case also owns a focused correction in `.agents/ask/workflow_refs/impact.py`: validate a revise decision against the declared inputs of both its registered old and replacement dependent revisions. Preserve incomplete status when any required transition input remains unresolved. This path is shared with completed Task 4 and is changed only in serialized Task 9 after Task 4 integration; the case already binds this source. No spec, case, authority, or acceptance change is proposed.

**Task 10.** Run identical frozen baseline/candidate journeys using the pinned tokenizer, retain full input/lookup transcripts, count every generated catalog/profile/index and metadata output, assert both strict aggregate savings and full evidence equivalence, report individual regressions/full-value exceptions. Any miss returns to design/spec review, not a lowered threshold.

## Test contract and execution rules

`test-plan.json` defines **39 explicit cases**, **14 supported unittest runners**,
all 18 criteria and every required evidence type, with Given/When/Then and
per-criterion expected assertions. The exact case/test/source mapping lives there;
the work table and TaskGraph contain the identical ten local task IDs. Test IDs
are `<task>/<test>` inside this work/plan context. Every case binds the concrete
production modules available by its task (including prerequisite modules);
measurement cases additionally bind the frozen manifest and requirements. E2E
cases bind their shared fixture. No future task module is required by an early
task's source identity. No review-only task or
criterion exemption is declared. All task scopes are nonempty.

Every test is a declared obligation. For cases classified `new`, add the mapped
test plus only the minimal callable capability scaffold needed to obtain an
observable unsupported/result value; execute assertion Red on the missing
behavior, not import/setup failure. Cases classified `regression` need current
Green evidence and must not be relabeled as new. Then complete local Refactor
and obtain independent review bound to the exact candidate/source/assertion
continuity. Use the existing coordinator
traceability runner and its task filtering; an opaque shell exit supplies no case
evidence. A production defect found in a later task requires an explicit reviewed
scope correction/amendment for the responsible task before writing outside owned
paths; do not silently broaden a test-only task.

Existing `_ask/tests/test_traceability*.py`, inner-loop shell/reliability suites,
engineering model/context/workbench suites, status tests and intent-confirmation
checks remain mandatory regressions appropriate to their touched modules. New
mapped cases exercise the changed behavior; unchanged tests need no fabricated
Red. Task 9 adds `test-workflow-references.sh` to the already mandatory shell-test
glob so the new suite is also run by aggregate `./ask verify`.

## Frozen measurement contract

`benchmark/baseline.json` freezes exact real corpus paths, full source IDs/file
hashes, all three questions, projection/accounting rules and workload version.
Baseline source: `9a3d25d035baafc23508f242020d46fae7ff5b14`. Use `tiktoken==0.12.0`,
`cl100k_base`, `encode_ordinary`, UTF-8; package version verified against
[the pinned PyPI release](https://pypi.org/project/tiktoken/0.12.0/). The package
and encoding must be available and checked before Task 1 measurements; no
estimated token counts or substitute tokenizer are allowed. This planning run
freezes the experiment and corpus; it claims no measured tokens or savings.

Baseline projections select every mapped case/obligation/runner needed for the
frozen question, not arbitrary unrelated tasks. Necessary verification details
may be loaded by tools without adding unrelated file text to the agent input.
Candidate transcripts must answer the exact same question, preserve authority
and outcome, and include every required context/catalog lookup response and
selected log byte. Count complete unique generated JSON metadata including
new integrity catalogs, profiles, decisions, contexts and indices. Each replay
retains the identical immutable legacy-input archive at separate input paths;
baseline writes legacy-shaped outputs and candidate writes new-format outputs.
Include the archive's equal overhead on both sides and count every actual output
path once; no deletion of originals may claim savings. Report YAML, source prose
and logs separately; they cannot offset a JSON-byte regression.

Task 10 accepts only strict aggregate reduction in both agent-input tokens and
generated metadata bytes, with per-journey totals, individual regressions, exact
source/tool versions and full-value exceptions. A larger graph/catalog does not
earn an exception. A miss requires reviewed redesign before implementation can
be accepted; this plan does not pre-claim feasibility.

## Verification approach and seal

Before sealing: validate all graph dependencies/path overlap, spec/test coverage,
case uniqueness and exact one-task assignment; verify the frozen corpus hashes
against its source; independently review this exact plan/spec/graph/test mapping
and baseline/inventory; commit and register the approved contracts using
`./ask traceability accept-plan`. The independent decision must bind canonical
spec/test-plan/TaskGraph digests plus exact plan/inventory/benchmark file hashes.
Changing any bound artifact makes its seal stale and requires renewed review.

During later execution: follow `.agents/ask/task-loop.md`, capture real Red/Green,
current independent review and integration per task. After all tasks, run full
`./ask verify` and record actual completion evidence before Accept. A sealed plan
contains future tests and cannot satisfy that execution gate.

## Risks and escalation points

- Unknown item formats/global inputs must report incomplete instead of claiming
  independence; extending supported behavior beyond these rules needs Spec Change.
- Any weakening of coordinator acceptance, intent bytes, candidate/runner/log
  binding, old-entry immutability or one-writer/FF integration is a blocker.
- Concurrent capture must detect additions/removals/ABA generation changes; a
  mechanism unable to do so cannot assert project-wide completeness.
- Any new producer/dependency family found during implementation is inventoried
  and reviewed into the contract before work starts, rather than omitted.
- New public semantics, changed comparison exclusions, unresolved ownership,
  authority conflicts, or failed savings require explicit escalation/amendment.

## Out of scope for this plan

Production deployment, remote synchronization services, distributed transactions,
new authentication, bulk historical rewriting, visual/UI redesign, unrelated
refactors, or implementation during this planning run. No optional command flag,
storage algorithm or future reviewer may alter the sealed behavioral rules.

## E2E

Applicability: `applies`. Task 9 runs actual ask/coordinator interfaces in
temporary Git repositories and worktrees with retained local authority refs,
real legacy inputs, multiple owner branches, numeric collisions, shared/global
constraints, exact profiles, real executed cases/logs, interrupted publication
and unavailable objects/owners. It covers valid/invalid completion, selective
resume, reviewed retain/revise/retire, deletion/shared tests, source-only export
and reviewed authority registration, and coherent discovery at capture/use.
Cases assert externally observed eligibility, revisions, status/error scope and
actual evidence binding, not only in-memory helpers or JSON success fields.

Reset removes fixture-owned worktrees/runtime files and releases all fixture
locks/processes. No network/production datastore is required during workflow
tests; provision the frozen tokenizer/encoding beforehand. Real work stays
committed on the original workstream branch; no task writer starts in this run.
