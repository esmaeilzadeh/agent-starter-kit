# CR-3 coordinator-upgrade decision record

Date: 2026-10-23
Workstream: `continuation-recovery`
Task: `CR-3`

Human choice: **Approve upgrade**.

The user approved the exact trust-boundary correction in
`cr3-coordinator-upgrade-scope-change.md`, SHA-256
`dc00da7bb74eaae600afa542379796162a7c426d5d34adc48a454275a7ae0035`, together
with the complete revised intent now in `intent.md`.

The decision authorizes a one-time, independently reviewed coordinator
upgrade for `continuation-recovery` / `CR-3` to select only the exact verifier
commit/tree bound into accepted P1. It preserves original task base
`2c508ff`, historical report/ledger/authority/candidate/runner identities, all
normal static/semantic/candidate/completion/integration checks, and the narrow
T21 exception conditions from the earlier CR-3 decision. It does not authorize
arbitrary candidate verifier code, product runtime changes, product adoption,
or product scheduling.

This decision authorizes the revised trust assumption and scoped plan amendment.
The coordinator upgrade and verifier remain inactive until P0 Red/Green/Refactor,
exact independent source review, exact P1 contract review, and normal coordinator
acceptance bind their immutable identities. T21 remains inactive until P1
acceptance and still requires all behavioral checks and current Green.
