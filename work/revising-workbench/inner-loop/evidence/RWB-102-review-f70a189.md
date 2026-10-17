# Independent RWB-102 review: f70a189

**REJECTED. Ownership boundary APPROVED.** Reviewer `/root/review_revising_plan`, selected `gpt-6.1-sol` / high, independent Codex review. Exact candidate `f70a1898465697237d28d8d880c61d674e092335`; task admission base `c2635515f4f4643344b8483b86ea7d8e046d4bab`; accepted contract/inventory base `5964fbfb56128e95676f0b991852ac58529cb8f8`. Review includes the full original task diff from `c3c148c4d483d9b8cc9ad50915c81e60ea07abb5`, including WIP already present in the new admission base. Previous rejection artifacts remain intact. Reviewer changed only runtime review artifacts.

## F10 — review target can change after selected-task admission

High severity, `.agents/ask/verification/traceability/evidence.py:132-166`. `record_test_review` loads review body A and resolves/adopts A's selected task, but `_record_test_review` loads the path again. A concurrent external save can replace A with another individually valid review B. The helper validates and records B under A's task admission. CLI's cached review body also stops at `execute`: it passes only the path into the recorder, so caching there does not close this boundary.

Independent exact-candidate archive counterexample:

1. Valid canonical v2 fixture has captured product Task with execution alias WB-003 and available required passages. The accepted graph/plan additionally contains a valid review-only WB-004 task scope with no assigned cases. Both source contracts remain valid.
2. Body A is a fully valid WB-003 review. Body B binds the same candidate, contract, source inventory and digests but names WB-004, with its correctly empty tests/criteria/source digests. `review_errors` accepts B for that accepted task scope. WB-004 has no captured product Task alias.
3. Schedule a real file save of B immediately after the first review-path read returns A. Only external-save timing is controlled; admission, guard, semantic validation and recording are real.
4. Actual `record_test_review` successfully returns and publishes `task_id == 'WB-004'`, admitted using WB-003. Calling the same API with unchanged B correctly refuses `EM015_TASK_ID: selected identity must resolve to exactly one captured Task`.

The timing mechanism is equivalent to:

```python
original_load = evidence.load
first = True
def scheduled_save(path):
    global first
    document = original_load(path)
    if Path(path) == review_path and first:
        first = False
        review_path.write_text(json.dumps(valid_body_b))
    return document
# Set only the review-path load scheduling hook; invoke real record_test_review.
```

Carry one captured review document through actual target resolution, admission, `review_errors`, digest and record publication, including the CLI route; alternatively detect replacement and refuse without recording the substituted target. The task identity and document recorded must be the same ones that were admitted. Add an assertion through the real recording boundary. This is the existing selected-task guard obligation, not a request for broader product scope.

## Prior findings and caller assessment

F1-F8 repairs remain substantive: persisted resolution text is hashed; execution identity requires the matching qualified plan owner; direct omitted review target is derived; real v2 start/spawn refuses missing required context; safe committed missing blobs stay unavailable without fallback; backtick/tilde example fences obey closing grammar; foreign case/mapping selectors participate in captured closure; valid v1 task routes retain compatibility.

F9 is repaired: schema compatibility now dispatches on the exact admitted snapshot in `admission._selected_diagnostics` and the exact freshness-checked nested snapshot in `workflow._require_task_context`. The separate preflight no longer drops the selector. Independent probe against a captured v2 snapshot refuses missing required context. F3b is repaired: CLI validates document diagnostics without publication, resolves CLI/body scope agreement before workflow admission, and a default-workstream/task-body mismatch leaves an initially absent generation absent. These fixes retain invalid-document diagnostic precedence.

All eight amended caller paths were included in complete source and test review:

