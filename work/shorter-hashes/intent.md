# Intent: Reduce workflow token cost with compact references and exact dependencies

## What

Reduce tokens in workflow JSON, agent prompts, CLI output, and reports; improve
readability second. Shorten ordinary hash references, compact generated JSON,
and eliminate repeated metadata. Use readable task/test IDs and shared Git
snapshot references instead of copying committed-artifact checksums across JSON.
Keep full checksums for evidence outside Git wherever verification needs them.

Bind each actual dependency to its exact source snapshot, path, and stable
artifact item ID. Git supplies history without separate per-item revision counters
or checksum histories. Compare meaningful item content and bindings so an unrelated
edit in the same file does not invalidate an independent requirement or plan.
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
- Ordinary hash references use a six-character repository minimum with validated
  per-work overrides; only colliding displays grow, and ambiguity is rejected.
  Exact Git operations resolve full IDs. Prefixes never verify integrity.
- New task/test IDs are unpadded local numbers with readable qualified forms
  `<work>/task/<task>` and `<work>/test/<task>/<test>`; legacy mappings stay stable.
- Dependency identity includes owner, pinned snapshot, path, and stable item ID;
  local context may be inherited, while cross-workstream ownership is explicit.
  Ownership or a lookup link alone does not establish a dependency.
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

No unresolved What/Why question. This reconciled complete intent and its assumptions
await the required submitted approval. Exact schemas, discovery rules, extraction
algorithms, corpus, and command flags are Plan deliverables constrained by the spec.

## Human decisions

- Primary goal: reduce token consumption; secondary goal: readability.
- Preserve exact dependency provenance for every existing relationship, not only
  spec-to-plan; independent items must remain unaffected.
- Use project-wide dependency impact with workstream-scoped ownership.
- Preserve revision 4 refinements and require cross-workstream traversal explicitly.

## Engineering subject

- Subject: `shorter-hashes/readable-work-identifiers`.
- Source: explicit user request and subsequent dependency refinements; original
  Explore snapshot `5e9522e9842b540dcc1493569a062c66d382e4e0803c2d12889b65d9a70a5a2f`.
- Contribution: lower workflow token cost with compact references and shared Git
  identities while preserving exact item dependencies and acceptance authority.
- Execution owner: none assigned; implementation has not started.

## E2E

Applicability: `applies`

Journeys: query compact task/test/status/evidence projections; resolve exact inputs;
change one requirement beside an independent item; traverse a shared-policy change
across workstreams; reassess through retain/revise/retire decisions; verify valid
and invalid completion; reload historical records and exported evidence.

Observable outcomes: lower measured aggregate tokens and metadata bytes; exact
source/approval/execution binding; impact follows actual item edges across owners;
unrelated items stay eligible; unresolved, missing, ambiguous, or altered evidence
cannot authorize completion. Original evidence remains historically retrievable.

Environment/data: temporary Git repositories and worktrees with coordinator refs,
legacy/new JSON, multiple workstream branches, shared constraints, repeated hashes,
prefix collisions, deleted items, missing objects, and execution logs.

Reset: remove fixture-owned worktrees/runtime files, release locks/processes, and
leave real source artifacts committed on the original clean workstream branch.
