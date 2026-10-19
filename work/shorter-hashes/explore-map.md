# Explore Map: Work-scoped short hash references

## Destination

Define a consistent, configurable way to shorten hash references used inside a workstream, such as references among tasks and specifications. The relevant uniqueness boundary is one workstream, not the whole repository or universe. The minimum prefix length must be configurable below eight characters and must be possible to increase when a collision is encountered.

## Notes

- Standing preference: keep agent-facing context compact; do not pay for global uniqueness when references are scoped to one work.
- Recovered source: `.later/shorter-hashes.md` was deleted at `c39dcf2` after `refactor-inner-loop` deferred it until integration. It proposed reviewing prompts, artifacts, and CLI output while preserving full hashes where needed for durable identity, audit evidence, or exact Git operations.
- Current assumption to confirm: short prefixes are work-scoped references; full cryptographic digests remain available wherever integrity verification or exact Git identity depends on them.
- Initial configurable minimum: recommend six hexadecimal characters, with collision detection increasing the shown/recorded prefix length as needed within that work.

## Decisions so far

- Collision domain is the containing work, not the repository as a whole.
- The configured prefix length may be less than eight and must be adjustable upward after a collision.

## Not yet specified

- Whether the setting is per-work, repository-wide with per-work collision expansion, or both.
- Whether to shorten only human-facing references or also serialized references inside work artifacts.
- Whether collision handling expands just the colliding references or raises the configured minimum for the whole work.
- Which hash-bearing surfaces are in scope beyond tasks, specs, prompts, artifacts, and CLI output.
- Initial default length (six is a recommendation, not yet confirmed).

## Out of scope

- Changing hash algorithms or weakening verification by truncating a digest that is used as a cryptographic integrity check.
- Changing Git object IDs required for exact Git operations.

## Handoff to Intent

The destination is to reduce hash noise in work-local references while preserving uniqueness within each work. Intent should define a configurable minimum prefix length below eight, explain how collisions expand that length, and identify whether shortening affects display only or serialized references too. The recovered card provides the original rationale and surfaces; this map records the human's clarified work-local collision boundary.
