# Explore Map: Work-scoped short hash references

## Destination

Define compact, unambiguous references for work-owned items. Prefer hierarchical, work-qualified IDs for tasks and tests over hashes, for example `shorter-hashes/task/<task-id>` and `shorter-hashes/test/<task-id>/<test-id>`. Choose a numeric format that supports easy string sorting without imposing a practical count cap. For any references that still use hashes, keep uniqueness scoped to the owning work, make the minimum prefix configurable below eight characters, and allow it to grow when collisions occur.

## Notes

- Standing preference: keep agent-facing context compact; do not pay for global uniqueness when references are scoped to one work.
- Recovered source: `.later/shorter-hashes.md` was deleted at `c39dcf2` after `refactor-inner-loop` deferred it until integration. It proposed reviewing prompts, artifacts, and CLI output while preserving full hashes where needed for durable identity, audit evidence, or exact Git operations.
- Current assumption to confirm: hierarchical IDs replace hashes for task/test references; full cryptographic digests remain available wherever integrity verification or exact Git identity depends on them.
- For hashes that remain as references, recommend a configurable six-character minimum, with collision detection increasing prefixes as needed within the work.

## Decisions so far

- Task references should use `<work-id>/task/<task-id>`.
- Test references should use `<work-id>/test/<task-id>/<test-id>`.
- Work qualification makes references unambiguous across work boundaries; task/test references need no hash prefix.
- Any remaining hash-reference collision domain is the containing work, not the repository as a whole. Its configurable minimum may be less than eight and must be adjustable upward after a collision.

## Not yet specified

- Whether the hierarchical task/test IDs are canonical serialized IDs or compact references projected from existing IDs.
- How IDs stay lexically sortable without a practical maximum: fixed-width zero padding sorts simply but needs a width policy; unpadded decimals grow freely but require numeric-aware sorting; a length-prefixed decimal format can support both at the cost of longer, less familiar IDs.
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

Prefer short hierarchical IDs for work-owned tasks and tests, carrying the work ID in references that cross the work boundary. Resolve the numeric encoding tradeoff between lexical sorting and unbounded growth. Determine whether specs and other artifacts follow the same pattern. For remaining hash references, define the configurable work-local prefix length and collision behavior, while retaining full cryptographic digests where integrity or exact Git identity requires them. The recovered card provides the original rationale and surfaces; this map records the human's scope and ID examples.
