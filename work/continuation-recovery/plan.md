# Plan: durable continuation and evidence recovery

Revision 12 is the P0 implementation/test contract for the approved CR-3
recovery package. It retains Revision 10's CR-T38 and CR-T55–57 changes,
checkpoint closure, and CR-T57 ownership. CR-T22 remains mapped only to CR-07.
P0 does not activate the CR-T21 exception; that requires a later reviewed P1
contract binding `cr3-scoped-decision-record.md`. The approved bounded CR-3
coordinator-upgrade correction is recorded in
`cr3-coordinator-upgrade-decision.md`.
Exactly one
requirements contract remains `specs/current/continuation-recovery.json`
(ask-spec/v1, CR-01–CR-08). Human authority: `authorization.md`.
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

## CR-3 P0 evidence and verifier contract

One shared coordinator evidence decision separates original report truth,
current per-case permission, and current-candidate success. The original report,
ledger row, candidate, runner and accepted authority are verified against their
original immutable identities. A reviewed P1 row separately binds applicability
to the current case and explains behavioral continuity; original source and
contract ancestry remains required, while authority-commit ancestry is not.
Only failed mapped behavior-assertion cases in an eligible report receive Red.
Current Green must use the current P1 contract and exact reviewed candidate.
Preflight, completion selection and `checkpoint-run` use this same decision;
preflight derives identities from retained state, is read-only, and never marks
a task milestone.

The coordinator pinned at the original CR-3 base `2c508ff` cannot enforce
P1's per-case continuity table or the narrow T21 declaration. Keep that task
base and every historical runner identity unchanged. The approved scope change
authorizes a bounded, independently reviewed coordinator upgrade for CR-3;
this is a code-path upgrade, not a data migration. P0 implements the selector
and receipt checks in coordinator source `C`, but neither `C` nor verifier
source `V` may run for integration until an exact independent review approves
both and accepted P1 binds their immutable commit/tree identities, the P1
contract digests and the review identity/digest. Normal P1 coordinator
acceptance records that exact binding. Run integration through only reviewed
`C`, which checks that the live accepted P1 binding matches the unchanged task
base and selects only bound `V`. No caller path, ambient value, unreviewed
source, or arbitrary candidate verifier may select executable code. The
integration result binds work/task, unchanged `base_sha`, exact coordinator
`C`, verifier `V`, candidate commit/tree, accepted contract digests, historical
runner identity and P1 binding digest. The selected verifier retains existing
static, semantic, candidate, completion and integration checks. CR-T19 and
CR-T59 exercise this through the real disposable coordinator integration
path; `check-completion` alone is insufficient evidence. Exact source commits
are determined from the P0 implementation candidate and must be recorded and
independently reviewed before P1 acceptance and activation.

## Work breakdown

`inner-loop/tasks.yaml` is the sole executable graph; `test-plan.json` is the
sole test mapping. Shared files are serialized by the dependency chain. One
committing writer uses this repair branch. CR-1 implementation is underway;
its first candidate failed aggregate integration and is not integrated.

