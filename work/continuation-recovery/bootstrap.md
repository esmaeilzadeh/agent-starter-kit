# Separate repair initialization and later legacy adoption

Normative design for CR-01/CR-06–CR-08; replaces the former combined-queue
bootstrap. Execute only after later explicit implementation authorization.

## Repair startup before CR-1

The repair uses `agent/continuation-recovery` from the human-selected current
product branch at d04b3a4, but its work ID, canonical spec, accepted-tests authority,
TaskGraph and runtime directory are exclusively `continuation-recovery`.
The graph is CR-1 → CR-2 → CR-3 → CR-4. There is no task insertion into the legacy
queue, no rewrite of its coordinator SHA and no new repair permit bypassing guards.

After later authorization, ensure a clean repair checkout, valid intent approval,
engineering-model admission and exact sealed authority. Use existing normal
coordinator initialization (`cas-init`/normal scheduler) for this new work ID.
Initialize all four repair task records at the reviewed repair source baseline;
use ordinary `spawn-writer` and one writer. CR-1 then uses genuine assertion
Red/Green, Refactor, exact independent review and ordinary verification/FF
integration. CR-2 admission follows that integration through normal dependencies.
Inherited `work/shorter-hashes` evidence is a distinct work ID and is not repair
history; CR-1's recovery guard reconciles within the selected work ID, never by
unscoped repository-wide task-ID matching. Real discrepancies within repair
history still block. The retained legacy snapshot is read-only input.

No initialization is performed to seal this plan. Original product state revision
11 (Task1 integrated, Task2 blocked, Tasks3–10 pending), task results, evidence,
accepted-tests ref and agent/shorter-hashes remain unchanged. Snapshot fields
for tracked prior pin and observed authority are observations, not retroactive
approval. The existing v1 engineering model admission applies; a missing runner
capability or incompatible model requires migration, never a bypass.

## CR-4 deliverable and reviewed integration handoff

CR-4 implements legacy reconciliation/adoption support and tests it in disposable
repositories. On this branch it creates a read-only audit/proposal under
`work/continuation-recovery/adoption/`, covering original Tasks1–5 sources,
original bases/candidates, assertion continuity, Red/Green, Refactor, reviews,
contract/authority versions, FF ancestry and receipts. Tasks6–10 remain pending
unless independently proven otherwise. Record each first unmet valid milestone;
source presence, commit messages or Green alone never establish completion.

The proposal records exact product branch HEAD, state revision/raw digest,
original task records/results/evidence digests, current and historical authority
identities, accepted graph/spec/test digests, available object closure, supported
schema/model/verifier and absence of a writer. Preserve differing pin/ref values
explicitly. Propose per-task preservation or renewed evidence without changing
classifications, IDs or acceptance requirements implicitly. Missing proof is
reported missing. A reviewer must approve the exact proposal before adoption.

Real product integration/adoption is a separate later authorization, outside
both this seal and automatic CR-4 execution. The human must authorize bringing
the completed repair into the product branch under the branch policy and approve
the adoption scope. Integration must preserve original source/attempt ancestry;
if FF integration is unavailable, obtain an explicit integration decision rather
than rebase/cherry-pick task evidence. Revalidate the exact product preimages,
current authority, clean tree, no writer and trusted upgraded verifier before
any mutation. Stale inputs require refreshed audit and independent review.

The later adoption command uses the new checkpoint transaction machinery under
product state.lock: retain a Git-reachable preimage and full source/authority
closure, validate reviewed postimage, CAS-publish a checkpoint, then replace
cache. Before publication the old state wins; after publication replay only the
exact postimage. Preserve every prior attempt as history; renew stale milestones
through explicit new attempts. No unverified task is labeled integrated and no
product task is spawned by adoption. A durable attributed receipt binds before,
after, proposal, reviewer and checkpoint identities. Product scheduling remains
stopped until separately authorized. CR-T17 rehearses separate admission; CR-T15/16 cover adoption preservation
and exact preimage/adoption refusal boundaries.
