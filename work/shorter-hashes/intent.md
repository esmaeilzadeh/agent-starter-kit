# Intent: Reduce hash token cost and improve readability

## What

Review hash references across agent prompts, workstream artifacts, command-line
output, and reports. Reduce token use by shortening ordinary references wherever
they are presented or persisted for lookup. Improve readability second by using
readable, work-qualified identifiers for tasks and tests, such as
`shorter-hashes/task/3` and `shorter-hashes/test/3/2`.

Use a repository default of six characters for remaining hash references, with
per-work overrides. Detect ambiguity within the work and lengthen only
colliding references until they are unique. Keep the full value available in
authoritative data wherever tools need it. Preserve full cryptographic digests
for integrity verification and full Git object IDs for operations that require
exact identity.

The primary outcome is lower token consumption. Readability is the secondary
outcome.

## Why

Full hashes consume context while conveying little meaning in ordinary
references. Shorter references reduce repeated token cost; readable task and
test IDs also make agent context easier to scan. Integrity evidence and exact
Git operations still require their authoritative full values.

## Non-goals

- Changing hash algorithms or weakening cryptographic verification.
- Shortening values where an exact Git object ID is required by an operation.
- Replacing authoritative integrity digests with truncated values.
- Redesigning unrelated IDs or optimizing unrelated prompt and artifact text.
- Removing evidence or audit information to reduce tokens.

## Known assumptions

- “All hashes” means every eligible hash reference surfaced in prompts,
  artifacts, command output, and reports; integrity and exact-operation values
  remain full.
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
- Scope: all eligible hash references, retaining full integrity digests and
  exact Git IDs where required.

## Engineering subject

- Subject: `shorter-hashes/readable-work-identifiers`
- Source: explicit user request, resolved at Explore snapshot
  `5e9522e9842b540dcc1493569a062c66d382e4e0803c2d12889b65d9a70a5a2f`
- Contribution: reduce token consumption first by shortening hash references;
  improve readability second.
- Exclusions: preserve full cryptographic integrity digests and exact Git
  object IDs; do not change hash algorithms or weaken verification.
- Execution owner: none assigned.

## E2E

Applicability: `applies`

Journeys: an agent reads task, test, commit, and remaining hash references in
prompts, workstream artifacts, CLI output, and reports; resolves a shortened
reference within its declared work; and verifies that collisions lengthen
references without altering authoritative values.

Observable outcomes: ordinary references use fewer tokens; task and test
references are readable and work-qualified; colliding references are unique
within their work; integrity checks and exact Git operations continue to use
full authoritative values.

Environment and test data: repository fixtures with representative prompts,
artifacts, CLI results, and synthetic references including a deliberate
same-prefix collision.

Reset: run checks in isolated temporary Git repositories or worktrees and
remove those fixtures after each run.
