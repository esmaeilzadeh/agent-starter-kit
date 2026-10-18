# Specification Change Proposal

## Current specification

The approved plan covers nested task-level Red -> Green -> Refactor and code
review, plus consistent generated runtime bundles. It does not require each
Grill decision question to use selectable choices with a write-in path, and it
does not distinguish a missing gate for an authorized next step from a plan
that explicitly stops before that step.

## Proposed change

Extend the workstream to make every load-bearing Grill decision an interactive
choice question. Render alternatives as selectable options and retain a free
text path so the human can add nuance or a different answer even after choosing
an option. Use the active runtime's structured choice control; use numbered
options and an explicit write-in path only when the runtime has no such control.

Clarify continuation handling: resume an authorized stage without repeating a
valid approval. If the authorized next step requires a missing or stale
confirmation, ask for that confirmation with the runtime's choice control. If
the accepted plan explicitly stops before that step, report the authorized work
as complete and do not describe the future implementation gate as missing.

## Why the change is needed

The current Grill contract asks for expanded numbered questions, which permits
text-only grilling. The previous continuation response also called out an
implementation confirmation as missing even though the approved plan explicitly
stopped before implementation. These behaviors make decision questions hard to
answer in the UI and misstate the workstream's current authorization.

## Impacted artifacts

- `work/refactor-inner-loop/intent.md`, spec, criteria metadata, task graph, and
  plan: add the structured Grill interaction and continuation-boundary contract.
- `.agents/ask/stages/01-grill.md`, `.agents/ask/stages/06-implement.md`,
  `AGENTS.md`, and `_ask/policies/workflow.md`: define the authoritative
  behavior and its hard-stop cases.
- Generated Cursor and runtime agent projections: regenerate from canonical
  sources with `./ask sync`.
- `work/refactor-inner-loop/` verification and review artifacts: refresh against
  the amended spec and plan. Preserve the existing planning-only approval as
  historical; obtain new choices before implementation under the amended scope.

## Impacted workstreams

`refactor-inner-loop` on `agent/refactor-inner-loop`. This proposal amends its
reviewed plan before implementation begins; no second overlapping branch is
started.

## Migration / transition notes

No stored user decisions or runtime task state need migration. Existing
text-only Grill prompts are replaced by runtime choice questions with a
write-in path. Existing explicit stop boundaries remain authoritative.

## Acceptance criteria for the change

- Every load-bearing Grill decision is presented with selectable answer options
  and a way to add free text regardless of the selected option.
- Continuation guidance distinguishes a missing gate on an authorized next step
  from a completed plan whose explicit stop boundary excludes that step.
- Canonical prompts and generated runtime projections state these behaviors
  consistently.
- The amended plan receives independent review and pins the changed criteria
  before any implementation starts.

## Decision

Approved by the human's submitted response `approve` on 2026-10-19. This
approval authorizes updating the workstream specification and plan; it does not
replace the amended complete-intent confirmation required before implementation.
