# Independent RWB-102 remediation review

**REJECTED. Ownership boundary APPROVED.**

Reviewer `/root/review_revising_plan`, selected Sol/high, Codex independent context. Exact candidate `26e8cbd1342a182b35bda5e3b015bbeab3b20ca9`, recorded admission base `c2635515f4f4643344b8483b86ea7d8e046d4bab`, accepted inventory base `5964fbfb56128e95676f0b991852ac58529cb8f8`. Full original task source review still starts at `c3c148c4d483d9b8cc9ad50915c81e60ea07abb5`, including pre-new-base WIP. Earlier64bf26c rejection remains preserved. Runtime review writes only; no source/state/ref/commit changes.

## Remaining F6: false heading after invalid fence closer

The ordinary fenced heading/table cases now work, but scanner accepts info text after a supposed closing fence. Exact candidate archive reproduction:

~~~text
# Work
```text
```python
## Work breakdown
Example still inside fence.
```
~~~

With selector `{"kind":"heading","path":["Work","Work breakdown"]}`, resolver returns available example text. Markdown closing fences may have only trailing whitespace; the inner ` ```python ` is code content, so the heading remains inside the fence. Extend closing grammar tests across marker characters/length and heading/table lookalikes. This is the originalF6 false-contract selection class, not a new feature.

## F8: valid v1 task starts regress

The F4 fix gates every adopted model by a synthesized execution pair. V1 permits no execution/context fields, so these pairs cannot match. Independent clean-archive comparison of originalc3c148c and this candidate used the same valid fixture: referenced_model, contained planned task build, ready TaskGraph build, no execution fields; validate_current returns no diagnostics. Original driver.run_once returns running=build and cmd_spawn after cas_init returns0. Both current routes refuse EM015_TASK_ID.

Schema-aware compatibility is needed across the same pattern in driver start/integration, direct/CLI coordinator review, task traceability and verification workflow bridge, while preserving validation-first diagnostic precedence and all v2 selected-context refusal. Existing v1 direct-integration positive does not cover these task-start callers. Add genuine failing tests for representative legacy routes before repairing the guards.

## Prior findings rechecked

F1 resolved: full derived resolution now participates in generation identity; exact persisted-text tamper probe rejects on reload. F2 resolved for the reported ownership mismatch: borrowed product row refuses, foreign execution's own plan admits. F3 resolved for omitted/default caller target: review body now supplies task identity and CLI/body scope mismatch rejects before review replacement. F4 v2 resolved: actual driver/spawn missing-context tests preserve state and publication, valid v2 starts remain available; F8 exposes the separate version-dispatch regression. F5 resolved: safe absent committed context is admitted unavailable with no fallback; unrelated workflow remains possible and dependent Task refuses. F7 resolved: selected foreign case plan and both external mapping endpoints enter captured closure; direct/captured validation agree. Real stale helper/context actions and bound publication checks strengthen prior coverage.

The full original-base source inventory and eight amended caller paths remain reviewed. All worker sources fit the amended ownership; approved coordinator amendment/pin/runtime archive/state history remain explicit exclusions. No immutable runner/authority, instrumentation, CheckPlan, integrity, CAS or FF-only mechanism was weakened. New compatibility and parsing defects still prevent semantic approval.

## Evidence and TDD

Final run `57d0c0ee75624111ad34eebbb732a0e5` is coordinator-ledger bound to this candidate, contains all13 assigned cases and passes; report, retained logs and Git source hashes were independently verified. Test source is byte-identical to claimed full-byte counterfactual red a878ec4.

Runtime citation discrepancy E1: report `fd5d6dabb7fd4e25bc91a3e2135092fc` exists and shows3 assertion failures/10 baseline passes, but no matching current executions.json entry exists. a878ec4 is a sibling final-test/old-implementation commit on d386, created after production-fix development, so it must not be presented as original test-first chronology. Actual authoritative pre-fix reds44d6d62/run2c05d3... andd386cfe/runbbbd412... already show all three assertion failures before399491f. They support honest continuity with later additive checks. Correct TaskResult citation or use supported supplemental recording; do not fabricate a ledger/history entry.

Earlier behavior assertions remain; F5's error→unavailable correction implements the unchanged safe-gap contract and adds action-disposition/no-fallback checks. No behavior exemption or regression relabel is used. Context-freshness case is now semantically approved; selectors and passage-actions remain rejected forF6/F8. All10 unchanged generic guard cases retain fresh passes. Machine input contains every assigned criterion/type/case, exact source/inventory bindings and original-base review metadata; parser failures are only intended rejected semantic decisions.

Coordinator must preserve this rejection. Required source work remains F6/F8, plus citation repair and fresh candidate evidence/review. No integration authorization for26e8cbd.
