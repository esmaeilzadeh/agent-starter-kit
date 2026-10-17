# Independent RWB-101 review

**Verdict: REJECTED. Ownership boundary: APPROVED.**

Reviewer `/root/review_revising_plan`, selected `gpt-6.1-sol` / high, Codex independent review context. Candidate `571a4b24c6a836fe13e9362c28eb6465a658ab02`. Accepted contract base `f563e619c5c809cdb39072941fab4c2626284f64`. Boundary comparison starts at `09fbcc3`; coordinator bootstrap `8fbd389` is explicitly permitted runtime, not a task extra. No source edits or commits by reviewer.

## Blocking findings

### RWB101-F1 — high: _ask/scripts/engineering_model/flows.py:95

Qualified Test path, work_id and plan_digest are checked against different plans. A Test path to work/other/test-plan.json with a different assertion, but work_id product and digest of the product plan, is admitted and treated as exact product flow coverage. Bind path/owner/digest/case consistently and reject contradiction while preserving genuine reviewed cross-work mappings.

### RWB101-F2 — medium: _ask/scripts/engineering_model/flows.py:143

A reviewed local mapping selector with case_id [] is accepted. _qualified_selector returns a tuple without validating local case ID type; _validate_mappings skips its local-ID branch and reports no error for a recognized local scope. Reject malformed local case IDs deterministically before considering any coverage.

### RWB101-F3 — medium: _ask/scripts/engineering_model/validation.py:454

A v2 decision history entry with all required keys but event [] raises unhashable-list TypeError at set membership. The helper is inherited unchanged, so this is not evidence of altered valid v1 rules, but the new v2 validator fails its promised malformed-field nonmutating diagnostic contract. Type-check malformed JSON before membership, keeping valid v1 behavior and diagnostics stable.

### RWB101-G1 — medium: _ask/tests/test_revising_model.py:86

The qualified-ID case covers duplicate aliases, foreign edges and distinct explicit works, but has no assertions for its mapped definition-done versus verification distinction or tracker/later reference metadata not implicitly joining/owning execution. Add bounded identity-helper assertions without inventing a new metadata schema or relying on future intake/projection tasks.

## Exact reproduced counterexamples

F1–F3 were reproduced again in a clean temporary git archive of exact candidate `571a4b24c6a836fe13e9362c28eb6465a658ab02`, with no original-checkout imports, while the writer was preparing remediation. Both F1 and F2 returned an empty diagnostic list; F3 raised TypeError.

```python
from _ask.tests.revising_fixture import model, reference_bytes, digest, reviewed_mapping
from _ask.scripts.engineering_model.validation import validate
import copy, json
refs, p = reference_bytes()
d = model()
d["nodes"][2]["case"]["plan_digest"] = digest(p)
# F1: inconsistent declared plan path and qualified owner/digest
other = copy.deepcopy(p)
other["work_id"] = "other"
other["tests"][0]["scenario"]["then"] = ["Entirely different assertion"]
refs["work/other/test-plan.json"] = json.dumps(other).encode()
bad = copy.deepcopy(d)
bad["nodes"][4]["reference"] = {"path": "work/other/test-plan.json",
    "id": "WB-publish", "work_id": "product", "plan_digest": digest(p)}
assert validate(bad, ".", "product", reference_bytes=refs) == []  # incorrect acceptance
# F2: invalid selector value is silently accepted even with exact body review
p2 = copy.deepcopy(p)
p2["flow_mappings"] = [reviewed_mapping(
    {"scope": "local", "case_id": []}, {"scope": "local", "case_id": "WB-stale"})]
refs["work/product/test-plan.json"] = json.dumps(p2).encode()
bad = copy.deepcopy(d)
bad["nodes"][2]["case"]["plan_digest"] = digest(p2)
assert validate(bad, ".", "product", reference_bytes=refs) == []  # incorrect acceptance
# F3: complete history keys with malformed event cause a crash
refs, p = reference_bytes()
bad = copy.deepcopy(d)
opts = [{"id": "a", "label": "A"}, {"id": "b", "label": "B"}]
bad["nodes"].append({"id": "choice", "type": "decision", "title": "Choice",
    "lifecycle": "open", "options": opts, "history": [{"event": [], "actor": "a",
    "rationale": "r", "timestamp": "2026-10-16T00:00:00Z", "options": opts, "resolution": {}}]})
validate(bad, ".", "product", reference_bytes=refs)  # TypeError: unhashable type: list
```

