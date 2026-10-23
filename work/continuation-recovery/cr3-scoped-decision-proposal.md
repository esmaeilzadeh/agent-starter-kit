# CR-3 scoped decision proposal

Status: draft for one human scope decision. This file is not an accepted
contract, an `accept-plan` receipt, a T21 authorization, or permission to
change source/runtime state. It supplements
[`cr3-recovery-decision.md`](cr3-recovery-decision.md); that decision note
controls if any wording here differs.

## Decision requested

Approve the bounded CR-3 recovery package below, including the narrow T21
evidence exception proposal and the verifier compatibility migration. Approval
authorizes preparation and execution only through the phase gates in the
decision note. It does not itself activate T21: activation still requires the
exact decision artifact to be bound into the independently reviewed P1
contract and accepted by the coordinator. Decline or request changes leaves
CR-3 interrupted and blocks dependent contract/source/runtime changes.

The accepted What, Why, assumptions, and product scope in `intent.md` remain
unchanged. No CR-1/CR-2 reopening, product runtime mutation, broad TDD waiver,
synthetic Red, or change to the original task base is included.

## P0 implementation contract draft

Prepare a P0 plan/test-plan/graph revision while CR-3 is interrupted. P0
authorizes tests and implementation only; T21 remains `new` and has no active
exception. It includes these case treatments:

| Existing case | P0/P1 treatment |
| --- | --- |
| CR-T10 | Preserve original Red only for its demonstrated finalization failure; independently review behavioral continuity; add current Green and observer sensitivity evidence for `afc7ab2`. |
| CR-T11, CR-T14 | Retain the already accepted regression classifications. |
| CR-T12 | Apply the supported narrow regression reclassification and retain its failed `final_green` history. |
| CR-T13 | Preserve earlier passing history; add a real assertion Red for repeated-reopen/consumed-receipt selection before implementing that repair. Do not duplicate the same outcome as another selector. |
| CR-T19 | Preserve applicable original and attempt-2 Red per case; assess behavioral continuity; obtain current Green. |
| CR-T20 | Preserve the original Red only for mapped behavior that remains applicable; obtain current Green. |
| CR-T21 | Remain `new`; retain every behavioral check and report the historical Red gap honestly. |
| Proposed recovery selectors | Allocate only after checking IDs: receipt lifecycle, read-only preflight, T21 exception enforcement, historical-Red continuity/finalization, and T10 observer sensitivity. Each selector maps to one existing criterion/task and exact source paths. |

The proposed CR-T58–61 labels are not reserved. Resolve any overlap with
CR-T13 and confirm identifiers against the canonical test plan before P0
acceptance. New selectors must test distinct outcomes and cannot be filtered
out of a claimed full-scope run.

P0 requires real task-scoped Red from behavior assertions on test-only
candidate code, then implementation, Green, Refactor, and exact-candidate
review. Setup/import/collection failures do not qualify as Red. The P0
acceptance contains no T21 exception declaration.

## P1 historical-evidence and exception draft

P1 retains all P0 selectors and adds an explicit per-case historical evidence
applicability table. Each row binds the original run, task/scope/phase,
candidate, report bytes and canonical digest, ledger-row digest, original
authority/contract, original/current assertion-source identities, and an
independent behavioral continuity decision. The reviewer explains what the
original failure proved, how the current assertion covers that behavior, and
which newly added behavior remains outside the historical evidence. Statement
or AST equality is not an eligibility rule; fingerprints may be diagnostic
only. Original source/contract ancestry and immutable objects remain validated;
authority-commit ancestry is not required.

The current-case inventory is the one in `cr3-recovery-decision.md`: T10,
T19, and applicable T20 original failures; eligible P0 Red for newly added
behavior; and no invented Red for T21. Per-case validation must preserve the
original run identity, allow only failed behavior-assertion cases in a failed
report to receive Red, and retain current P1 Green as a separate requirement.
Preflight, completion selection, and coordinator `checkpoint-run` use the
same validator. A read-only preflight never creates a milestone.

