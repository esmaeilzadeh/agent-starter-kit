# Plan: durable continuation and task evidence recovery

Revision 2. Requirements: `spec-change.md` and standard-schema `spec.json`,
CR-01–CR-08. Final sealed status, artifact identities and coordinator registration
are recorded in `plan-seal.md` after fresh independent approval.

## Endpoint and contract

Human direction: apply all review changes, seal the plan, then stop. Register
the reviewed combined planning contract; implementation and runtime bootstrap
require a later explicit direction. Preserve approved product intent bytes.

Supplemental `test-plan.json` and `tasks.yaml` define four repair tasks. Canonical
`specs/current/shorter-hashes.json`, `work/shorter-hashes/test-plan.json` and
`work/shorter-hashes/inner-loop/tasks.yaml` combine unchanged 18 product criteria
and 39 product cases with the recovery requirements/cases. Combined ordering is
**1 → CR-1 → CR-2 → CR-3 → CR-4 → 2 → … → 10**. Task 2's added dependency changes
scheduling, not historical attempt identity. Planning registration initializes
no task state and claims no execution.

## Fixed design decisions

`checkpoint-design.md` and `bootstrap.md` are normative inputs. They resolve
review R1–R3 before sealing, rather than deferring architectural choices.

- Checkpoint commits retain required source/base/candidate and historical
  authority commits through real parent edges; the tree stores actual evidence
  bytes. Export a complete bundle and validate it in a separate object database.
- The future reviewed bootstrap uses one existing coordinator CAS mutation to
  preserve original tasks, add repair tasks and start only CR-1 at its approved
  separate baseline. The initial suspension permit is a coordinator instruction
  until CR-1 implements enforcement. It is not an existing mechanical guard.
- Adapters and pinned children publish data only. The coordinator finalizes
  checkpoints after children exit; transaction-internal code reuses its held
  lock. No child acquires the parent state lock or imports new checkpoint code.
- Each test binds exact production, fixture and assertion source files. No
  source-path glob or mutable operational state is an immutable source binding.

## Work breakdown

One branch and committing writer. Supplemental and combined graphs share the
four CR IDs; combined CR-1 additionally depends on already integrated Task 1.
Exact ownership is in `tasks.yaml`; module summaries below have the same scope.
Shared files are deliberately serialized by the dependency chain.

| Task | Outcome | Depends on | Owned components | Planned cases | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| CR-1 | Reconcile before admission and enforce reviewed repair context | none supplemental; 1 combined | state/driver/recovery/CLI; recovery assertions/fixture; shell entry | CR-T01–CR-T04, CR-T17 | Real assertion Red/Green; blocked-shape bootstrap test; original attempts preserved; Refactor; exact independent review; normal verification/FF integration |
| CR-2 | Retain full checkpoint object/evidence closure and recover cache | CR-1 | checkpoint/state/recovery/CLI; recovery assertions/fixture | CR-T05–CR-T09, CR-T18 | Crash/CAS/cache tests; GC/non-shared transfer E2E; real Red/Green; Refactor; independent review and normal integration |
| CR-3 | Finalize standalone/nested milestones in coordinator without verifier trust changes | CR-2 | checkpoint/state/recovery/driver/evidence/CLI; traceability CLI/adapter publication; protocol/docs/generated projections; recovery assertions/fixture | CR-T10–CR-T14, CR-T19–CR-T21 | Real run/ledger interruption tests; bounded nested verification; pre-hook runner compatibility; current independent review and normal integration |
| CR-4 | Audit/adopt old attempts and produce exact recovery handoff | CR-3 | legacy adoption in recovery/CLI, assertions/fixture; workstream audit/state/result/evidence and reviewed contract amendment artifacts | CR-T15–CR-T16 | Legacy fixture assertions; reviewed Tasks 1–5 audit; original identities/missing milestones preserved; transfer/reload; product suspension |

