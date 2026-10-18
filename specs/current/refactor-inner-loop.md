# Specification: Refactor and code review inside the task loop

## Status

CURRENT, revision 2. The human approved the 2026-10-19 Spec Change proposal.
Implementation remains subject to the updated complete-intent confirmation.

## Goal

Make every task use behavior-preserving Red -> Green -> Refactor cycles followed
by independent task code review, correction, verification, and integration.
Complete local refactors; park broader horizontal refactors as tagged later work.

## Non-goals

Changing product requirements or contracts through refactoring; removing evidence,
review, retry, ownership, or human-authority gates; renumbering stage IDs; replacing
the task scheduler; implementing an automatic code-quality judge; editing pinned
upstream repositories; adding a new later-inbox CLI or external tracker workflow.

## Behavior

### One task, two nested cycles

For each behavior slice: observe a behavior-assertion Red, implement the minimum
Green, then apply relevant task-local structural refactors while keeping tests
Green. A Refactor pass with no applicable cleanup records that outcome and does
not invent cosmetic edits. Continue slices until the task outcome is implemented.

Independently review the committed candidate. Classify every suggestion:

| Finding | Required action | Task integration |
| --- | --- | --- |
| Local structural refactor | Implement it, run relevant checks, obtain fresh review | Blocked until fixed |
| Behavioral defect or existing-contract violation | Correct within the accepted spec using Red -> Green -> Refactor, then fresh review | Blocked until fixed |
| Broader horizontal behavior-preserving refactor | Prepare a parked later card tagged refactoring | Does not block on doing that refactor |
| Necessary change to meaning, behavior, or contracts | Enter Spec Change before changing the implementation contract | Blocked until authorized amendment |
| Cannot classify or safely complete a required local fix | Escalate with evidence | Blocked; never silently defer |

A broad refactor spans responsibilities or requires cross-cutting structural work
beyond the current task outcome, even if files happen to match owned_paths.
A local refactor improves code introduced or directly affected by the task within
its accepted responsibility. File count and owned-path membership alone do not
make broad work local. A bug or contract violation is not an optional refactor.

After a local fix, repeat task code review on the changed candidate. An advisory
label or a rationale alone cannot waive a valid local suggestion. A reviewer may
withdraw a mistaken finding with evidence that no change is needed; that is a
corrected assessment, not a waiver. Existing bounded review/debug retries remain;
exhaustion blocks or escalates rather than permitting an infinite loop or an
integration with unfinished local findings.

Only an independently APPROVED current candidate with completed local findings
and passing required candidate checks can integrate. Final candidate evidence
must remain bound to its exact SHA. Worker self-reported Green is insufficient.

### Broader refactoring cards and writer boundaries

The task reviewer records each broad candidate in a later-card draft in the
candidate-bound review evidence, including a stable slug, Tags: refactoring,
motivation, affected responsibilities, suggested scope, and source work/task.
Existing matching cards are referenced rather than duplicated. This work is a
proposal, never approval to execute the broader refactor.

The coordinator owns parking and publication. It preserves complete tagged card
drafts and their pending publication status in persisted candidate-bound runtime
review evidence while any task candidate may resume. It makes no out-of-band
source commit to park cards during task execution, including blocked/escalated
states. After all task candidates integrate and no writer or resumable candidate
remains, it materializes attributed .later/<slug>.md cards at the clean normal
workstream integration boundary. Integration then publishes them on develop,
where status reads the shared inbox. The task writer does not switch branches,
edit unowned paths, or start another workstream to publish a card. Complete
drafts, stable slugs, and pending publication status remain in the persisted
runtime handoff if work is interrupted or cancelled; local recovery durability
does not claim remote publication before integration. The broader refactor itself
never blocks the task; preserving its suggestion is required evidence.

### Outer workflow and compatibility