The only proposed exception is `historical-red-unavailable` for the exact
`continuation-recovery` / `CR-3` / `CR-T21` declaration. Its P1 declaration
binds this submitted decision artifact and digest, names the missing historical
Red, and keeps all mapped behavior checks plus current Green mandatory. The
runtime reports “historical Red unavailable / approved exception”; it must
not fabricate a Red-to-Green transition. Any other workstream, task, case,
P0 plan, or exception kind is rejected. Existing exemption kinds retain their
current meanings.

The decision artifact digest is computed only after this exact content is
approved and recorded. P1 review and coordinator acceptance must bind that
digest; a preselected choice or this draft alone has no authority.

## Verifier compatibility proposal

The existing trusted path cannot express this package at base
`2c508ff`: `snapshot_runner` in `_ask/scripts/inner_loop/evidence.py` snapshots
`.agents/ask/verification/` from the task base, and that verifier's
`reports()` selects only executions whose spec and plan digests equal the
current contract. Its supported exemption set also lacks the proposed narrow
historical-Red-unavailable declaration. Changing `base_sha`, rewriting old
reports, trusting candidate verifier code, or ignoring the pinned-verifier
receipt is excluded.

P0 must therefore implement and test an explicit verifier migration seam:

1. Keep the attempt/task `base_sha` and all historical runner identities
   unchanged. Add a coordinator-owned migration authorization record naming
   the migration kind, immutable verifier source revision and tree/digest,
   independent review artifact/digest, accepted P0/P1 contract identities,
   and the exact work/task scope.
2. Select that verifier only through the authorization record validated by
   coordinator code pinned at the original base. Never select a verifier by a
   caller-provided path, candidate content, or ambient environment variable.
3. Require the migrated verifier to retain all existing static, semantic,
   candidate, completion, and integration checks. Its output binds the
   unchanged task base, exact candidate SHA/tree, work/task IDs, accepted
   contract digests, runner identity, and migration authorization digest.
4. In the disposable end-to-end scenario, prove normal integration actually
   invokes the authorized verifier revision and rejects a stale/mismatched
   authorization, candidate, base, contract, or output receipt. Unit tests or
   `check-completion` alone do not satisfy this boundary.

The P0 contract must name the exact implementation and test paths for this
seam after reviewing the current module boundaries. At minimum, evaluate
`_ask/scripts/inner_loop/evidence.py`, the inner-loop coordinator CLI, and the
`.agents/ask/verification/traceability/` contract/evidence/completion/service
modules; list only paths actually needed. Add exact helper and fixture paths
to CR-3 ownership before P0 acceptance. If a safe verifier source cannot be
authorized without changing the task base or weakening the existing trust
boundary, stop and present that concrete contradiction for a new decision.

## Required scope and evidence

The exact accepted P0/P1 drafts will include source ownership, selector-to-case
mapping, verifier migration authorization, the case inventory above, and the
phase order from `cr3-recovery-decision.md`. The disposable lifecycle must
cover two interrupted attempts, the consumed receipt, P0 Red, P1 authorization,
current Green, read-only preflight, a distinct reviewed attempt-2-to-3 receipt,
real coordinator reopen/checkpointing, independent exact-candidate review,
and normal integration through the authorized verifier.

Preserve old report bytes, ledger rows, bases, authorities, attempts, and
receipt. Reject altered/undeclared evidence, wrong-task/case use, invalid
authority, stale requests, and failed preflight without publishing state. Keep
T10/T20 original scope limited to the actual failures and prove T10 observer
sensitivity in a disposable negative control.

Only the following is authorized before this decision is submitted: read-only
inspection and drafting in proposal files. Active `plan.md`, `test-plan.json`,
`tasks.yaml`, accepted refs, source, receipts, state, reports, and ledgers remain
unchanged. After submission, follow P0 → new-slice Red → P0 implementation →
P1 → current Green/preflight → reviewed reopen → finalization/review/integration
in the order and with the stop conditions in `cr3-recovery-decision.md`.
