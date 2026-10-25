# CR-4 exact-candidate review

- Reviewer: `/root/final_review`
- Candidate: `622e89c879c1b09d4982b84b3327bcfcaa216059`
- Tree: `150e1cb98ec01fd6a689283a793300362b3e6042`
- Base: `bf8696707293700a384850710490432420cadfce`
- Verdict: `APPROVED`
- Canonical proposal payload SHA-256 (top-level `review` excluded): `b643b7c4530deb2621262e1e2bf1e0b0e2dc846288b05ea70a318a38889d7535`

## Findings and scope

No blocking findings. The checkout fallback now rejects empty, absolute,
backslash, and traversal paths before either Git or filesystem lookup; resolved
checkout paths must remain under the resolved repository root. This also blocks
symlink escapes. The regression checks traversal, absolute, and symlink paths
without dynamic `subTest` collection, so the pinned runner sees only CR-T15 and
CR-T16.

The earlier decision-field concern was mistaken and withdrawn. The validator
compares `decision` with its generated expected proposal, and the added test
changes the decision, recomputes the proposal digest, then confirms refusal.

The exact-candidate TaskResult binds Green run
`828faea9006a42c1b618d49f4906a79d`; its report digest matches, collection is
complete, and CR-T15/T16 both pass at this candidate. The TaskResult also
retains an executable focused reproduction against pre-fix candidate
`a2b7522d47bfcf3c26cf8b2b1923ccd2338989c8`, with exit 1 and the expected
outside-repository assertion. Updated TaskResult SHA-256:
`91220cf4ae2692e7eb893e1b1a0c39e56a6dd20ce391db52815fe245664b29a9`. No
synthetic Red is claimed.

The real audit binds `refs/heads/agent/shorter-hashes` at
`d04b3a4e515105df8cdf703f2fa0a28895f1524d`. It reports the tracked-pin versus
authority mismatch and state/result conflicts. Task 1 has missing Red/Green,
unverified review, no structured Refactor, and no integration receipt. Tasks
2–5 expose checkout-only Red/Green reports, missing review/Refactor/integration
evidence, and the recorded result/state conflicts. The proposal binds the exact
audit; its pending decision and false mutation/reclassification/scheduling flags
are consistent with the proposal-only boundary. Its current review binding is
APPROVED by `/root/final_review`, recorded by `/root`, against the exact payload
digest above. This approval does not authorize product adoption or scheduling.

The only applicable TDD boundary is the user's explicit one-time CR-4 waiver;
the review claims the observed focused pre-fix failure and current Green, not a
fabricated historical Red. No source files were modified and no additional
tests were run during this review.
