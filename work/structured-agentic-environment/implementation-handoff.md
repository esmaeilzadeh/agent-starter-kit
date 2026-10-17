# Fresh-context handoff: connected Engineering Workbench

Status: planning finished; implementation intentionally stopped at the human's request. Start implementation only after explicit continuation in the fresh context. Remain on `agent/structured-agentic-environment`; work ID is `structured-agentic-environment`.

## Current goal

Replace record-type tabs with one connected **Epic → Story → Scenario → Task → Test → Result / Evidence** hierarchy. Keep parent context visible beside the selected detail. The epic root is the overview. Optional task/test/status filters operate on the same records. Generic Objects inspection is advanced only; evidence belongs with its result. Use meaningful titles, actionable counts, visible test source, recorded outcomes and useful collapsed debug details.

Open current-branch work by default. Other work/branch sources are explicitly identified, revision-consistent and read-only, without changing checkout. Preserve many-to-many links and label scenario-mediated secondary tests distinctly from executable task ownership. Missing stories, historical task breakdown, execution metadata and evidence remain explicit; never fabricate completion.

## Read these current artifacts

1. `plan.md`: execution sequence, ownership, verification, risks and stop boundary.
2. `workbench-design.md`: connected navigation, wireframes, source/relationship authority and UI states.
3. `specs/current/structured-agentic-environment.md` and adjacent JSON: the one specification, revision 3.
4. `inner-loop/tasks.yaml` and `test-plan.json`: nine tasks and 57 exactly-once test assignments.
5. `workbench-plan-review.md` and `traceability/workbench-plan-review.json`: independent approval of the exact planning source.
6. `traceability-accepted.json`: coordinator pin of that contract.
7. `performance-baseline.md` and `planning/performance-baseline-*.json`: measured baseline and limitations.

Use the current brief/design as authority. Earlier table-first discussion is superseded; it is unnecessary for implementation decisions. Existing evidence remains available for truthful historical inspection.

## Implement in order

WB-001 relationships/tasks → WB-002 branch/source inventory → WB-003 source/result identity → WB-004 connected navigator → WB-005 epic/story/scenario details → WB-006 task detail → WB-007 contextual attention/decisions → WB-008 test/result/debug detail → WB-009 browser/accessibility/performance validation.

Retain Streamlit for the measured first pass. Read the pinned frontend-design skill and version-matched Streamlit references. Theme is script-scoped under `_ask/ui/.streamlit/`. Load selected details lazily. Initial root overview performs no evidence scan or test-source parsing. Caches must preserve evidence-integrity checks and captured-form freshness; mutations call the existing guard.

## Verification boundary

Planning source `b755d83141b030d2d101e9fd9f37b51e28a8ef26` was independently approved and pinned. Graph, contract, model validity and exact-once case mapping passed. No application code changed and no new behavior tests were implemented or executed in this planning turn. There is no new task execution state.

The 57 cases comprise 34 retained obligations and 23 new future obligations. Earlier required red-phase history remains incomplete. Preserve this limitation separately from actual case execution results; the new pin does not repair it. Capture genuine assertion-red before each behavioral implementation, then green and candidate review. Full Verify and exact-candidate result recording are required before claiming delivery.

Honor the human's chosen implementation model, including Luna, over old model metadata. Recheck the clean worktree and current accepted bindings before starting. Commit meaningful steps on this branch. Do not initiate a second workstream or infer permission to merge/push from this handoff.
