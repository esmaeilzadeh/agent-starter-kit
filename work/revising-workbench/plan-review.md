# Partial independent plan review

Status: INCOMPLETE. Coordinator record of observations reported by the independent
`gpt-6-astra` / high reviewer `/root/review_revising_plan`. Reviewed source:
`5fc3ac8f5cc6490b441fe31e318e887d9a16ba05`. The reviewer reached its usage limit
before writing a final report or decision. No APPROVED or REJECTED final verdict,
accepted contract or implementation authority is claimed by this record.

## Reported findings to address

1. Existing regression selectors use `_ask.tests.*`, but their modules import
   bare `engineering_fixture` / `traceability_fixture`. The declared root-level
   unittest invocation does not put `_ask/tests` on the import path. The reviewer
   reproduced collection errors for model, guard, CLI and evidence tests. Use
   supported discovery with the correct collected identities and map every case
   collected by each runner; avoid ambient imports from outside the candidate.
2. `RWB-PASSAGE-ACTIONS`, assigned to RWB-102, requires association, migration and
   representative entrypoints introduced by RWB-103/RWB-108. Earlier tasks cannot
   reach their required final green before successors exist. Assign each real
   entrypoint case to the task that introduces it, retaining complete final
   coverage without future-entrypoint stubs or weakened assertions.
3. The proposed canonical `flow_mappings` registry requires references to cases
   inside its containing plan to embed that plan's digest. Inserting the digest
   changes the plan and therefore its digest. Derive local case identity from the
   enclosing reviewed plan; bind mapping-body review without self-reference.
   External case references can retain explicit immutable target-plan digests.

## Boundary

These observations concern planning mechanics and can be corrected without
changing the passed revision-2 specification. The human requested that work stop
after the plan is revised. Record structural/collection validation and the exact
revision result; a completed independent review and contract pin remain pending
before implementation. The earlier Spec Challenge PASS remains about its original
unchanged specification inputs, not this unfinished planning review.

## Revision recorded by the coordinator

The three observations are addressed in planning source commit
`e0dead38a1e06fafe536f27461b558876d429e7e`: four candidate-local baseline discovery
runners; passage cases assigned to the introducing tasks; and local flow selectors
whose identity comes from the enclosing reviewed plan, without recursive hashes.
Graph/coverage/scope checks passed for nine tasks, 56 cases and 38 runners. Isolated
collection matched all 22 existing regression cases without executing test methods.
This records the revision and its checks, not an independent final verdict.
Per the human's instruction, stop after revision; further review and pinning remain
pending before implementation.