| Caller | Assessment |
| --- | --- |
| `.agents/ask/verification/run.py` | Qualified selected execution passes through actual verification/workflow bridge; legacy v1 remains supported. |
| `.agents/ask/verification/traceability/cli.py` | Actual scope/task agreement and refusal before generation publication now pass; F10 downstream document continuity remains. |
| `.agents/ask/verification/traceability/evidence.py` | Derives actual task body and refuses mismatched explicit target; F10 recording reread is the blocker. |
| `_ask/scripts/engineering_model/__main__.py` | Explicit product selection reaches actual model actions; no task-ID fallback to an unrelated product. |
| `_ask/scripts/inner_loop/__main__.py` | Actual spawn path carries selected execution; refusal prevents task-state mutation. |
| `_ask/scripts/inner_loop/driver.py` | Real selected startup admission, qualified identity and publication lineage are asserted. |
| `_ask/scripts/inner_loop/evidence.py` | Actual review bridge carries selected execution; guards remain active. |
| `_ask/scripts/inner_loop/integrate.py` | Actual selected integration admission retains required context and immutable candidate boundaries. |

Canonical/selector/snapshot sources and all other changed task sources were assessed with the same original-base scope; the new f70 production delta is limited to exact-snapshot schema dispatch and CLI pre-scope handling. No immutable base runner, accepted authority, CheckPlan, integrity, CAS or FF-only restriction is weakened. Real foundation registry/entrypoints, ordered lineage and retained baseline guards remain substantive. F10 prevents semantic approval despite green collected cases.

## Assigned cases/types and ownership

The machine artifact explicitly assesses all 13 assigned cases and every assigned criterion/type. `RWB-SELECTORS` and `RWB-CONTEXT-FRESHNESS` are approved. `RWB-PASSAGE-ACTIONS` is rejected for F10. All ten unchanged guard cases are approved. EM-001 integration is approved; EM-002 integration and EM-007/EM-015 integration remain rejected. EM-007 unit/e2e and EM-015 unit are approved within this task's accepted assignments.

All 14 worker Python sources fit amended RWB-102 ownership. Inventory from accepted contract and the complete original-base Python diff agree. All three changed test methods map to accepted new cases; no unmapped test methods or inventory exclusions. Coordinator plan/design/TaskGraph amendment, accepted pin, audited state/base history and RWB-101 runtime archival are the explicit approved exclusions. WIP source in the new base received no exemption.

Canonical spec digest `626fab82df682bdc7b382e4188bc822e488a8bf4ca9682a209be535fcea119bd`; plan digest `936e4cb9a06d550476170c299c9a64e337cd6c9c833da3ce5952c871f87a2e7b`; graph digest `e691e26e2865f165d3a59f57d4d2144675fb48f1c16ded0804aff6dbb3f6160a` remain pinned and unchanged.

## TDD and retained execution evidence

Test-only red `f6fa215957f9b6690e6a5aac0e8b083355c1827b`, run `67c5a9d2b9da464d96dae61367049597`, has one passage-action behavior assertion failure and 12 passes, with all runners collected. Final run `fa4c0d12de804f56b4e84022292f642b` binds this exact candidate and passes all 13. Both are present in `work/revising-workbench/traceability/executions.json`; canonical report-ledger digests, retained output hashes and each case's Git source digests independently match. Red/final test bytes are identical. TaskResult's candidate, admission base and commands match this pair.

Exact retained reports:

- `work/revising-workbench/traceability/runs/67c5a9d2b9da464d96dae61367049597/results.json`
- `work/revising-workbench/traceability/runs/fa4c0d12de804f56b4e84022292f642b/results.json`
- `work/revising-workbench/inner-loop/results/RWB-102.json`

Earlier registered original/F1-F7 reds and additive F6/F8 corrections remain as assessed in the preserved f52 review. No weakened assertions, exemption or unregistered supplemental red is used to satisfy current evidence. Green evidence is accurate but lacks the independently failing F10 counterexample.

Machine input `work/revising-workbench/traceability/RWB-102-review-input-f70a189.json` passes exact source/inventory/scope binding checks. `review_errors` reports only the deliberate rejected integration/criterion/action-case decisions. No integration authorization for this candidate.
