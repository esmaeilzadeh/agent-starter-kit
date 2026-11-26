# Kit Protocol: 06 Implement

Source contract extracted from the Build Spec agent-contracts section. Portable SoT for this stage.

Requires: clean tree and dedicated branch. Feature work uses the accepted spec
and plan under `work/<work-id>/`. A reproduced bug against an existing contract
may reuse that contract and a concise repair record instead of creating a new
feature spec/plan; follow `_ask/policies/workflow.md`.
Behavior-preserving maintenance uses the existing contract and a concise work
record of scope, invariants, and checks. It does not inherit feature spec/approval
gates. Use `maintenance/<work-id>` and repository-level verification for standalone
maintenance under `_ask/policies/workflow.md#investigation-review-and-maintenance`;
preserve existing model/TaskGraph gates for work already governed by them.
An investigation or review request alone does not authorize implementation.

## 15.6 06 Implement Agent

Purpose:

```text
Perform delegated implementation labor.
```

When a TaskGraph is active, use the accepted plan's task graph as
the execution queue. Work only on its reviewed task IDs and owned paths. Record
the task ID on its result and verification evidence, then update that task's
state only when its planned completion evidence is present. A new deliverable
or changed test assignment returns to Plan for an amended, independently
reviewed contract before implementation continues.

Preconditions (`./ask check-workstream` for feature work; see `_ask/policies/workflow.md` for the reproduced-bug path):

```text
clean working tree          ← still hard (safety)
dedicated branch
explicit complete-intent approval ← feature path
accepted spec and plan      ← feature path; prepare from defaults if missing
reporter-authorized repair request and concise reproduction record ← bug-fix path
authorized maintenance request, preserved invariants, and checks ← maintenance path
no unrelated uncommitted changes
```

Feature branch convention (standalone maintenance uses the route above):

```text
agent/<work-id>
```

Must not:

```text
modify unrelated work
rewrite acceptance criteria to make tests pass
bypass policy
perform forbidden high-risk actions
continue through a mandatory human-approval gate; route uncertainty through `_ask/policies/workflow.md#model-confidence-escalation`
```

At meaningful milestones, create commits so that important engineering states are recoverable and attributable. **Do not wait until the plan is finished** — commit after each meaningful step. **Do not wait for the human to ask** to commit on `agent/<work-id>`; the dedicated branch is the safety boundary (`_ask/policies/worktree.md`).

---

## Kit emphasis

- For feature work or an existing TaskGraph, require the populated `work/<work-id>/engineering-model.json` before starting or
  resuming implementation. Keep model links and declared lifecycles current through
  guarded edits when the work changes. Execution results remain in their existing
  authoritative records; follow `_ask/docs/engineering-model.md`.

- For feature work, a missing or stale explicit intent confirmation blocks an otherwise authorized next step: present the full current intent and assumptions as a choice question with “Approve complete intent and assumptions” / “Request changes” buttons, keep an optional comment available alongside the choice, wait for a submitted approval, record it with ./ask confirm-intent --work-id <id> --choice approve, and re-run the gate. If the runtime cannot preserve both values, offer numbered choices and invite the selected number or option label plus added text in the same reply. Accept unsolicited concise affirmative text for compatibility and record the exact response with `--response`; never ask the human to write or repeat a confirmation sentence. A preselected option is not approval. Never infer confirmation from a request to implement alone or a prior approval of only the direction/order. If the approved plan explicitly stops before implementation or another future action, report completion within that scope instead of describing the future gate as missing.

- A later explicit human direction can extend a previously approved execution endpoint. When What, Why, and assumptions stay the same, record that direction in the plan or a scoped authorization artifact and keep the approved `intent.md` byte-for-byte unchanged; do not ask the human to reapprove the complete intent. A generic “continue” does not override an explicit stop. A clear direction such as “continue through acceptance” does. If What, Why, or an assumption changes, use the normal intent/spec-change choice and bind renewed approval to the changed intent.

- **Reproduced bug:** follow the short path in `_ask/policies/workflow.md`; the existing accepted contract and concise repair record replace new feature spec/plan artifacts. Keep applicable clean-worktree, scope, review, commit, and verification gates.
- **Default feature path:** run `./ask check-workstream <work-id> --implementation` before implementing. This explicit entry verifies a confirmed model plan against the active runtime; generic continuation does not authorize implementation. If the runtime cannot verify or switch the active model, stop at the single named handoff request and resume only after recording the observed model and its provenance with `ask orchestrator-handoff resume`. If it fails for missing spec/plan and the work is still on the kit path, **prepare** those artifacts from accepted defaults (if intent is not yet approved, present its choice question once), then continue — do not implement feature work on empty paper. Off-path (“just code”) only if they explicitly left: warn once and follow.
- If the tree is dirty: stop and grill the human per `_ask/policies/worktree.md` (never silent stash/reset). That refusal is safety, not workflow theater.
- One plan → one `agent/<work-id>` branch; do not start a second related branch that would conflict on shared files while this one is active.
- Commit after each meaningful step on the workstream branch **without waiting for the human to ask** (kit policy overrides global “only commit when asked”).

## Inner-loop

**Steering `owned_paths`:** seam/module globs in `work/<work-id>/inner-loop/tasks.yaml` (project memory, not a file census). Expand at spawn. Files created inside a glob are in scope.

When that TaskGraph file exists, follow `.agents/ask/task-loop.md` and run `./ask inner-loop run` (or `resume`). The coordinator verifies the confirmed model handoff before admitting a writer. Scheduling, retry, CAS, and evidence fold live in `_ask/scripts/inner_loop/`. This contract does not copy the DAG.

One committing writer. Done when the current task is `integrated`, `blocked`, or `escalated`.

Future submissions use candidate-bound `ask-task-result/v2`. After committing the candidate, emit its work/task/base/candidate identity and TDD history or typed exemption. Follow `_ask/docs/inner-loop-evidence.md` for the result format and coordinator-recorded review. Integration executes the candidate CheckPlan; worker-reported green fields alone cannot advance state.

## E2E

For feature work, build the spec’s confirmed E2E journeys, or keep `not_applicable` plus reason. Missing E2E with no reason refuses feature implementation. Maintenance retains applicable existing journeys and checks without inventing a new behavior contract.

## Structured test evidence

For behavioral slices, capture actual failing behavior at immutable red revisions with `./ask traceability run`; commit the candidate and retain final green separately. For a bug fix, only the reproduced defect is a Red target; mapped regression guards require Green, not manufactured failures. Structural maintenance keeps existing checks green and uses the structural exemption when a TaskGraph is active. Planned outcomes never count as execution.

Contract, authority, commands and migration: `_ask/docs/spec-test-traceability.md`.

For consequential uncertainty, use `_ask/policies/workflow.md#model-confidence-escalation`
to investigate missing facts, consult on technical judgment, or seek human
preferences/authority. Classify `uncertainty_kind` explicitly; preserve saved
model selections and required independent review.
