# CSH-10 recovery reconciliation proposal

Status: proposal only; no inner-loop state or checkpoint mutation is authorized
by this record.

## Bound source and authority

- Work branch: `agent/client-security-hardening`.
- Product/evidence state assessed: `3d33dc9` (`docs: checkpoint client security task evidence`).
- Subsequent reconciliation records: `19645e8` (proposal) and `e889779`
  (privacy-safe evidence bundle). The source commits remain in their original order.
- Historical coordinator source: `9c62390c2f8b135f0b0256c2ad1233145d64c6d7`.
- Retained checkpoint ref: `refs/ask/inner-loop/client-security-hardening` at
  `c8ebe82a55f40fca95036c0555e5280bbe605add`.
- State: revision 108, SHA-256
  `c05a4f9478cf1888a2d721b8e84bb606c331537152dba736a865f1211cc57dc3`; CSH-10
  is `pending`, attempt number 0, with no attempt history.
- Current accepted contract pin: `18783adf1f922fa902215b49a45938ddeea9cba0`;
  it is a reviewed CSH-10 `owned_paths` amendment adding `ask`,
  `_ask/scripts/tracker-config.py`, and `_ask/scripts/launcher-trust.py`.
- The CSH-01–09 TaskResults retain contract SHA
  `ab109ead101e409f8f30b5339cd3ecf2157bf4c6`. Their task state, review
  receipts, integration receipts, and results remain historical records and
  must not be rewritten to the current pin.

## Evidence inventory

- The current execution ledger has 80 rows and SHA-256
  `f526f52796a1e360e8b2c4120171721966a230c83fe1a13459354e484a7da95f`.
  All 80 reports match their ledger digests; all 89 referenced output files
  exist. They were not all present in the `3d33dc9` Git tree. Commit `e889779`
  preserves 279 structured traceability and inner-loop files as one aggregate
  artifact at
  `work/client-security-hardening/inner-loop/evidence/recovery-evidence-bundle.tar.gz`.
  Its sidecar binds SHA-256
  `6605baa865406e1137d66e1add0469cc4a649463535bc132bc6be5dbd5dd6091`, 80
  ledger rows, source tip `19645e8dab1ea615a7df54ab66040a0859ffca53`, state
  digest, and checkpoint ref. The internal 279-file digest manifest and outer
  archive digest were verified before commit. Raw output logs were excluded
  from Git and preserved in a private archive at
  `/home/mohamad/.local/state/askit/recovery/private-raw-logs-20261120T121230Z/raw-logs.tar.gz`
  (directory mode `0700`, archive mode `0600`); it contains all 128 traceability
  `.log` files, including the 89 referenced by execution reports.
- The retained checkpoint contains 77 execution rows. The three later rows
  preserved in the current commit are:
  - `9df29c7a6725452e8824ccb902094a2b`: CSH-10 Red at
    `4a820137941e78c5e3fc8e6eb4667fc60505c02f`.
  - `45a9810a47ca418da3f4d329695a04b6`: CSH-10 Red at the same candidate.
  - `bf2e9bdc52cb4e95b0242d78a4216c59`: workstream final-Green attempt at
    `38fd792c82d1d3b05d8712541067fa97800b36fb`; its aggregate verification
    failed and remains failed evidence.
- The earlier private recovery archive manifest at
  `/home/mohamad/.local/state/askit/recovery/evidence-20261120T025943Z/manifest.json`
  and their archive SHA-256 values verify. Those archives are earlier snapshots,
  but they are not complete backups of the 80-row ledger:
  the primary archive has 47 rows and the candidate archive has 64. The new
  committed structured bundle and private raw-log archive together preserve
  the current evidence without putting raw outputs in source history.
- Frozen runner `98f3c09d958a75c6e78181f196f313a99b4c0379` read-only reconcile
  returned `recovery_required` with these conflicts: runtime traceability
  differs from checkpoint; CSH-10-owned source changed after its coordinator
  SHA while state says pending; and CSH-01–09 TaskResults fail the accepted
  contract carry-forward check.
- The 77 retained execution rows are an exact prefix of the current 80 rows;
  the runner explicitly permits append-only ledger rows. The concrete shared
  carry-forward failure is `traceability/model-state/current.json`: its
  checkpoint digest is
  `facb21ed3d5c01165791d3e42ba1bf4cfdccf3c30200c35f6efe5fc40d3ac374` and its
  live digest is
  `9b8fac461b898082071d0f114f2bf242bdda07600b0206a78efc785d4058f4b4`. The
  frozen validator requires that retained file to remain byte-identical and
  also rejects the subsequently published model-state generation/publication
  files and new `completion.json`, which are outside its allowed-new paths.
  The accepted spec, plan, review, and per-task scope checks pass before this
  traceability predicate. This is a recovery-validator compatibility defect;
  it does not prove the historical TaskResult identities are wrong.

## Source chronology

After coordinator SHA `9c62390`, the branch first accepted the CSH-10 path
amendment (`18783ad`, `4b11b5a`), then committed the CSH-10 fixture repair and
product/documentation work (`4a82013`, `1bfcac8`, `1892407`, `8cb0eee`,
`2ebc362`, `7a72254`, `38fd792`, `3299099`, `1e925ab`, `f97aa1a`). The user
then explicitly authorized confidence-escalation feature work on this branch
(`6400154` authorization, `e8414c4` implementation). Finally, `3d33dc9`
checkpointed the current task and traceability evidence. Preserve this order
and attribution; do not recast all later source as a CSH-10 attempt.

## Proposed treatment

1. Keep state revision 108, coordinator SHA, checkpoint ref, all prior
   TaskResults, reviews, integration receipts, accepted contract identities,
   and all execution rows unchanged. Do not reset HEAD or restore the older
   accepted contract pin.
2. Do not create a CSH-10 attempt from the two historical Red runs, because
   state never recorded those runs as a started attempt. Do not mark CSH-10
   integrated or treat the failed aggregate run as passing.
3. Keep CSH-10 blocked from writer admission until the exact recovery conflicts
   have a history-preserving, independently reviewed transition. Existing
   `reconcile` is read-only, while `reopen` requires an interrupted task with
   attempt history; CSH-10 is pending with neither. `resume` and
   `resume-repair` can reset source and are unsafe here.
4. Do not repair contract identity by editing historical results. The exact
   failed recovery predicate is the checkpoint comparison for valid model-state
   projections described above. Treat that as recovery-tooling work; retain
   the old TaskResults and accepted pins unchanged.
5. The pending-with-zero-attempt state has no supported transition: `reopen`
   requires an interrupted task with attempt history, while `interrupt`
   requires a running task. Astra/high assessed this at 98% confidence and
   recommends preserving state and treating the transition as separate
   recovery-tooling work before any migration. Keep the queued
   milestone-evidence maintenance stopped until this workstream is closed.

## Review and next check

This proposal requires independent review before any state mutation. After
review, run the frozen read-only reconcile check again. Writer admission and
CSH-10 completion remain blocked unless every conflict has a reviewed
resolution.
