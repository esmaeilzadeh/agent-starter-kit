# Independent P0 contract review request

Workstream: `continuation-recovery`
Task: `CR-3`
Candidate source commit: `a553ef9b81321cfb5e74e596c5c3ff6b347e35db`
Review status: pending; no approval is implied by this request.

## Exact canonical identities

| Contract | Digest |
| --- | --- |
| Accepted spec (`CR-01`–`CR-08`, unchanged) | `02dcf36a73bbaf4c100e413854e823518f14d3dcbed34fe47a333d8e65790cf1` |
| P0 test plan | `bd07e997c4532b686ca09bbb8c32ca4b243b75ef832382e666789b670c6855ec` |
| P0 task graph | `d7f6819c4990f4e416f693ff3a274e92c2b57b7ca78ef04c1c2e58d622d979f5` |

Design file byte digests:

| File | SHA-256 |
| --- | --- |
| `work/continuation-recovery/plan.md` | `48922157ba8f67c47857255c99393b8d5512f411f12035f9a5b6b640fa5f19ca` |
| `work/continuation-recovery/inner-loop/tasks.yaml` | `494b31047cfbfc4cca758cc8effc18218ddc69d2710cfce819a190da0a7aca63` |
| `work/continuation-recovery/test-plan.json` | `0c81523e1bb8f4b483a1d7bce95a1760c92b2ccdf8d056574acbe9743f1403be` |
| `work/continuation-recovery/cr3-scoped-decision-record.md` | `409f38a1120f45f48d6693176e21d0cab93e0107e412614945f09b9c23e44fe8` |
| `work/continuation-recovery/cr3-coordinator-upgrade-decision.md` | `f122bfadb8e009be6f8a79daae58fed3339651edeb899dc7e93aac78ef1e25b4` |

## Review scope

Review this exact candidate commit and all identities above. The prior independent review at `fff72663f723ac177eabc7cef4761bcce62b8c99` requested changes because the original-base coordinator at `2c508ff` could not select a newly authorized verifier. The human has now approved the narrowly scoped correction recorded in `cr3-coordinator-upgrade-decision.md`; the original task base and historical runner identities must remain unchanged.

Confirm the revised P0 plan specifies a secure bootstrap: coordinator source `C` and verifier source `V` are independently reviewed, accepted P1 binds their exact commit/tree identities, P1 contract digests, and review identity/digest, normal coordinator acceptance stores that exact binding, and only reviewed `C` can select bound `V` after checking the unchanged base. Ensure neither can execute before review and P1 acceptance, and integration output binds coordinator, verifier, base, candidate/tree, contracts, runner and P1-binding digest. Reject any design that derives trust from an arbitrary candidate path, ambient value, or candidate commit alone.

Also reconfirm:

1. CR-T12's narrow regression reclassification retains failed `final_green`; CR-T11/14 retain accepted classifications.
2. CR-T13 repeated attempt-history behavior is distinct from CR-T60 receipt request identity and stale-request atomic refusal.
3. CR-T58 cannot activate an exception in P0 and confines P1 to the approved `continuation-recovery` / `CR-3` / `CR-T21` decision while preserving all T21 checks and current Green.
4. CR-T59 covers original/P0 per-case Red applicability, current Green, coordinator `checkpoint-run`, and normal integration without rewriting old report, ledger, authority, runner, or task-base identities.
5. CR-T61 is read-only, derives identities from retained state, and uses the shared evidence validator. New selectors have one task, exact source paths, and criteria/types satisfying the accepted spec.

P0 validation completed after this contract revision: `./ask inner-loop validate continuation-recovery` returned `ok`; `./ask traceability validate-plan continuation-recovery --revision HEAD` returned valid contracts with no violations. These are coordinator/static checks, not independent review or behavior execution.

Return a separate review record bound to this candidate and all three canonical digests, with `APPROVED` or `REQUEST CHANGES`, findings, and reviewer identity. Do not execute task behavior, accept P0, activate T21, or mutate CR-3 runtime state as part of this planning review.
