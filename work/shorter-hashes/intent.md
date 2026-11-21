# Intent: Reduce workflow token cost with compact references and exact dependencies

## What

Reduce tokens in workflow JSON, agent prompts, CLI output, and reports; improve
readability second. Use parent-qualified numeric IDs for specs and their parts,
plans and their items, tasks, and tests, with numeric revisions identifying exact
versions. Compact generated JSON and eliminate repeated metadata. Store full
checksums and exact Git identities in a separate integrity file; ordinary workflow
records reference numeric item revisions. Keep all integrity data verification needs.

Bind each actual dependency to its exact numeric source item revision, resolved
through the separate integrity file to a source snapshot, path, and stable item ID.
Git preserves source history; numeric revisions identify immutable item versions.
Compare meaningful item content and bindings so an unrelated edit in the same
file does not invalidate an independent requirement or plan.
Preserve existing exact-byte checks, including intent approval and bound logs.

Track dependencies project-wide with ownership scoped to each workstream.
Qualified cross-workstream edges carry impact across branches; shared policies
reach all actual consumers. Direct dependents need reassessment; downstream items
are potentially affected and cannot authorize completion until affected paths are
resolved. Attributable retain/revise/retire decisions follow existing authority
and evidence-reuse rules. Unrelated items remain valid. Deleted requirements
trigger assessment; retirement preserves history and shared active dependents.

## Why

Repeated hashes and verbose JSON consume context. Shared snapshot identities and
selective projections reduce repeated data while exact dependency bindings prevent
stale plans, tasks, tests, reviews, or execution records from appearing current.
Savings must include necessary lookups, shared metadata, and complete agent inputs.

## Non-goals

- Change hash algorithms, truncate required authoritative checksums, or weaken
  coordinator acceptance, independent review, or execution evidence requirements.
- Rewrite unrelated JSON/prose or invent missing historical approval/execution.
- Rebind old evidence through checksum, alias, or pointer edits.
- Give project-wide traversal authority to edit another workstream's records.

## Known assumptions

- Scope is workflow JSON and every eligible hash surface, with justified full-value
  exceptions. Legacy records remain readable; historical records are not bulk
  rewritten. Explicit migration/export preserves provenance and dependencies.
- Ordinary workflow references use unpadded positive numeric IDs and numeric
  revisions, qualified by work, type, and declared related parent identities.
  Explicit context may be inherited; cross-workstream ownership is explicit.
  Legacy mappings stay stable; published item/revision targets remain immutable.
- Parent prefixes identify ownership. Multiple upstream dependencies remain
  explicit edges; they do not duplicate an item under every source. Ancestor
  version changes alone do not rename descendants. Exact spelling is Plan work;
  the user's reference examples illustrate intention rather than a fixed grammar.
- Full required checksums and exact Git IDs live in a separate integrity file.
  Numeric item/revision references resolve exact snapshot/path/item bindings.
  Explicit raw Git/hash inspection preserves ambiguity rejection and full-ID
  resolution for exact operations. Short references never verify integrity.
- Meaningful item-content or dependency-binding changes publish fresh revisions;
  unrelated edits and permitted formatting changes leave independent revisions
  unchanged. Ownership or a lookup link alone does not establish a dependency.
  Comparison includes every obligation-bearing field and exact input binding;
  unknown/unavailable comparison context cannot prove equivalence. Propagation
  stops require reviewed validity for named retained versions in a coherent
  recorded owner/snapshot context, preserving immutable pins and executions.
- Project discovery includes committed workstream sources outside the checkout.
  Missing sources or declarations produce incomplete analysis, never an empty
  graph or a claim that all affected paths are clear.
- Accepted contracts and later run records have separate immutable lifetimes.
  Reassessment cannot relabel historical executions; reuse must satisfy existing
  rules. Propagation stops only with a valid recorded decision.
- Before implementation, Plan freezes baseline workloads, source identities, and
  a tokenizer/version. Acceptance requires lower aggregate agent-input tokens and
  metadata JSON bytes; report individual regressions and count lookup overhead.
- Token savings take priority over readability while preserving required evidence.

## Open questions

The numeric correction was approved with “yes apply it”; see `spec-change.md`.
The user subsequently authorized specification closure and consolidated planning;
`spec-change-r7.md` records the scope-preserving behavioral clarifications.
Complete-intent confirmation before implementation remains pending. Exact
encoding, integrity-file path, extraction/capture mechanisms, corpus, and command
flags are Plan choices within the spec's normative comparison, stop, and discovery
rules. This run stops after a sealed specification and clear plan/tasks.

## Human decisions

- Primary goal: reduce token consumption; secondary goal: readability.
- Preserve exact dependency provenance for every existing relationship, not only
  spec-to-plan; independent items must remain unaffected.
- Use project-wide dependency impact with workstream-scoped ownership.
- Preserve revision 4 refinements and require cross-workstream traversal explicitly.
- Apply parent-qualified numeric IDs across specs/parts, plans/items, tasks, and
  tests, plus numeric revisions and separately stored checksums. Approval response:
  “yes apply it”. Preserve the existing exact-source and dependency-impact rules.

## Engineering subject

- Subject: `shorter-hashes/readable-work-identifiers`.
- Source: explicit user request and subsequent dependency refinements; original
  Explore snapshot `5e9522e9842b540dcc1493569a062c66d382e4e0803c2d12889b65d9a70a5a2f`.
- Contribution: lower workflow token cost with parent-qualified numeric item and
  revision references and separate integrity data, preserving exact dependencies
  and acceptance authority.
- Execution owner: none assigned; implementation has not started.

## E2E

Applicability: `applies`

Journeys: query compact task/test/status/evidence projections; resolve exact inputs;
change one requirement beside an independent item; traverse a shared-policy change
across workstreams; reassess through retain/revise/retire decisions; verify valid
and invalid completion; reload historical records and exported evidence.

Observable outcomes: numeric parent/item/revision references resolve separately
stored integrity data; lower measured aggregate tokens and metadata bytes; exact
source/approval/execution binding; impact follows actual item edges across owners;
unrelated items stay eligible; unresolved, missing, ambiguous, or altered evidence
cannot authorize completion. Original evidence remains historically retrievable.

Environment/data: temporary Git repositories and worktrees with coordinator refs,
legacy/new JSON, multiple workstream branches, shared constraints, repeated hashes,
prefix collisions, deleted items, missing objects, and execution logs.

Reset: remove fixture-owned worktrees/runtime files, release locks/processes, and
leave real source artifacts committed on the original clean workstream branch.
