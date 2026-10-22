# Plan: durable continuation and evidence recovery

Revision 3. Exactly one requirements contract: `specs/current/continuation-recovery.json`
(ask-spec/v1, CR-01–CR-08). Human authority and stop: `authorization.md`.
Explore skipped: destination already clear. This is continuation of the authorized
planning interrupt, isolated on the selected base, not a new product request.

## Decisions and affected components

`checkpoint-design.md` and `bootstrap.md` are normative design inputs. They
resolve all R1–R4 findings in `plan-review-reevaluation.md`.

- R1: checkpoint commits retain every required source/base/candidate, runner,
  contract and historical authority commit through parent edges, and artifact
  bytes through their tree. Validate closure before CAS publication; transfer
  a self-contained bundle into an independent object database after fixture GC.
  Retained historical authority never becomes current acceptance implicitly.
- R2: use normal existing initialization of a separate four-task repair queue;
  legacy records never receive CR IDs. Work-ID-scoped recovery permits normal
  CR-1 then CR-2 admission. CR-4 produces an exact reviewed legacy audit/adoption
  proposal; real product integration/adoption and scheduling need later direction.
- R3: adapters/pinned children write data only. The coordinator finalizes after
  child exit, reusing its held transaction lock where nested. It repairs complete
  interrupted ledger insertion idempotently before checkpointing. The trusted
  `.agents/ask/verification/` snapshot acquires no new checkpoint dependency.
  Pre-hook verifier output has an explicit compatibility/migration boundary.
- R4: each case binds exact production, fixture and assertion files. Operational
  state is fixture/output evidence, never a source binding; no glob source paths.

## Work breakdown

`inner-loop/tasks.yaml` is the sole executable graph; `test-plan.json` is the
sole test mapping. Shared files are serialized by the dependency chain. One
committing writer uses this repair branch. Implementation has not begun.

| Task | Outcome and owned components | Dependency | Cases | Completion evidence |
| --- | --- | --- | --- | --- |
| CR-1 | Work-ID-scoped reconciliation before admission; state/driver/recovery/CLI, immutable fixture and assertion modules, shell entry | none | CR-T01–04,17 | Actual assertion Red/Green, Refactor, independent exact review, normal verification/FF integration; isolated queue admits CR-1 and subsequently CR-2 while product bytes remain unchanged |
| CR-2 | Git-retained checkpoint closure, cache recovery, transfer CLI; checkpoint/state/recovery | CR-1 | CR-T05–09,18 | CAS/crash/cache assertions, GC and separate-object-database bundle E2E; real Red/Green, Refactor, review, integration |
| CR-3 | Coordinator finalization for standalone/nested and old pinned verifier; checkpoint/state/recovery/driver/evidence/CLI, adapter/traceability CLI and protocol/docs projections | CR-2 | CR-T10–14,19–21 | Bounded real pinned verification, interrupted report/ledger finalization, old-base runner compatibility; real Red/Green, Refactor, review, integration |
| CR-4 | Legacy reconciliation/adoption implementation and disposable tests; recovery/CLI and immutable fixtures; read-only real audit/proposal under adoption/ | CR-3 | CR-T15–16 | Exact Tasks1–5 provenance audit and independently reviewed adoption proposal; missing evidence honest; product state/authority untouched; real Red/Green, Refactor, review, normal repair integration |

Owned paths are enumerated in the graph. CR-1 creates immutable fixture and test
sources. Commit callable scaffolds with assertions before obtaining behavior Red;
import/setup failure cannot be Red. CR-2 API accepts existing run evidence before
CR-3 automatic finalization exists. No task is a deferred design decision.

## Verification and E2E

All eight criteria map to integration and E2E obligations, 21 new behavior cases
and one supported unittest runner. Every case has exactly one responsible task,
observable scenarios and per-criterion assertions. All require actual assertion
Red in future implementation; inherited product runs are never relabeled.

E2E applies: disposable Git repositories, fresh processes, cache loss and process
interruption at publication boundaries. CR-T18 deletes temporary refs, expires
reflogs, prunes and transfers without alternates/hardlinks/shared objects before
revalidating original evidence. CR-T19 exercises actual nested pinned verification
with bounded timeout. CR-T20/21 cover standalone interruption/old runner. CR-T17
starts from the exact immutable blocked ten-task fixture beside a new repair
queue and checks admission/preservation. CR-T16 checks reviewed handoff refusal.

Future checks include the recovery unittest module and shell wrapper, existing
inner-loop/reliability/stage shell suites, traceability unittest discovery,
`./ask sync`, task-scoped traceability runs and normal `./ask verify` integration.
Runtime sources do not yet exist; mapping denotes planned exact identities, not
present execution. The shell wrapper joins existing aggregate discovery.

Planning checks use graph/contract validators only, canonical digests, case
ownership, exact source-path syntax and supported runner filtering. No behavior
suite or aggregate `./ask verify` runs at this endpoint because it would execute
production behavior and falsely conflate planning with implementation evidence.
No implementation `record-result pass` or workstream acceptance is claimed.

## Dependencies, risks and escalation

Existing coordinator CAS, authority, v1 model admission, exact-candidate review,
trusted verifier and FF-only integration stay required. Storage grows with
retained proof; cooperative refs/locks are not hostile-writer authentication.
Historical tracked pins/observed authorities may differ and remain observations.
Changed requirements, ownership, runner capability, schema, closure or unsupported
recovery transition require spec-change and independent review before execution.
Stale product preimages require refreshed audit; no broad repair bypass applies.

## Seal and explicit stop

Commit corrected contracts/design; obtain fresh independent review bound to
canonical spec/plan/graph digests and exact design-file identities. Register
only `continuation-recovery` using existing `traceability accept-plan`, commit
the generated pin and durable `plan-seal.md`, and read back authority/digests.
The original product contract, intent, branch ref, runtime and authority remain
unchanged. STOP after sealing. Implementation, runtime initialization/bootstrap,
product adoption and scheduling require later explicit human authorization.