CR-1 creates immutable fixture definitions before subsequent tasks use them.
Tests bind modules available within their task or predecessors. Commit assertion
sources and minimal callable scaffolds before obtaining observable behavior Red;
never use import/setup failure as Red. CR-2's API can explicitly accept existing
run evidence; automatic coordinator finalization belongs to CR-3. CR-4 tests
exercise the existing recovery API with historical fixture data, alongside the
real audit/adoption report. New outcomes or paths require reviewed amendment.

## Tests and verification

The supplemental contract uses current `ask-spec/v1`, `ask-test-plan/v1` and
TaskGraph schemas: 21 planned cases, one supported unittest runner, observable
scenarios, per-criterion expected assertions and exactly one task per case.
All eight recovery criteria require integration and E2E evidence. CR-T17–CR-T21
cover the actual bootstrap, Git retention, nested verifier, standalone publication
and old pinned-runner boundaries introduced by review. All recovery cases test
new behavior requiring genuine assertion Red. Original product classifications
remain unchanged; no historical run is relabeled.

Future implementation checks:

```bash
PYTHONPATH=_ask/scripts python3 -m unittest _ask.tests.inner_loop_recovery
bash _ask/tests/test-inner-loop.sh
bash _ask/tests/test-inner-loop-reliability.sh
bash _ask/tests/test-stages-inner-loop.sh
python3 -m unittest discover -s _ask/tests -p 'test_traceability*.py'
./ask sync
./ask verify
```

The new shell wrapper joins existing aggregate shell-test discovery. Keep CAS,
stale review, candidate drift, FF interruption, model admission and source repair
regressions. Run workflow-reference publication checks if those locks change.
Use task-scoped traceability runs and normal coordinator integration; shell exit
alone is not mapped evidence. Record actual candidate/source/assertion continuity.

During planning, use existing graph/contract validators on supplemental and
combined contracts; check case uniqueness/ownership, exact paths, task module
availability, unchanged product cases/criteria and combined serialization. Planned
entry points do not constitute execution. Do not manufacture runtime passes to
seal a plan.

## E2E and migration

Applies. Use disposable repositories, real test assertions, fresh processes,
ignored-cache removal and process death at publication boundaries. The retention
case deletes temporary fixture refs, expires reflogs, prunes and transfers a
bundle into a separate object database. Nested verification uses a real trusted
snapshot and bounded timeout. The first hook-adding candidate is also tested
against its pre-hook verifier base. Bootstrap starts with the actual blocked
ten-task shape and adopted v1 model. No network/production datastore is needed;
cleanup affects fixture resources only.

Audit original Tasks 1–5: source and assertion continuity, authority versions,
Red/Green, reviews and integration receipts. Approval at `0d9089f` is historical,
not current-candidate approval. Retain valid proof and renew only unmet/stale
milestones. Tasks 6–10 remain pending absent independent evidence. CR-4 produces
a reviewed adoption proposal; apply it only after CR-4 integrates and retain
product scheduling suspension until explicit human authorization to resume it.

## Risks and escalation

- Historical authority retention is not current approval. Capture differing
  old tracked/authority pins separately; plan registration validates no old run.
- Cooperative local Git refs/locks provide neither hostile-writer authentication
  nor distributed consensus. Existing current-contract eligibility still applies.
- Retention grows Git storage; report sizes and preserve required proof.
- New writer, state drift, model/schema/closure drift or changed contract makes
  bootstrap preconditions stale and requires reviewed refresh.
- Changed behavior, ownership or unsupported recovery transitions require a new
  exact independent review before implementation proceeds.

## Seal and stop

Record the user's explicit sealing direction and obtain an independent decision
bound to exact supplemental/combined contracts, this plan and its design inputs.
Commit the contract source. Preserve old authority provenance, then register the
reviewed combined contract with existing `./ask traceability accept-plan`.
Commit its generated acceptance pin and final `plan-seal.md`; read back the
registered contract/digests without scheduling a task. Stop on a clean branch.
The planning seal authorizes no implementation or runtime bootstrap.
