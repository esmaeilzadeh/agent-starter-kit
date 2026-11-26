# 18. Verification policy

File:

```text
_ask/policies/verification.md
```

The policy should map classes of claims to appropriate evidence.

Example:

```text
Type correctness
→ compiler/type checker

API behavior
→ integration/contract tests

Security invariant
→ security check + targeted tests

Performance claim
→ reproducible benchmark

Architecture boundary
→ static/architectural check where available

Formal mathematical property
→ formal proof where justified
```

The kit must explicitly avoid claiming that one evidence source is universally strongest.

The evidence mechanism must fit the claim.

## Failure diagnosis

A failed check is evidence to diagnose, not automatic permission to change code
or requirements. Record the failed command/case, candidate revision, observed
failure, and the evidence for its cause before choosing a route:

- **Implementation violates the accepted contract:** reproduce the defect, repair
  within scope through Implement, then rerun checks and candidate review.
- **Check, fixture, test data, or environment is wrong:** repair verification
  within existing authority while preserving the accepted criterion. Rerun the
  original obligation against the affected candidate; document any check change.
- **Acceptance criterion or contract is wrong or ambiguous:** use Spec Change or
  obtain the missing human decision before dependent work. Preserve the failure.
- **Environment, access, or dependency is unavailable:** record a blocker and the
  input needed to resume. Do not count an unexecuted check as passing.
- **Cause unknown:** investigate; use workflow uncertainty routing for remaining
  technical judgment or human decisions.

Verification repairs that change product behavior or weaken an obligation need
the corresponding authority. A changed candidate needs fresh applicable evidence
and review. Resume Verify only when the cause is resolved; retry limits do not
turn a failure into permission to change scope or claim success.

---