The outer path becomes Explore when needed -> Grill -> Spec -> Challenge -> Plan
-> execute task loop -> workstream Verify -> Accept. Task-level Review and
Refactor are inside the execution loop. Any aggregate workstream assessment
retains its purpose; its local findings route into the affected task/remediation
loop, and findings that alter accepted scope return through Plan or Spec Change.
There is no second unconditional outer Refactor pass.

Stage IDs 06/07/08 remain usable as operation contracts. The existing next-action
CLI values implement/debug/integrate/blocked and retry counts remain compatible:
implement means enter the correction/TDD cycle, including its Refactor pass;
debug diagnoses a stalled correction and returns to that same cycle. No new
persistent TDD sub-state or changed CLI return vocabulary is required here.

### TDD guidance and generated bundles

One repository-owned canonical task-loop contract owns the semantics. Stage
contracts and generated bundles reference it. Preparation applies a managed,
idempotent repository TDD override to the installed skill views used by this
repository, explicitly superseding the upstream exclusion of refactoring.
Preserve source/revision pins, do not vendor upstream skill trees, retain
unrelated upstream skill content, and update both .agents and Cursor skill views.
The canonical rules apply to Claude, Codex, Cursor, and OpenCode agents.

SKIP_INSTALL=1 remains pin-validation-only and cannot mutate prepared skill files.
Missing optional skills are not fabricated. A missing required TDD output or a
failed installation cannot be reported as a successful patched preparation.

## Interfaces

Existing public ./ask prepare, ./ask sync, ./ask install, and ./ask inner-loop
commands. Existing candidate-bound review evidence remains the review authority;
review prose carries the finding classifications and parked-card drafts. This
change does not invent a machine proof of semantic refactoring quality.

## Constraints and invariants

- One active committing task writer and existing owned-path boundaries.
- Refactoring preserves observable behavior, meaning, and contracts.
- All valid local findings are fixed; broader structural proposals stay parked.
- Source edits invalidate old review approval and require fresh candidate checks.
- Existing retry limits, Spec Change authority, FF integration, and source-clean
  verification boundaries remain intact.
- Every runtime projection follows the canonical task-loop contract.

## Failure cases

A post-refactor failure returns to task correction. Stale/rejected review or
failed checks refuse integration. Scope-changing redesign enters Spec Change.
Unresolved local work at the retry limit escalates. Interrupted card publication
retains the tagged draft and publication status. Repeated preparation replaces
its own managed override without duplication or changing pinned upstream input.

## Acceptance criteria

RF-001: TDD Refactor and independent code review occur inside each task loop;
no unconditional outer Refactor phase remains.
RF-002: Every valid local finding is fixed and re-reviewed; broad horizontal
refactors are not implemented as part of that task.
RF-003: Broader proposals become attributed later cards tagged refactoring,
with coordinator-owned publication and interruption-safe handoff.
RF-004: Behavior/meaning/contract changes are distinguished from structural
refactors; necessary redesign enters Spec Change.
RF-005: Existing rejected/stale review and failed-check integration refusals
remain; only a freshly approved verified candidate integrates within retry bounds.
RF-006: Preparation applies the canonical TDD override to both local skill views,
idempotently, retaining pins/upstream text and respecting dry-run/failure cases.
RF-007: Install/sync deliver consistent canonical task-loop references and
stage projections to every supported runtime.
RF-008: Every load-bearing Grill decision uses selectable answer options and
keeps a free-text path available regardless of the selected option. Use the
active runtime's structured choice control; when unavailable, provide numbered
options plus an explicit write-in path.
RF-009: Continuation asks for missing or stale confirmation only when it blocks
an otherwise authorized next step. An explicit plan stop is reported as
complete within scope, without presenting a future gate as currently missing.

## Open questions

None about user intent. Exact review-only criterion authority and test mapping
must be independently reviewed before implementation; no test execution is claimed
by this planning document.

## Source intent

work/refactor-inner-loop/intent.md

## E2E

Applicability: not_applicable for an application journey. Public CLI integration
and temporary consumer install/prepare/sync tests cover the changed interfaces;
semantic protocol claims require independent scenario review.
