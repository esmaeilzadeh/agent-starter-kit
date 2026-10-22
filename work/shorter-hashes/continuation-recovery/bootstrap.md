# Future bootstrap and original-attempt preservation

Normative design for CR-01/CR-06–CR-08; resolves R2. Execute only after an explicit
later implementation direction. Plan sealing registers contracts, not task state.

## Preconditions

`bootstrap-baseline.json` captures state revision/digest and all task records,
prior coordinator SHA, tracked accepted pin and observed authority ref. The
observed ref and tracked pin are separate evidence, not an assertion that they
agreed. Sealing registers a fresh reviewed combined contract while retaining
both historical preimages.

Before bootstrap: clean `agent/shorter-hashes`, no running writer, state matching
the sealed baseline (otherwise reviewed refresh), and registered combined
contract matching the seal. Current HEAD must be the sealed acceptance commit
or an independently reviewed documentation-only descendant. Use that exact HEAD
as CR-1's repair baseline; verify ancestry and supported trusted verifier.

Require normal engineering-model admission before and after the transition. The
current adopted model is v1; its existing compatibility path needs no v2 Task
execution aliases for CR IDs. If schema or captured closure changes, re-evaluate
this precondition rather than bypass admission.

## Combined contract

The sealed canonical graph orders **1 → CR-1 → CR-2 → CR-3 → CR-4 → 2 → … → 10**.
Task 2 gains CR-4 as a scheduling dependency. Original task IDs, scenarios,
assertions, source bindings and classifications remain unchanged. Validate all
original/recovery shared-path ordering together. The supplemental contract is an
inspection view, not a second workstream or separately active accepted-tests ref.

## One initial CAS transaction using existing APIs

No new recovery command is assumed before CR-1. Under normal workflow admission,
the coordinator uses existing `state_transaction`/`cas_apply` for this reviewed
operational transition:

1. Under state lock, recheck exact preimage digest/revision, new contract authority
   and absence of a running writer.
2. Retain a Git-reachable preimage of state, tracked prior pin and distinct prior
   authority object. The source/authority commits are parents of the preimage
   commit; raw state/pin bytes live in its tree. Preserve old coordinator context
   as `suspended_product` and name this preimage in a transition receipt.
3. Add the four standard CR task records. Preserve original Task 1–10 records
   byte-for-value; do not reset old statuses/bases or rewrite their result files.
   Add `repair_context` naming the accepted contract, captured discrepancy,
   original-state identity, allowed CR IDs, suspended product IDs and repair base.
4. In the same transaction mark only CR-1 running with its task-specific
   `base_sha` equal to the approved repair baseline and empty in-place task branch.
   Do not call `spawn_writer` afterward: it overwrites that base with the older
   operational coordinator SHA.
5. Publish an attributed receipt with exact before/after identities. Use a durable
   prepared journal ref containing preimage, expected revision, postimage and
   selected baseline before CAS, then finalize its receipt after CAS. The journal
   owns no task completion authority. Report complete only after durable receipt.

Crash before CAS leaves old state and a prepared journal. Crash after CAS but
before receipt matches the exact recorded postimage and finalizes the receipt
without a second start. Any other state/contract mismatch preserves artifacts
and refuses recovery. This bounded bootstrap interval is recovered by coordinator
operations using existing APIs; CR-2 later adopts its journal into checkpoints.
Use expected-old CAS for journal refs; all source/authority objects are retained.

## Interval before enforcement exists

Existing code does not enforce a newly added `repair_context`. Until CR-1 installs
its guard, it is a reviewed coordinator instruction: only already-running CR-1
may write. Invoke no general `run`/`resume` or other spawn during this interval.
CR-1 then enforces the named repair scope and admits only CR IDs despite the
explicitly isolated legacy discrepancy. Product scheduling remains suspended.
No permit creates historical approval, Red evidence or integration eligibility.

CR-1 still needs actual assertion Red/Green, Refactor, current independent review
and ordinary `integrate_ready`. Existing `read_candidate` pins verification to
task.base_sha, not doc.coordinator_sha. After normal integration the operational
coordinator SHA advances to the repair candidate; the product's old SHA survives
in suspended context. CR-2–CR-4 then use normal repair-restricted scheduling.

## Adoption and handoff

CR-4 audits Tasks 1–5's original sources, authority, runs, reviews and integrations
and emits a reviewed adoption proposal. Apply its final state transition only
after CR-4 integrates. Missing milestones remain unmet; historical Green is not
current integration. Renew necessary checks/review and use normal exact-candidate
FF gates. Required reclassification gets a reviewed amendment; never relabel
merely because a resumed test passes. Keep Tasks 6–10 pending absent evidence.

Retain product suspension after this handoff. A later explicit human endpoint
must authorize product resumption. Registration of this plan and the earlier
completion direction do not override the current stop after sealing.
