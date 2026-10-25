# CR-4 exact-candidate review

- Reviewer: `/root/final_review`
- Candidate: `874f091165f5e4cb8dc2d3a03ee0c7160cab8bf1`
- Tree: `f91f080dd83edafdbb098ecaa584390aeaaca41b`
- Verdict: `APPROVED`
- Canonical proposal payload SHA-256 (top-level `review` excluded): `b643b7c4530deb2621262e1e2bf1e0b0e2dc846288b05ea70a318a38889d7535`

## Finding withdrawal

I withdraw the P2 finding from my initial review. I misread the exact candidate:
the comparison at `recovery.py:1431–1435` includes `decision`, so a modified
decision fails the expected-proposal comparison. This exact-candidate review is
now `APPROVED`. A regression for this condition would strengthen coverage, but
its absence does not block the implementation.

## Scope and evidence

The change paths are within CR-4's owned paths. The audit binds the named product
ref and commit, distinguishes product-ref artifacts from checkout-only data,
reports tracked-pin/authority and task-result conflicts, and states the
limitations. The proposal binds the exact audit and captures those preimages;
its current decision and non-mutation flags are consistent with the audit and
CR-4's proposal-only boundary. The validator performs read-only Git checks and
reports that it neither mutates product state or authority nor schedules tasks.
Focused tests cover those non-mutation guarantees, moved refs, active writers,
unsupported verifier capability, and changed preimages, but not the decision
field mutation specifically.

No product or authority mutation was observed in the reviewed diff. `git diff
--check` passed. No tests were run during this review.
