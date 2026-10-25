# CR-4 exact-candidate review

- Reviewer: `/root/final_review`
- Candidate: `a2b7522d47bfcf3c26cf8b2b1923ccd2338989c8`
- Tree: `24d5993933a2da845b66d4b933bd016b903dd25b`
- Base: `bf8696707293700a384850710490432420cadfce`
- Verdict: `REJECTED`
- Canonical proposal payload SHA-256 (top-level `review` excluded): `b643b7c4530deb2621262e1e2bf1e0b0e2dc846288b05ea70a318a38889d7535`

## Finding

- **P2 — checkout-only review evidence can escape the repository.** In
  `_ask/scripts/inner_loop/recovery.py:1244–1249`, the legacy state supplies
  `review_path`; the prefix check only checks that it starts with
  `work/<work-id>/inner-loop/evidence/`. `_legacy_artifact` rejects `..` for
  the Git lookup, then its checkout fallback at lines 997–1004 reads
  `root / path` without equivalent path containment validation. A path such as
  `work/shorter-hashes/inner-loop/evidence/../../../../etc/hostname` therefore
  reaches a file outside the checkout and contributes its SHA-256 to the audit.
  Reject traversal and symlink escapes before checkout reads; add a regression
  proving an outside file is never accessed or represented as checkout-only
  evidence.

## Review evidence

The added decision-tampering regression is sound: it changes `decision`,
recomputes the proposal review digest, and expects refusal. The validator also
compares `decision` to the generated proposal; the previously reported decision
finding was mistaken and remains withdrawn in the prior candidate review.

The real audit binds product ref `refs/heads/agent/shorter-hashes` at commit
`d04b3a4e515105df8cdf703f2fa0a28895f1524d`. It reports the tracked-pin versus
authority mismatch and result/state conflicts. Task 1's historical Red, Green,
Refactor, and integration evidence are missing or unverified; tasks 2–5 have
checkout-only Red/Green data, no structured Refactor or integration, and
conflicts. The proposal binds the exact audit, preserves preimages, and leaves
product state, authority, test classification, and task scheduling unchanged.
Its `review` field is still pending. These gaps are disclosed rather than
presented as verified adoption evidence.

Review is against the exact candidate/tree above. No source files were modified
and no tests were run during this review.
