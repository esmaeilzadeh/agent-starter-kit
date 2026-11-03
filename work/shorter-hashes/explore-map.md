# Explore Map: Work-scoped short hash references

## Destination

Replace opaque hash identifiers with readable, work-scoped references wherever the identifier names a domain item such as a task or test. Prefer hierarchical IDs such as `shorter-hashes/task/<task-id>` and `shorter-hashes/test/<task-id>/<test-id>`, using unpadded numeric components. Keep hashes for content-integrity checks and any remaining references that truly need them; make abbreviated reference length configurable below eight characters and expandable on collisions within the work.

## Notes

- Standing preference: keep agent-facing context compact; do not pay for global uniqueness when references are scoped to one work.
- Recovered source: `.later/shorter-hashes.md` was deleted at `c39dcf2` after `refactor-inner-loop` deferred it until integration. It proposed reviewing prompts, artifacts, and CLI output while preserving full hashes where needed for durable identity, audit evidence, or exact Git operations.
- Current assumption to confirm: hierarchical IDs replace hashes for task/test references; full cryptographic digests remain available wherever integrity verification or exact Git identity depends on them.
- For hashes that remain as references, recommend a configurable six-character minimum, with collision detection increasing prefixes as needed within the work.

## Decisions so far

- Task references should use `<work-id>/task/<task-id>`.
- Test references should use `<work-id>/test/<task-id>/<test-id>`.
- Use unpadded numeric IDs; tools that order them must use numeric-aware sorting.
- Work qualification makes references unambiguous across work boundaries; task/test references need no hash prefix.
- Hashes are poor domain identifiers because they are opaque and add no useful meaning to tasks, tests, or similar work items. Prefer readable identifiers there; retain hashes for content integrity.
- Any remaining hash-reference collision domain is the containing work, not the repository as a whole. Its configurable minimum may be less than eight and must be adjustable upward after a collision.

## Not yet specified

- Whether the hierarchical task/test IDs are canonical serialized IDs or compact references projected from existing IDs.
- Whether specs and other work-owned artifacts should use a similar hierarchical ID form.
- Where configurable shortening applies to hash references that remain (per-work setting or repository default with per-work expansion).
- Whether shortening applies to serialized references, human-facing output, or both.
- Whether collision handling expands only colliding hashes or raises the configured minimum for the whole work.
- Which hash-bearing surfaces still need compact references beyond task/test identity.
- Initial default length (six is a recommendation, not yet confirmed).

## Out of scope

- Changing hash algorithms or weakening verification by truncating a digest that is used as a cryptographic integrity check.
- Changing Git object IDs required for exact Git operations.

## Handoff to Intent

Use unpadded hierarchical numeric IDs for work-owned tasks and tests, carrying the work ID in references that cross the work boundary; sort numerically in tools. Determine whether specs and other artifacts follow the same pattern. For remaining hash references, define the configurable work-local prefix length and collision behavior, while retaining full cryptographic digests where integrity or exact Git identity requires them. The recovered card provides the original rationale and surfaces; this map records the human's scope and ID examples.

## Subsequent decision

The user approved extending numeric IDs to specs/parts and plans/items as well as
tasks/tests, with related parent prefixes, numeric item revisions, and full
integrity data in a separate file. This supersedes the open artifact-family
question and six-character default for ordinary workflow references above. The
decision, scope, and transition are recorded in `spec-change.md`; revision 6 of the
proposal and canonical contract define the current destination. The exploration
above is retained as historical context.
