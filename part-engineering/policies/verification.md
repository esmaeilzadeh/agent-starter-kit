# 18. Verification policy

File:

```text
part-engineering/policies/verification.md
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

---