## Evidence and TDD continuity

Independently verified all four retained red ledger/report canonical digests, report→log byte digests and recorded test-source digests against their Git source commits. Each red reports three behavior-assertion failures and eight baseline passes. Final green `84b180c7ecac453c80fabf37306c4eee` binds this candidate and passes all 11 assigned cases. Green execution is genuine but insufficient to override reproduced semantic counterexamples.

| Revision | Run | Assessment |
| --- | --- | --- |
| 89c7d1f | 079915b42162485e9d9edacba1228143 | Initial red retained; contained downstream fixture/assertion mistakes. Not used alone for continuity. |
| 0be97a3 | d7b41df09aa348efa5e5eb010f1d259d | Test-only strengthening/correction retained. |
| bbe2cbf | ddad73f1490c485283828cafb5762bfc | Added missing graph/identity/flow counterexamples before production. |
| 3dc7fb4 | 1f74aea3ce7c41998cecd762b03c8bc3 | Complete test-only red, including local mapping digest self-reference. All three new mapped cases fail behavior assertions; eight regressions pass. |
| 571a4b2 | 84b180c7ecac453c80fabf37306c4eee | All 11 cases pass; exact new test/fixture bytes unchanged from complete red. Semantic rejection remains. |

The corrected v1 fixture now expects its original intent/parent rules, the valid distinct-alias fixture removes its dangling foreign edge, and dependency-cycle assertions now construct an actual cycle. Local/external reviewed mapping positives and negative review/hash cases were added before production. These corrections strengthen the obligation and avoid implementing wrong assertions; no test changes occur from the complete red to this green. Existing v1 validator body and apply_batch are unchanged, and the eight assigned regression cases have fresh candidate execution.

## Criterion/type and case decisions

- EM-001: REJECTED; task types integration, unit. V1 graph/reference regression assertions and v2 optional/shared graph, duplicate/cycle/lifecycle checks are substantive, but F3 crashes on malformed v2 history and F2 admits malformed mapping metadata.
- EM-002: APPROVED; task types integration, unit. All four unchanged semantic edit regressions inspect attributable history, transitive invalidation, stable stale/invalid bytes and CAS. Production semantic apply_batch is unchanged. Fresh final green is recorded.
- EM-008: REJECTED; task types unit. Optional/shared v2 edges and explicit execution/product pairs are implemented, but F1 permits contradictory source identity to prove coverage, F2 accepts malformed mapping identity and G1 omits mapped completion/external-reference assertions.
- EM-011: REJECTED; task types unit. Criterion-overlap refusal and reviewed local/external mappings are asserted, but F1 falsely establishes exact concrete-flow coverage using two different declared sources.
- EM-014: REJECTED; task types unit. Exact schema dispatch preserves the original v1 validator and the eight task-assigned v1 regressions pass. New v2 graph acceptance is present, but malformed v2 metadata remains admitted or crashes (F2/F3). Migration is not claimed in this task.
- EM-018: REJECTED; task types unit. The sole assigned unit case lacks its explicit tracker/later reference no-implicit-join assertion (G1). Later intake/network integration cannot substitute for this assigned obligation.

Only task-assigned types are assessed here: later migration/intake/projection/browser/human obligations are not claimed.

### RWB-V2-GRAPH: REJECTED

Checks optional/no intent, one/multiple intents, support without containment, duplicate identity, multiple parents, illegal pairs, containment/dependency cycles, resolved-decision contradiction, scalar/list malformed type/lifecycle and nonmutation. Incomplete for malformed decision history: F3 still raises instead of diagnostics.

