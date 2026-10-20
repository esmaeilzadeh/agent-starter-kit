# Proposed scope amendment: complete workbench coverage

Status: proposed; complete correction intent and assumptions await approval.
Explore skipped: destination already clear.

## Request and selected scope

The user reports an empty workbench beneath “Use readable identifiers scoped to
each work” and says that title does not summarize the current workstream.
The submitted scope choice was “Current work + prevention (Recommended)”.

## Reproduction and cause

At source commit `3517e96`, `engineering-model.json` is a v1 model containing one
intent node and zero edges. The actual snapshot capture and navigation functions
produce one epic and zero stories, scenarios, tasks, or tests. Capture follows
model references; this model has none. The separate test plan declares 39 tests,
and the task graph/runtime state contain 10 tasks. Runtime records mark tasks 1
and 2 integrated, task 3 running, and tasks 4 through 10 pending.

The title predates the expanded intent covering token cost, exact dependency
bindings, immutable revisions, project discovery, impact reassessment, evidence
authority, migration, and savings measurement.

## Complete correction intent

Make the workbench accurately describe and expose the selected workstream's
recorded scope and progress, including when its model is sparse.

1. Give the shorter-hashes root a title and description representing its approved
   full intent. Populate explicit product relationships from the canonical spec
   and test plan, with source attribution and stable identifiers.
2. Include the selected workstream's existing test plan and task graph in the
   workbench's captured inputs even when the model has no links to them. Preserve
   snapshot freshness and working-versus-committed source selection.
3. Display tasks and planned tests with missing product relationships in explicit
   unmapped groups. Distinguish missing records from zero records, and expose
   incomplete model coverage. Product membership requires a recorded relationship.
4. Preserve recorded runtime status and evidence provenance. Planned tests,
   completed execution, and accepted evidence remain distinct states.

## Assumptions and boundaries

- Existing approved intent/spec/test-plan/task graph define the work; the
  correction is a projection and model-coverage change.
- One root may summarize this workstream; its recorded features/stories/scenarios
  express the distinct outcomes. Additional unrelated epics require source evidence.
- Missing or malformed optional inputs get attributable diagnostics. They cannot
  supply invented relationships or authorize workflow completion.
- Prefer compatibility with the existing v1 model. Any required v2 migration uses
  the existing reviewed migration contract.
- Existing immutable execution history and sealed plan/test obligations retain
  their authority. This amendment does not advance or integrate task 3.
- Implementation ownership is limited to engineering-model snapshot/projection
  and workbench loading/navigation/coverage surfaces, their regression tests,
  and this workstream's model and correction evidence. Comparison modules are
  outside this correction.

## Acceptance criteria

- The current workstream exposes all 10 recorded tasks and 39 planned tests.
- Tasks 1–2 display their recorded integrated state; task 3 displays its recorded
  running state; pending tasks and unexecuted tests remain distinguishable.
- The epic description represents the complete approved scope and has navigable,
  source-backed children. Unmapped records remain reachable and labeled.
- A sparse-model fixture with real task/test artifacts remains navigable.
- Working-file and committed snapshots use their selected sources consistently;
  changes to captured task/test artifacts invalidate stale views as appropriate.
- Missing/malformed artifacts and unsupported relationships remain visible as
  unavailable/incomplete; no fabricated success or membership is introduced.

## Execution after approval

Prepare the bounded implementation plan and regression mapping; record a scope
amendment before changing files outside the active task. Capture failing behavior,
implement and refactor, obtain independent review, run applicable checks and
`./ask verify`, and record candidate-bound results. Commit meaningful steps.
Preserve the active task's execution state and evidence during this correction.

## Approval needed

Approve the complete correction intent, assumptions, acceptance criteria, and
temporary scope amendment above, or request changes. The prior scope choice
selects the destination; it is not recorded as approval of this complete proposal.
