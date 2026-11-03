# Specification Change: Numeric hierarchy and item revisions

## Current specification

Prior source: `6bbcde91ed31276d56d3b74df94d2e31e6d9fc96` on
`agent/shorter-hashes`, with revision 5 in
`specs/current/shorter-hashes.json` and its Markdown proposal.

Revision 5 specified numeric task/test IDs, six-character ordinary hash
references, and Git-backed item identity without requiring per-item numeric
revisions. Spec/part and plan/item numeric IDs and parent qualification were
unspecified. Full source IDs were shared, but a separate integrity file for
numeric item/revision references was not required.

The independent challenge in `spec-challenge.md` covers revision 5 at its exact
recorded commit and digests. Git retains the prior documents unchanged at those
commits. No accepted implementation plan or implementation is present.

## Proposed change

Apply revision 6 to the proposed contract and reconcile its source intent:

- Use unpadded positive numeric local IDs for specs and their parts/requirements,
  plans and their items, tasks, and tests, qualified by work, type, and declared
  related parent identities.
- Give each artifact/item immutable positive numeric revisions distinct from its
  stable logical identity. A meaningful content or dependency-binding change
  publishes a fresh revision. Unrelated edits and ancestor version changes alone
  leave independent item identities and revisions unchanged.
- Use numeric item/revision references in ordinary workflow records. Store full
  required checksums and exact Git identities in a separate integrity file;
  resolve each reference to its exact source snapshot, path, and stable item ID.
- Preserve shared Git history, byte/canonical-JSON verification semantics,
  external-evidence digests, coordinator authority, historical evidence, and
  project-wide impact traversal. Numbers and integrity-file edits grant no
  approval or evidence-transfer authority.
- Keep ownership prefixes separate from dependency edges, so multiple upstream
  inputs do not duplicate one item. The Plan defines exact grammar, parent rules,
  file paths, and publication interfaces. The user's examples illustrate intent;
  they are not a prescribed contract syntax.

The default identity scheme is numeric. Scoped hash abbreviation remains relevant
only to explicit raw Git/hash inspection and compatible historical references.

## Why the change is needed

The user clarified that parent-qualified numeric references apply across
spec/plan/task items, with numeric versions and separately stored checksums.
Restricting numeric IDs to tasks/tests and omitting item revisions failed to
capture that intention. The correction retains the primary token-reduction goal.

Alternatives considered:

| Alternative | Consequence |
| --- | --- |
| Keep revision 5 | Leaves spec/plan numeric identities unspecified and uses Git snapshots without required numeric item revisions; does not satisfy the clarification. |
| Fix a literal reference grammar now | Prematurely treats illustrative examples as a contract and constrains multi-input ownership choices. |
| Numeric hierarchy/revisions with separate integrity data | Captures the approved behavior while leaving exact versioned schemas and storage paths for Plan. Selected. |

## Impacted artifacts

- `specs/current/shorter-hashes.json`: advance to revision 6; reconcile SH-01,
  SH-02, SH-03, SH-07, SH-08, SH-10, SH-11, SH-15, and SH-18.
- `specs/proposals/shorter-hashes.md`: align behavior, invariants, criteria,
  source/approval status, and E2E journeys with numeric identities/revisions.
- `intent.md` and `engineering-model.json`: align the recorded destination.
- `explore-map.md`: retain its original exploration and append the superseding
  decision so earlier open questions are not mistaken for current ones.
- `spec-challenge.md`: retain the revision-5 review unchanged; revision 6 needs
  its own independent challenge before progression to an accepted plan.
- Future Plan/test-plan/TaskGraph: define numeric parent/revision allocation,
  immutable integrity entries, legacy migration, concurrency, and executable
  verification. Their current scaffolds are not an implementation plan.

## Impacted workstreams

Only `shorter-hashes` documents change. Future implementation must inventory all
workflow producers/consumers and cross-workstream dependencies already required
by this proposal. This amendment does not authorize editing another workstream.

## Migration / transition notes

Keep existing criterion labels (`SH-01`–`SH-18`) and historical IDs stable.
This amendment specifies future runtime identity behavior; it does not migrate
existing records or claim that the numeric scheme is implemented. Legacy
conversion must preserve exact sources and cannot invent item versions, approval,
or execution evidence. Required old revision entries and Git objects remain
retrievable. Changed/missing integrity entries, duplicate parent-qualified IDs,
and conflicting revision publication must fail explicitly.

## Acceptance criteria for the change

Revision-6 JSON and Markdown must agree on numeric identities across all named
artifact/item families, parent context, immutable revisions, separate full
integrity data, and exact dependency-version bindings. Unrelated changes must not
cause revision churn; relevant content or binding changes must create a revision.
All prior authority, evidence, migration, measurement, partial-invalidation,
retirement, and cross-workstream requirements remain in force.

Validate the canonical contract structure and the amendment's consistency, run
`./ask verify`, and record the actual result against the committed source. A
workflow refusal at this pre-implementation stage is not implementation evidence
and must not be recorded as a passing workstream.

## Decision

Approved amendment. Exact user response: **“yes apply it”**.

The response followed the explicit clarification that the current spec lacked
the complete parent-prefixed numeric spec → plan → task identity system, and
that the intended hierarchy includes numeric revisions and separate checksums.
It authorizes this correction without a repeated approval request.

This is scoped specification-change approval. It is not complete-intent approval,
an independent challenge, implementation-plan acceptance, execution evidence,
or final workstream acceptance.
