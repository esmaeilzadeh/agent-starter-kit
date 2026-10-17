# Specification Change Proposal: context-first work and readable evidence

## Current specification

Revision 3 at `38870c2f6c4e34c12bbe7d535f3005aa53a1edf3`, `specs/current/structured-agentic-environment.md`
and adjacent JSON. Accepted authority and historical challenge are unchanged.

## Proposed change

`specs/proposals/structured-agentic-environment.md` and adjacent JSON are
PROPOSED revision 4. Separate execution workstream from Epic/Story/Task scope,
permit direct/standalone entry and optional membership, define shared Task
support, repository-owned source context, readable Tests/evidence, and one
complete representative Story. Remove older harness from main pilot only.
Propose explicit Engineering Model v2 migration; no implementation here.

## Why the change is needed

The human could not relate the Epic or opaque Tests to their work. The agent
missed existing Story/Task entry and conflated workstream with Epic. Jira
comparison exposed the need to preserve documentation/code relationships in
versioned repository sources. See `intent.md` and `spec-gap-notes.md`.

## Impacted artifacts

Proposed spec/criteria, future v2 schema/validator and migration, context
projection/navigation, Task relationships, source/context display, selected
Tests, future reviewed test plan/TaskGraph and design. Current accepted spec,
pins, runtime state and evidence are not changed by this proposal.

## Impacted workstreams

Only `structured-agentic-environment` is under this proposal. General Ask
protocol improvements for discovering omissions are separate later work;
no new workstream or Jira deployment/integration is authorized.

## Migration / transition notes

Preserve canonical IDs and historical attribution; keep V1 historical records
under their version. Adopt V2 and repin contracts only after explicit reviewed
migration/planning. Retained runtime evidence may be locally unavailable.

## Acceptance criteria for the change

Retain EM-001–007 and EM-012; amend EM-008–011; add EM-013–018. Read proposed
Markdown and JSON together. Independent challenge must examine observability,
relationship cardinality, passage identity, migration and evidence limits.
No current test-plan mapping or accepted-ref advancement is claimed.

## Decision

PROPOSED. Human explicitly authorized storing this draft and starting Sol/high
in a clean context after same-family warning. That is review authorization,
not complete-intent approval, CURRENT promotion or implementation permission.
