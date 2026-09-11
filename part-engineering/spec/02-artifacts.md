# Artifact Model and Spec Lifecycle

# 6. Artifact model

Every material phase should have an artifact.

## 6.0 Explore map

**Canonical path (always, when Explore runs):**

```text
work/<work-id>/explore-map.md
```

This file is the source of truth for handoff into `01 Grill`, including in repos with no issue tracker.

**Optional tracker mirror:** If the consumer has a configured issue tracker, Explore may also maintain a wayfinder-shaped tracker map for collaboration. The workstream file must include a pointer to that tracker map. The tracker must not replace the file as the Grill handoff artifact.

**Child Explore tickets** (research / prototype / grilling): live on the tracker when mirroring; otherwise under `work/<work-id>/explore/`, always linked from the map file.

Minimum fields:

```markdown
# Explore Map: <title>

## Destination

## Notes

## Tracker map (optional)
<!-- URL or id when mirroring -->

## Decisions so far

## Not yet specified

## Out of scope

## Handoff to Intent
```

**Gate:** `## Handoff to Intent` must be non-empty (clear destination + remaining human decisions) before `01 Grill`. Closing a tracker map alone is not sufficient. Grill must be able to produce `intent.md` from this file without re-deriving from chat.

## 6.1 Intent

Path:

```text
work/<work-id>/intent.md
```

Template:

```markdown
# Intent: <title>

## What

## Why

## Non-goals

## Known assumptions

## Open questions

## Human decisions
```

The artifact represents clarified human intent, not merely a copy of the original request.

---

## 6.2 Specification

Initial path:

```text
specs/proposals/<work-id>.md
```

Template:

```markdown
# Specification: <title>

## Status
PROPOSED

## Goal

## Non-goals

## Behavior

## Interfaces

## Constraints

## Invariants

## Failure cases

## Acceptance criteria

## Open questions

## Source intent
<work-id>
```

The specification must preserve a stable relationship to its source intent.

After acceptance, it may be promoted or copied to the project's canonical current location according to policy.

---

# 7. Specification lifecycle

Supported semantic states:

```text
OBSERVED
PROPOSED
ACCEPTED
IMPLEMENTED
VERIFIED
CURRENT
```

Recommended lifecycle:

```text
PROPOSED
   ↓
ACCEPTED
   ↓
IMPLEMENTED
   ↓
VERIFIED
   ↓
CURRENT
```

`OBSERVED` is used when the repository documents behavior that exists without necessarily asserting that it is the desired semantic contract.

Important invariants:

```text
Never silently rewrite an accepted spec during implementation.
Never infer that observed code behavior is the desired spec merely because it exists.
Never promote a proposed change to CURRENT without the required decision and verification.
```

---

# 8. Specification Challenge artifact

Path:

```text
work/<work-id>/spec-challenge.md
```

Minimum fields:

```markdown
# Specification Challenge

## Specification

## Ambiguities

## Hidden assumptions

## Counterexamples

## Conflicting requirements

## Acceptance-criteria gaps

## Recommended changes

## Outcome
PASS | ESCALATE
```

The challenge agent must not silently rewrite the accepted human intent.

---

# 9. Specification Change artifact

Path:

```text
work/<work-id>/spec-change.md
```

Template:

```markdown
# Specification Change Proposal

## Trigger

## Current specification

## Observed behavior / new analysis

## Problem with current specification

## Proposed semantic change

## Why the change is needed

## Impact

## Alternatives considered

## Required human decision

## Decision
PENDING | ACCEPTED | REJECTED
```

Use this workflow when:

```text
implementation reveals a requirement problem
analytics produces new understanding
review identifies a semantic mismatch
acceptance criteria need to change
business/domain invariant needs to change
```

The Spec Change Agent does not silently modify `specs/current/`.

---

# 10. Planning artifact

Path:

```text
work/<work-id>/plan.md
```

The plan must reference exactly one accepted specification revision.

Minimum structure:

```markdown
# Plan

## Accepted specification

## Scope

## Implementation tasks

## Verification tasks

## Dependencies

## Risks

## Escalation points

## Potential specification changes
```

The plan may decompose implementation but may not redefine requirements.

---

# 11. Review artifact

Path:

```text
work/<work-id>/review.md
```

Review finding format:

```markdown
## Finding RV-001
Severity: LOW | MEDIUM | HIGH | CRITICAL
Status: OPEN | FIXED | ACCEPTED | ESCALATED

### Claim

### Location

### Evidence

### Suggested correction
```

Review findings must be structured for machine consumption by the Refactor Agent.

Review should cover, as applicable:

```text
requirements
constraints
invariants
error paths
security
maintainability
tests
unintended scope
architecture
performance claims when relevant
```

Prefer concrete evidence to vague statements such as "this feels wrong."

---

# 12. Verification artifact

Path:

```text
work/<work-id>/verification.json
```

Minimum schema:

```json
{
  "verification_id": "",
  "work_id": "",
  "commit": "",
  "spec": "",
  "checks": [
    {
      "name": "",
      "status": "PASS",
      "evidence": ""
    }
  ],
  "created_at": ""
}
```

The `commit` field is mandatory.

The verifier must not report a check as passed unless the check actually ran or the repository has an explicitly documented equivalent evidence source.

---

# 13. Acceptance artifact

Path:

```text
work/<work-id>/acceptance.md
```

Minimum fields:

```markdown
# Acceptance

## Specification

## Code commit

## Verification

## Review summary

## Unresolved findings

## Risk class

## Acceptance decision
AUTO_ACCEPT_ELIGIBLE | HUMAN_APPROVAL_REQUIRED | REJECT

## Human decision

## Authority used
```

Acceptance must be policy-driven.

The Accept Agent assembles evidence and determines eligibility. It is not automatically the final human authority.

---

# 14. Result provenance

Path may be inside Git or an external result store depending on project needs.

Minimum schema:

```json
{
  "result_id": "",
  "work_id": "",
  "commit": "",
  "spec": "",
  "verification": "",
  "result": {},
  "created_at": ""
}
```

The result is invalid without an exact commit SHA.

For example:

```json
{
  "result_id": "order-cancel-perf-01",
  "work_id": "cancel-order",
  "commit": "8f31c42",
  "spec": "specs/current/cancel-order.md",
  "verification": "verify-17",
  "result": {
    "p95_ms": 83
  },
  "created_at": "2026-09-10T12:00:00Z"
}
```

The essential lineage is:

```text
which code
→ which commit
→ which spec
→ which verification
→ which result
```

Do not store full agent transcripts merely to satisfy provenance.

---