Counterexample: Append an open v2 decision with valid options and history entry whose event is []; public validate raises TypeError. Current test does not exercise this malformed-field counterexample.

Continuity: New behavior: all three mapped methods were retained at test-only red 3dc7fb4e130a9c0791dcdb55fbb2da875b964001 with behavior_assertion failures in run 1f74aea3ce7c41998cecd762b03c8bc3. That test and fixture file are byte-identical at final candidate. Earlier test-only corrections strengthened positive/negative obligations and repaired invalid fixtures before production; no assertion weakening between complete red and green. This continuity does not cure the semantic gaps above.

### RWB-QUALIFIED-ID: REJECTED

Checks duplicate explicit execution alias, dangling foreign edge, same-looking task IDs in distinct execution works and no automatic product-ID alias. Does not assert declared-done separation or tracker/later reference no-join/ownership (G1).

Counterexample: A helper that inferred execution from a tracker/later reference, or a projection/helper that fabricated verification for declared done, would not fail the assigned test; those expected assertions are absent.

Continuity: New behavior: all three mapped methods were retained at test-only red 3dc7fb4e130a9c0791dcdb55fbb2da875b964001 with behavior_assertion failures in run 1f74aea3ce7c41998cecd762b03c8bc3. That test and fixture file are byte-identical at final candidate. Earlier test-only corrections strengthened positive/negative obligations and repaired invalid fixtures before production; no assertion weakening between complete red and green. This continuity does not cure the semantic gaps above.

### RWB-FLOW-SELECTION: REJECTED

Checks matching case, wrong digest, active missing case, distinct shared-criterion case refusal, draft gap, reviewed local/external mappings, recursive local digest, pending review and changed body. F1 and F2 show remaining contradictory-source and malformed-selector acceptance.

Counterexample: Point Test.reference.path at an other plan defining a different WB-publish assertion, while declaring work_id product and product digest: validate returns []. A reviewed local mapping case_id [] is also accepted.

Continuity: New behavior: all three mapped methods were retained at test-only red 3dc7fb4e130a9c0791dcdb55fbb2da875b964001 with behavior_assertion failures in run 1f74aea3ce7c41998cecd762b03c8bc3. That test and fixture file are byte-identical at final candidate. Earlier test-only corrections strengthened positive/negative obligations and repaired invalid fixtures before production; no assertion weakening between complete red and green. This continuity does not cure the semantic gaps above.

### RWB-V1-VALID: APPROVED

Unchanged actual existing regression asserts: Accept broad v1 typed model and external references. Source file is byte-identical to accepted baseline; task final-green record passed this case.

Counterexample: Rejecting original valid broad v1 definitions would fail this unchanged positive baseline.

Continuity: Unchanged regression: test_engineering_model.py is byte-identical from accepted contract through red and final candidate; fresh final green run 84b180c7ecac453c80fabf37306c4eee passed. No TDD exemption or inherited historical pass is used.

### RWB-V1-GRAPH: APPROVED

Unchanged actual existing regression asserts: Reject duplicate/broken identities, illegal edges/cardinality and cycles with unchanged input. Source file is byte-identical to accepted baseline; task final-green record passed this case.

Counterexample: Allowing duplicate/broken IDs, illegal cardinality or cycles would miss explicit existing diagnostic assertions.

Continuity: Unchanged regression: test_engineering_model.py is byte-identical from accepted contract through red and final candidate; fresh final green run 84b180c7ecac453c80fabf37306c4eee passed. No TDD exemption or inherited historical pass is used.

### RWB-V1-FIELDS: APPROVED

Unchanged actual existing regression asserts: Reject malformed required fields and lifecycle conflicts. Source file is byte-identical to accepted baseline; task final-green record passed this case.

Counterexample: Accepting malformed required fields/lifecycle contradicts existing negative diagnostics.

Continuity: Unchanged regression: test_engineering_model.py is byte-identical from accepted contract through red and final candidate; fresh final green run 84b180c7ecac453c80fabf37306c4eee passed. No TDD exemption or inherited historical pass is used.

