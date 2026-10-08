# Harness reliability: completed implementation

## Current state

R1/R2 are implemented and locally verified on agent/harness-review. Independent
review is APPROVED. No implementation or verification work remains. Acceptance
eligibility/evidence is in acceptance.md; no separate human final acceptance is
invented and no permission question is pending.

Verified source commit: 4c13aec67d17228fad5b67074125cf939e2d4c7d.
Independent review/context-audit commit: e3a660fec76f88a37751dcbcd3ba0ad479653eca.
Final full ./ask verify: PASS, all 35 mandatory shell checks including 29
reliability cases. verification.json and evidence/full-verify.log record the
executed source SHA. Later commits contain result/review artifacts only.

## Delivered behavior

- TaskResult v2 binds work/task/base/candidate and keeps TDD history distinct
  from verification. A coordinator operation records attributable review bound
  to result, review and policy bytes; worker acknowledgment alone is insufficient.
- Verification snapshots runner/imports from the recorded coordinator base,
  executes the candidate's committed CheckPlan in a clean detached worktree,
  records checks/provenance, and revalidates inputs before pinned FF/state fold.
- State initialization is idempotent; local process-safe transactions serialize
  CAS and writer invariants. Same-directory atomic replacement protects readers.
- Resume preserves tracked runtime state/reviews during source or merge repair,
  and revalidates FF-before-fold interruptions without resetting valid candidates.
- Canonical instructions/docs and generated projections describe the new flow.
- AGENTS.md records the user's rule requiring concrete progress feedback at
  least every 60 seconds; a generic Working indicator is insufficient.

## Preparation and branch reconciliation

335d120 preserved the handoff/resume documents. ed6fa62 merged current main into
develop while preserving both later inboxes. Main remained unchanged. Baseline
verification passed 34 checks; the new reliability test raises the final count
to 35. Pinned skills prepared, bindings synced, and the workstream started from
updated develop. Handoff basis 9602217 and current main had identical reviewed
integration/state/verification source; both findings were confirmed.

## Findings and limitations

The first independent review found tracked-state loss on resume despite passing
initial tests. Its reproduction, fix and independent rerun are retained in
review.md/refactor.md and evidence/. Configured generated-role models were
unavailable; independent same-family fallback contexts were used and disclosed.
The boundary is cooperative local POSIX processes, not a security sandbox or a
multi-host store. No power-loss durability or comparative performance claim.

R3–R5 are explicit recommendations in followups.md. The companion
decision-review-harness-note.md was absent; its contents were not inferred.
No pushes, feature merges, tags, deployment or external messages were performed.

## Future continuation

Read acceptance.md, review.md and verification.json before release/integration.
Treat R3–R5 as separately sequenced pilot/evaluation work. Preserve the later
inbox if reconciling branches again; no unrelated workstream was started here.
