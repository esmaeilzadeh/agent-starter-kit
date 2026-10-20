# Intent: Reduce hash token cost and improve readability

## What

Review hash references and workflow JSON across agent prompts, workstream
artifacts, command-line output, and reports. Reduce token use by shortening
ordinary references, compacting generated JSON, and eliminating repeated
metadata and checksums wherever they can be resolved safely. Improve readability
second by using readable, work-qualified identifiers for tasks and tests, such
as `shorter-hashes/task/3` and `shorter-hashes/test/3/2`.

Use a repository default of six characters for remaining hash references, with
per-work overrides. Detect ambiguity within the work and lengthen only
colliding references until they are unique. For integrity records, store each
full digest in one authoritative, immutable record and refer to that record
from related JSON. Keep accepted contract authority coordinator-owned; separate
accepted contract pins from later run/evidence records. Derive tracked-file
content from a pinned Git revision and path only where that preserves the
existing digest semantics and availability guarantees. Preserve full
cryptographic digests wherever verification requires them and full Git object
IDs for operations that require exact identity.

The primary outcome is lower token consumption. Readability is the secondary
outcome.

## Why

Full hashes and verbose JSON consume context, especially when the same values
and metadata are copied across records. Shorter references, shared immutable
integrity records, and compact generated JSON reduce repeated token cost;
readable task and test IDs also make agent context easier to scan. Savings must
be measured over representative complete agent inputs, including any references
that need resolving.

## Non-goals

- Changing hash algorithms or weakening cryptographic verification.
- Shortening values where an exact Git object ID is required by an operation.
- Replacing authoritative integrity digests with truncated values.
- Redesigning unrelated IDs or optimizing unrelated non-JSON prompt and
  artifact text.
- Removing evidence or audit information to reduce tokens.
- Replacing coordinator-owned acceptance authority with candidate-controlled
  manifests or mutable short aliases.

## Known assumptions

- “All hashes” means every eligible hash reference surfaced in prompts,
  artifacts, command output, and reports; integrity and exact-operation values
  remain full.
- JSON optimization applies to JSON used by this workflow, including generated
  contracts, accepted pins, run records, and reports; it does not mean
  reformatting every unrelated JSON file in the repository.
- Accepted contract pins and run/evidence records have separate immutable
  lifetimes. Each reference resolves through authoritative records, and missing,
  ambiguous, or unavailable targets fail explicitly.
- Token savings are assessed on representative end-to-end agent context and
  persisted JSON size, not inferred from shorter individual fields.
- Task and test references use readable hierarchical IDs qualified by work;
  their identifiers do not need hash prefixes.
- Six characters is the default minimum for remaining display/reference
  prefixes. A work may override it, and only colliding references grow.
- A short reference is resolvable in its declared work scope, and the full
  authoritative value remains available to verification and Git tooling.
- Token reduction takes priority when token savings and readability conflict.

## Open questions

None. The complete assumptions above are submitted for approval.

## Human decisions

- Primary goal: reduce token consumption.
- Secondary goal: improve readability.
- Scope: eligible hash references and workflow JSON, including deduplication of
  repeated integrity metadata while retaining authoritative full digests.

## Engineering subject

- Subject: `shorter-hashes/readable-work-identifiers`
- Source: explicit user request, resolved at Explore snapshot
  `5e9522e9842b540dcc1493569a062c66d382e4e0803c2d12889b65d9a70a5a2f`
- Contribution: reduce token consumption first by shortening ordinary hash
  references and redundant workflow JSON; improve readability second.
- Exclusions: preserve full cryptographic integrity digests and exact Git
  object IDs; do not change hash algorithms or weaken verification.
- Execution owner: none assigned.

## E2E

Applicability: `applies`

Journeys: an agent reads task, test, commit, and integrity references in
prompts, artifacts, CLI output, and reports; resolves short references through
authoritative records for their declared work; and verifies that collisions,
stale content, missing records, or unavailable Git objects fail without
altering authority.

Observable outcomes: representative complete agent inputs and generated JSON
use fewer tokens/bytes; task and test references are readable and
work-qualified; repeated integrity metadata is stored once where resolution is
safe; references are unique within their authority; integrity checks and exact
Git operations continue to use full authoritative values.

Environment and test data: repository fixtures with representative prompts,
workflow JSON, CLI results, historical and current evidence, a deliberate
same-prefix collision, repeated digests, missing records, and unavailable Git
objects.

Reset: run checks in isolated temporary Git repositories or worktrees and
remove those fixtures after each run.