### RWB-V1-REFS: APPROVED

Unchanged actual existing regression asserts: Reject escaping references and missing canonical criterion. Source file is byte-identical to accepted baseline; task final-green record passed this case.

Counterexample: Accepting escaping reference paths or missing canonical criteria contradicts existing integration checks.

Continuity: Unchanged regression: test_engineering_model.py is byte-identical from accepted contract through red and final candidate; fresh final green run 84b180c7ecac453c80fabf37306c4eee passed. No TDD exemption or inherited historical pass is used.

### RWB-V1-DECISION: APPROVED

Unchanged actual existing regression asserts: Persist attributable decision history and task blocker propagation. Source file is byte-identical to accepted baseline; task final-green record passed this case.

Counterexample: Dropping attributable decision history or task blocker propagation contradicts retained-state assertions.

Continuity: Unchanged regression: test_engineering_model.py is byte-identical from accepted contract through red and final candidate; fresh final green run 84b180c7ecac453c80fabf37306c4eee passed. No TDD exemption or inherited historical pass is used.

### RWB-V1-REVISE: APPROVED

Unchanged actual existing regression asserts: Invalidate transitive dependent decisions after revision. Source file is byte-identical to accepted baseline; task final-green record passed this case.

Counterexample: Keeping a transitive dependent decision resolved after revision contradicts explicit invalidation assertions.

Continuity: Unchanged regression: test_engineering_model.py is byte-identical from accepted contract through red and final candidate; fresh final green run 84b180c7ecac453c80fabf37306c4eee passed. No TDD exemption or inherited historical pass is used.

### RWB-V1-STALE: APPROVED

Unchanged actual existing regression asserts: Invalid or stale edits preserve exact stable bytes. Source file is byte-identical to accepted baseline; task final-green record passed this case.

Counterexample: Publishing invalid/stale bytes contradicts exact stable-file preservation assertions.

Continuity: Unchanged regression: test_engineering_model.py is byte-identical from accepted contract through red and final candidate; fresh final green run 84b180c7ecac453c80fabf37306c4eee passed. No TDD exemption or inherited historical pass is used.

### RWB-V1-CAS: APPROVED

Unchanged actual existing regression asserts: Concurrent compare-and-swap publishes only one valid successor. Source file is byte-identical to accepted baseline; task final-green record passed this case.

Counterexample: Both concurrent edits publishing contradicts one-success CAS and persisted winner checks.

Continuity: Unchanged regression: test_engineering_model.py is byte-identical from accepted contract through red and final candidate; fresh final green run 84b180c7ecac453c80fabf37306c4eee passed. No TDD exemption or inherited historical pass is used.

## Boundary and inventory

All task-produced source changes are owned RWB-101 paths: engineering-model documentation, validation/domain, new identities/flows, new fixture and test module. The sole additional committed path is the explicitly permitted coordinator state bootstrap. No glob-too-narrow or source extras finding. Candidate accepted spec/test-plan/TaskGraph/delegation digests still match the authority pin.

Changed Python inventory:

- `_ask/scripts/engineering_model/domain.py`
- `_ask/scripts/engineering_model/flows.py`
- `_ask/scripts/engineering_model/identities.py`
- `_ask/scripts/engineering_model/validation.py`
- `_ask/tests/revising_fixture.py`
- `_ask/tests/test_revising_model.py`

Changed mapped cases are exactly RWB-V2-GRAPH, RWB-QUALIFIED-ID and RWB-FLOW-SELECTION. No unmapped cases or inventory exclusions. Machine input uses the deterministic inventory/source binding helpers but its semantic decisions were independently authored.

## Required remediation

Add failing behavior assertions for F1–F3 and missing mapped G1 obligations before fixing production. Keep valid genuine cross-work mapping positive coverage separate from contradictory-path rejection. Type/identity checks must reject malformed inputs without fabricating assertions or relaxing v1 valid behavior. Re-run current task final green and obtain fresh independent review bound to the corrected candidate. Do not integrate this rejected candidate.
