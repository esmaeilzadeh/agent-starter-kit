# Independent workbench planning challenge

Decision: **APPROVED — planning contract only**. No blocking findings remain at `b755d83141b030d2d101e9fd9f37b51e28a8ef26`.

Reviewer: `review_workbench_plan`; runtime: `codex`; model: `gpt-6-astra` (configured kit-03-spec-challenge role); reasoning: high; parent model: not exposed by runtime. Independent child context. This review implements stage 03 Spec Challenge and uses writing-for-agents in embedded mode.

## Exact authority

Reviewed one specification: `specs/current/structured-agentic-environment.md`, with adjacent canonical JSON revision 3. Reviewed supporting plan, design, scope amendment, TaskGraph, test plan and measured baseline at the same commit. Their file hashes and canonical contract digests are recorded in `traceability/workbench-plan-review.json`.

- Specification digest: `f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb`.
- Test-plan digest: `572d2c3dda82e69a49d78b1320ec35835f4f153137e62c35f41af678ad106330`.
- Parsed TaskGraph digest: `09016abdb419b5cd35f43c095fb0c2e0c2991d00a2883a38082b9cc30e2ffa23`.

The current human brief and clarification govern the redesign. Earlier table-first choices are historical. Original intent/confirmation bytes and EM-001–007 remain unchanged; the new scope amendment records the actual user instruction without inventing an approval quotation.

## Findings and resolutions

| Challenge / counterexample | Resolution at reviewed commit |
| --- | --- |
| A test appears under two tasks, but task scopes assign it to one owner. A naive join either drops the second relation or fabricates execution ownership. | The design separates one executable owner from secondary tests covering a task's recorded scenarios. Secondary links carry an explicit scenario-mediated label and cannot establish task completion. `WB-relations` tests this distinction and foreign-work ID collisions. |
| Structural lazy-loading checks pass while no measured latency sample exists. | `WB-latency-budget` now requires 20 warm samples, five complete cold starts, content-specific readiness, candidate-bound raw results and numerical comparisons. Misses remain failures. |
| A browser journey skips Story or logs poor contrast yet passes. | The journey explicitly traverses a recorded Story. Browser obligations assert rendered normal/large text and focus contrast, labeled controls, visible focus and no page-level narrow-layout overflow. |
| A task run accidentally executes every discovered engineering case. | The existing adapter filters the collected suite to task selectors before execution. The plan now describes that behavior and the remaining discovery-import-error constraint accurately. No speculative runner migration is required. |
| A root theme changes the unrelated training viewer. | Theme ownership is `_ask/ui/.streamlit/config.toml`; the unrelated viewer remains outside scope. |

## Why the plan is eligible

The main experience is one connected Epic → Story → Scenario → Task → Test → Result/Evidence hierarchy with contextual detail. Root overview, status filters and attention routes lead back to the same records. Objects and raw evidence are secondary technical inspection. There are no primary record-type tabs. Recorded relationships and absent stories are treated honestly.

Nine bounded tasks have stable IDs, outcomes, dependencies, distinct owned paths, completion evidence and mapped cases. The graph and plan agree. Backend relationship/source/evidence adapters precede navigation and detail surfaces, followed by final browser/performance validation. All 57 cases belong to exactly one responsible task: 34 retained cases and 23 future cases. Foundational tests are regression protection, not invented historical authorship. Source and result identity tests contain adversarial duplicate-work IDs, same-named test methods, historical source, moved refs, tampered logs and stale decisions.

The shared document guard and evidence evaluator remain authoritative. Branch inspection resolves a committed revision, uses matching definitions/source and original evidence authority, and stays read-only. Missing models, task history, source, runtime metadata and accepted evidence remain explicit. Declared done, actual case pass, evidence currency and workstream verification stay distinct.

The raw baseline supports the reported medians and nearest-rank p95. Five browser samples are limited; unreliable refresh timing is excluded from conclusions. Retaining Streamlit for bounded optimization is reasonable given the measured small-pilot backend costs. The plan does not claim an achieved improvement or a comparative framework benchmark. New performance budgets and rendered accessibility checks remain future obligations.

## Independent checks performed

The repository's `contracts_at` validator accepted the exact committed spec/plan/graph. Additional read-only checks verified matching nine graph/scopes, all 57 cases assigned exactly once, matching graph case lists, dependency order, nonoverlapping owned files, preserved first seven criteria, byte-identical historical intent/confirmation and unchanged classifications for all 34 retained cases. The only retained case assertion amendment makes overview source inspection lazy and is disclosed. No behavior suite was executed for this planning review.

## Approval boundary and stop

The coordinator may pin these exact reviewed obligations. This approval establishes neither application correctness nor implementation completion. Existing missing red-phase evidence stays unresolved and cannot be manufactured, relabeled away or treated as repaired by a new contract pin. Genuine behavior-red, green execution and candidate semantic review remain required during implementation.

Stop after the planning artifacts and accepted contract are committed. Application implementation begins only after the human's explicit continuation following the requested model switch. Any material contract change requires an amended independent review before that implementation starts.
