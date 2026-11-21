# Specification Change: Close the reopened revision-6 challenge

## Current specification

Revision 6 and its challenge are retained at
`9a3d25d:specs/current/shorter-hashes.json`,
`9a3d25d:specs/proposals/shorter-hashes.md`, and
`9a3d25d:work/shorter-hashes/spec-challenge.md`.

The original PASS did not sufficiently distinguish behavioral gaps from bounded
implementation choices. The reopened independent review identified three gaps:

| Finding | Two outcomes previously left possible | Revision-7 closure |
| --- | --- | --- |
| G1: meaningful equality | Ignore a changed inherited obligation or external binding because local text/blob is equal; alternatively revise and reassess. | All obligation-bearing content and exact input bindings participate by default. Versioned, pre-reviewed presentation exclusions are exhaustive. Unknown fields are significant; unavailable comparison context cannot prove equality. Blob equality cannot bypass external bindings. |
| G2: propagation stopping | Clear a descendant by treating its immutable old pin as the new revision; alternatively require a new pin/revision or reviewed retention. | A stop names exact versions, consumers, paths, profiles, evidence, and authority. Retaining an old pin requires explicit validity in the new context; changing a pin creates a revision. Changed outward/inherited obligations or unresolved inputs continue reassessment. Historical edges/runs remain intact. |
| G3: complete discovery | Report complete impact from a mixed scan that omits a new owner; alternatively retry or report incomplete. | Complete results bind an authoritative local owner/ref inventory, consistent immutable snapshot vector, and capture generation. Inventory changes require serialized capture, retry, or incomplete results. New-context clearance checks its selected scope again. |

## Proposed change

Revision 7 adds normative comparison/stop/discovery rules and required decision
examples to the Markdown specification, with corresponding SH-02/07/15/16/18
assertions in the canonical JSON. The identity scheme, separate integrity data,
coordinator authority, token/byte savings thresholds, retirement, migration, and
cross-workstream ownership requirements remain in force.

## Why the change is needed

Deterministic implementation choices can still disagree about whether an item
changes or a dependent remains eligible. Those outcomes must be settled before
Plan. Calling them Plan details did not close them.

## Alternatives

- Keep revision 6 and its broad PASS: leaves the three behavioral gaps open.
- Freeze implementation formats and algorithms in the spec: constrains mechanisms
  without necessarily defining correct observable decisions.
- Define decision boundaries and normative examples, then independently challenge
  them: selected; exact encodings/algorithms remain constrained Plan choices.

## Impacted artifacts and workstreams

Only `shorter-hashes`: canonical/proposal spec, source-intent clarification,
independent challenge, closure receipt, and consolidated planning artifacts.
Existing source/history and prior review decisions remain retrievable in Git.
No runtime code or other workstream is changed by specification closure.

## Migration / transition notes

All 18 criterion IDs remain stable. A future implementation must use reviewed
comparison profiles and explicit legacy provenance; this amendment creates no
historical approval, versions, runs, or accepted coordinator pins. Old review
digests do not approve the new contract.

## Acceptance criteria for the change

The independent reviewer must classify every prior deferral and counterexample
as covered by a cited rule, a bounded implementation choice with invariant
outcomes, or an open blocker. G1/G2/G3 need explicit closure against the revised
normative rules and examples. Any remaining behavioral blocker prevents a seal.
The seal must identify exact committed spec sources/digests and independent
review attribution. Consolidated Plan/TaskGraph/test mapping must derive from
that one specification without changing its behavior.

## Decision / authority

The user instructed “continue till spec sealed”, then “continue till you
consolidated plan and task become clear”. This authorizes resolving the identified
gaps within the recorded destination and preparing the consolidated plan/tasks.
It does not authorize production implementation, lower acceptance thresholds,
or invent complete-intent approval. Any new What/Why conflict must still be
escalated instead of being resolved through a silent scope change.