| Task | Outcome and owned components | Dependency | Cases | Completion evidence |
| --- | --- | --- | --- | --- |
| CR-1 | Work-ID-scoped reconciliation before admission; state/driver/recovery/CLI, immutable fixture, recovery assertion, and mapped traceability entrypoint modules, shell entry, plus compatibility with existing coordinator reliability and public-entrypoint assertions | none | CR-T01–04,17,22–37,39–54 | Actual assertion Red/Green, Refactor, independent exact review, normal verification/FF integration including the mapped reliability suite; isolated queue admits CR-1 and subsequently CR-2 while product bytes remain unchanged |
| CR-2 | Git-retained checkpoint closure, cache recovery, transfer CLI, explicit attempt interruption/reopen with retained prior plan and run history, scope-aware prior TaskResult validation, and durable attribution of interrupted candidate paths; checkpoint/attempts/state/driver/recovery/CLI | CR-1 | CR-T05–09,18,38,55–57 | CAS/crash/cache and post-FF checkpoint replay assertions, attempt-history replay and explicit reopen, scope-compatible historical result carry-forward, checkpoint-retained interrupted candidate attribution, GC and separate-object-database bundle E2E; real Red/Green, Refactor, review, integration |
| CR-3 | Coordinator finalization and historical evidence recovery; exact receipt lifecycle, read-only preflight, per-case historical Red continuity, exact T21 exception enforcement, and reviewed coordinator/verifier upgrade. CR-T12 is narrowly reclassified as regression while retaining its failed `final_green`; CR-T13 stays new and covers repeated reopen/receipt preservation; CR-T21 stays new in P0. | CR-2 | CR-T10–14,19–21,58–61 | Real task-scoped Red for new P0 behavior; current Green and Refactor; independent review of assertion continuity and exact contract; disposable two-interruption lifecycle through the exact reviewed coordinator/verifier integration path; unchanged original reports, ledger rows, bases, attempts and consumed receipt |
| CR-4 | Legacy reconciliation/adoption implementation and disposable tests; recovery/CLI and immutable fixtures; read-only real audit/proposal under adoption/ | CR-3 | CR-T15–16 | Exact Tasks1–5 provenance audit and independently reviewed adoption proposal; missing evidence honest; product state/authority untouched; real Red/Green, Refactor, review, normal repair integration |

Owned paths are enumerated in the graph. CR-1 creates immutable fixture and test
sources, including the disposable traceability consumer fixture. Commit callable scaffolds with assertions before obtaining behavior Red;
import/setup failure cannot be Red. CR-2 API accepts existing run evidence before
CR-3 automatic finalization exists. No task is a deferred design decision.

## Verification and E2E

All eight criteria map to integration and E2E obligations. Every case has
exactly one responsible task, observable scenarios, exact source paths and
per-criterion assertions. CR-T58–61 each cover a distinct P0 behavior; CR-T13
owns repeated attempt/receipt history while CR-T60 owns receipt request binding
and atomic stale-request refusal. CR-T12's regression classification retains
its failed `final_green` history. T21 remains `new` with all checks mandatory;
P0 has no active TDD exception. Historical Red is retained only under the
case-by-case continuity review in the recovery decision note.

E2E applies: disposable Git repositories, fresh processes, cache loss and process
interruption at publication boundaries. CR-T18 deletes temporary refs, expires
reflogs, prunes and transfers without alternates/hardlinks/shared objects before
revalidating original evidence. CR-T19 exercises actual nested pinned verification
with bounded timeout. CR-T20/21 cover standalone interruption/old runner. CR-T17
starts from the exact immutable blocked ten-task fixture beside a new repair
queue and checks admission/preservation. CR-T16 checks reviewed handoff refusal.

Future checks include the recovery unittest module and shell wrapper, existing
inner-loop/reliability/stage shell suites (the reliability assertion module is
owned by CR-1 so compatibility failures can be corrected without weakening its
assertions), traceability unittest discovery,
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

## P0 acceptance and staged recovery

The submitted decision is recorded in `cr3-scoped-decision-record.md`; the
approved intent remains byte-identical. Review and pin the exact P0 spec,
test-plan and task graph digests through the normal coordinator path. P0
contains no active T21 exception. After P0 acceptance, run the actual
task-scoped test-only Red, implement only mapped behavior, then obtain current
Green and Refactor evidence. Prepare P1 only after P0 implementation is
demonstrated; P1 binds exact historical continuity rows, the approved
decision record/digest, and independently reviewed coordinator/verifier
commit/tree identities with review evidence. Follow `cr3-recovery-decision.md` for the required
preflight, distinct attempt-2-to-3 receipt, reopen, checkpoint, independent
review and normal integration order.

The original product contract, intent, branch ref, runtime and authority remain
unchanged. Product adoption and scheduling remain outside the accepted scope.
