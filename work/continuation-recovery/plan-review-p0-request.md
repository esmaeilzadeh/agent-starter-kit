# Independent P0 contract review request

Workstream: `continuation-recovery`
Task: `CR-3`
Candidate source commit: `ce00e4d9ed24e860a6cba172804bb5c8d5c5dce0`
Review status: pending; no approval is implied by this request.

## Exact canonical identities

| Contract | Digest |
| --- | --- |
| Accepted spec (`CR-01`–`CR-08`, unchanged) | `02dcf36a73bbaf4c100e413854e823518f14d3dcbed34fe47a333d8e65790cf1` |
| P0 test plan | `22bd36b5bc41f89038e26bcfcd11685987b410dbb94d71aac805f33d47d77cbe` |
| P0 task graph | `d7f6819c4990f4e416f693ff3a274e92c2b57b7ca78ef04c1c2e58d622d979f5` |

Design file byte digests:

| File | SHA-256 |
| --- | --- |
| `work/continuation-recovery/plan.md` | `cdfe5e4deff0c879a325d8960225d0db36b67ee1e52375b075ab21299271e475` |
| `work/continuation-recovery/inner-loop/tasks.yaml` | `494b31047cfbfc4cca758cc8effc18218ddc69d2710cfce819a190da0a7aca63` |
| `work/continuation-recovery/test-plan.json` | `1f98b1298b5b11d0fc78ea1655e5eda1b21952786792cd4c31d692f0c7ffffed` |
| `work/continuation-recovery/cr3-scoped-decision-record.md` | `409f38a1120f45f48d6693176e21d0cab93e0107e412614945f09b9c23e44fe8` |

## Review scope

Review the exact candidate commit and the files/digests above. In particular:

1. Confirm CR-T12's narrow regression reclassification retains its failed
   `final_green`, while CR-T11/14 retain their accepted classifications.
2. Confirm CR-T13's two-interruption history behavior is distinct from CR-T60's
   receipt request identity and stale-request atomic refusal.
3. Confirm CR-T58 cannot activate an exception in P0 and confines the P1
   declaration to the approved `continuation-recovery` / `CR-3` / `CR-T21`
   decision record, while preserving all T21 checks and current Green.
4. Confirm CR-T59 covers original/P0 per-case Red applicability, current Green,
   coordinator `checkpoint-run`, and normal integration with a verifier
   migration binding, without rewriting old report, ledger, authority, runner,
   or task-base identities.
5. Confirm CR-T61 is read-only, derives its identities from retained state, and
   uses the shared evidence validator. Confirm the new selectors have one task,
   exact source paths, and criteria/types that satisfy the accepted spec.
6. Confirm the verifier migration design preserves base `2c508ff`, authorizes
   the exact reviewed verifier source through P1, has coordinator-owned
   selection, and binds base, candidate/tree, contract, runner and migration
   receipt in integration output. The implementation commit identity will be
   populated from the exact P0 implementation candidate in P1; review whether
   that binding is sufficiently constrained by P0 acceptance and independent
   candidate review.

P0 validation completed: `./ask inner-loop validate continuation-recovery`
returned `ok`; `./ask traceability validate-plan continuation-recovery
--revision HEAD` returned valid contracts with no violations. Structural checks
confirmed unique case IDs and exact one-to-one task-scope membership. These are
coordinator/static checks, not an independent review or behavior execution.

Return a separate review record bound to this candidate and all three canonical
digests, with `APPROVED` or `REQUEST CHANGES`, findings, and its own reviewer
identity. Do not execute task behavior, accept P0, activate T21, or mutate CR-3
runtime state as part of this planning review.
