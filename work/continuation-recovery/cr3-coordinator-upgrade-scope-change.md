# CR-3 coordinator-upgrade scope-change proposal

Date: 2026-10-23
Status: proposed; no new authorization is implied.

This proposal addresses the single blocking finding in
`traceability/plan-review-p0-review.md`. It amends the already approved
`cr3-scoped-decision-proposal.md` only at the trusted-verifier bootstrap
boundary. It does not repeat or broaden the approved recovery scope.

## Reproduced contradiction

The approved proposal requires migration authorization to be validated by
coordinator code pinned at original base `2c508ff`. The independent reviewer
verified that `_ask/scripts/inner_loop/evidence.py::verify_candidate` at that
base always snapshots `.agents/ask/verification/` from `identity['base_sha']`
and has no migration authorization or alternate verifier selector. Its
traceability implementation also cannot express per-case historical Red
continuity or the T21 exception. No existing original-base capability can
enforce the accepted P1 semantics through normal integration.

An authorization receipt understood only by newly changed coordinator code
cannot satisfy the requirement that the unchanged original-base coordinator
validate it. P0 remains unaccepted until this trust-boundary correction is
authorized and the amended contract receives a fresh exact review.

## Proposed bounded trust-boundary correction

Authorize a one-time, independently reviewed coordinator upgrade for
`continuation-recovery` / `CR-3` to select the P1-authorized verifier revision.
The task's original `base_sha` remains `2c508ff`; all original report, ledger,
accepted-authority and historical runner identities remain unchanged. This
decision changes which reviewed coordinator source is trusted to run the
integration migration. It does not authorize arbitrary candidate verifier
code.

Use the following selection and authorization protocol:

1. P0 continues to define tests and implementation only. It must not activate
   the T21 exception or authorize runtime reopening.
2. Implement the coordinator migration selector under the exact CR-3-owned
   paths. After P0 Red/Green/Refactor, commit the complete candidate as
   coordinator source revision `C`. Independently review `C`, including the
   selector, verifier source and the integration receipt checks. The review
   binds the exact commit/tree, source digests, P0 contract, original task base
   and all changed behavior.
3. Prepare P1 only after that review. Its independently reviewed plan-decision
   record contains a `coordinator_migration` binding with exactly:
   `work_id=continuation-recovery`, `task_id=CR-3`, original `base_sha`, source
   coordinator commit/tree `C`, verifier commit/tree `V`, P1 spec/test-plan
   digests, the P0 implementation review identity/digest, the submitted CR-3
   scope-decision record/digest, and the permitted integration output schema.
   P1's normal coordinator acceptance stores that complete review decision in
   the accepted authority ref. No caller path, environment variable or
   candidate metadata chooses `C` or `V`.
4. Run normal integration through the exact reviewed coordinator source `C`.
   It first verifies that the live accepted P1 authority contains the matching
   `coordinator_migration` binding and that the current task base remains
   `2c508ff`; it then runs only verifier source `V`. It fails closed on a
   mismatch, stale review, wrong work/task, changed base or candidate, or
   absent authority. The integration receipt separately records original task
   base, coordinator `C`, verifier `V`, candidate commit/tree, P1 contract
   digests, historical runner identity and migration-binding digest.
5. Verifier `V` retains normal static, semantic, candidate, completion and
   integration checks. It applies the shared per-case evidence decision for
   original/P0 Red and current P1 Green. Existing historical reports and
   runner records are read and validated at their original identities; none
   are rewritten or relabeled.

The external trust step is explicit: the human approves this narrow upgrade
mechanism; an independent reviewer approves the exact source `C` and verifier
`V`; the standard P1 coordinator acceptance records those exact reviewed
identities. Runtime selection uses only that accepted record. The original
base is retained as historical task provenance, not treated as a verifier that
contains a feature it does not have.

If the exact P1 accepted-review format or coordinator acceptance path cannot
store and validate this binding without weakening its existing checks, stop
before P1/reopen and return a concrete revised migration proposal. Do not
change `base_sha`, bootstrap by invoking candidate verifier code, or treat
`check-completion` as proof of normal integration.

## Effect on P0 and P1

After this proposal is approved, revise P0's verifier paragraph to name the
coordinator-upgrade protocol above and map its selection/receipt behavior to
CR-T19 and CR-T59. CR-T19 continues to cover real nested integration. CR-T59
covers original/P0 Red continuity through current Green, preflight,
`checkpoint-run` and normal integration using the exact P1 binding. The four
new selectors remain distinct; T12/T13/T21 dispositions do not change.

P1 must name literal `C` and `V` identities obtained from the reviewed P0
implementation candidate before P1 acceptance. It must bind the exact submitted
scope decision and review digests. Only then can P1 activate the separate,
narrow CR-T21 historical-Red-unavailable exception. All T21 behavior checks
and current Green remain mandatory.

No active `plan.md`, `test-plan.json`, task graph, accepted ref, source,
receipt, state, report or ledger is modified by this proposal.

## Complete revised intent proposed with this decision

```markdown
# Intent: implement durable continuation recovery

## What
Implement and verify the sealed continuation-recovery plan addressing all R1–R4
findings, isolated from the interrupted product workstream. Execute CR-1 through
CR-4 on `agent/continuation-recovery` against the accepted CR-01–CR-08 contract.

## Why
Missing/replaced runtime state must not erase real execution or restart a task
at its implemented candidate without reconciliation.

## Non-goals
Product adoption/integration and product scheduling. CR-4 is limited to the
read-only product audit and reviewed adoption proposal defined by the sealed
plan. Do not initialize or mutate the original product runtime state.

## Known assumptions
Local cooperative Git; existing coordinator admission and TDD gates remain
required. For this workstream's CR-3 recovery only, a human-approved,
independently reviewed coordinator upgrade may select an exact P1-authorized
verifier source after the P1 authority records its commit/tree and review
identity. The original task base remains `2c508ff`; historical report,
authority, candidate and runner identities remain immutable. The upgrade cannot
select arbitrary candidate code and must preserve normal static, semantic,
candidate, completion and integration checks.

## Human decisions
Explore skipped: destination already clear. The user approved the implementation
scope change on 2026-10-22; its record is in `spec-change-execution.md` and
`authorization.md`. The user approved the bounded CR-3 recovery package on
2026-10-23; see `cr3-scoped-decision-record.md`. This proposed coordinator
upgrade assumption requires a separate submitted decision and exact intent
confirmation before it becomes active.

## E2E
Applies: disposable Git repositories and bounded fresh processes, as specified
in `plan.md` and `test-plan.json`. Execute task-owned Red → Green → Refactor,
independent review, and coordinator integration evidence for each task. CR-3's
normal integration uses only the exact coordinator/verifier revisions bound
and independently reviewed in its accepted P1 migration record.
```

Choose one option for this exact proposal and revised intent:

- **Approve coordinator upgrade (Recommended):** authorize the narrowly scoped
  P0/P1 migration above and approve the complete revised intent text. I will
  record the choice, replace `intent.md` with this exact content, confirm its
  digest, amend P0, and obtain a fresh independent exact review before P0
  acceptance.
- **Request changes:** preserve the current intent and stop CR-3 work until a
  different migration is designed.
