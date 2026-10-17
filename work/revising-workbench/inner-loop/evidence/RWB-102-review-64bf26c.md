# Independent RWB-102 semantic and ownership review

**REJECTED. Ownership boundary APPROVED. Do not integrate this candidate.**

Reviewer `/root/review_revising_plan`, selected gpt-6.1-sol/high, Codex independent context. Exact candidate `64bf26c40f937c2a662b626529f0824d0f1c5c6e`. Admission base `c2635515f4f4643344b8483b86ea7d8e046d4bab`; accepted contract/inventory base `5964fbfb56128e95676f0b991852ac58529cb8f8`. Full task source review also starts at original `c3c148c4d483d9b8cc9ad50915c81e60ea07abb5`, including WIPf964094 already in the new admission base. Review wrote runtime artifacts only; no source/commit/state/ref mutation.

## Concrete findings

### RWB102-F1 (high) — _ask/scripts/engineering_model/admission.py:204

Persisted resolution text is not bound by Snapshot.identity or recomputed on load. Editing generation manifest passages[spec].resolution.text to a forged contract leaves load_published successful and identity digest unchanged. Bind every displayed derived passage/helper text to captured bytes or checked derivation/digest on persisted reload.

Exact-candidate observation: Forged spec passage returned under original admitted digest.

### RWB102-F2 (high) — _ask/scripts/engineering_model/passages.py:164

Required plan passage compares only selector.task_id with execution.task_id. A Task execution owner changed to foreign still admits using work/product/plan.md rowWB003. Actual plan source must bind qualified execution owner and task, with separately valid foreign-owner plan coverage.

Exact-candidate observation: workflow_admission(selected_execution={foreign,WB-003}) enters action using product-owned plan row.

### RWB102-F3 (high) — .agents/ask/verification/traceability/evidence.py:145

Task review admission is opt-in. record_test_review with selected_execution omitted goes directly to unguarded _record_test_review even for review JSON scope task/task_idWB003. In a valid disposable accepted repo with required context absent, it writes the review record. CLI default workstream scope can likewise disagree with actual task-review body. Derive/validate actual operation task scope and reject contradictory selectors; optional arguments cannot bypass.

Exact-candidate observation: Real task review record created despite missing selected spec passage.

### RWB102-F4 (high) — _ask/scripts/inner_loop/driver.py:145

Actual writer admission does not carry known selected task identity. driver.run_once chooses WB003 then calls state.spawn_writer under generic workflow; cmd_spawn has positional task_id but its decorator only uses optional selector kwargs. Both start the writer with required spec context missing. Gate actual selected-task start before state/publication changes.

Exact-candidate observation: run_once returns running=WB-003; cmd_spawn returns0; both write running state despite missing required context.

### RWB102-F5 (medium) — _ask/scripts/engineering_model/snapshot.py:92

An existing selected commit lacking a safe optional context path is classified selector error, globally invalidating current admission. Safe absent files must remain admitted unavailable limitations and block only dependent actions; retain strict refusal for invalid revisions/nonregular/symlink sources and no current fallback. The current selector test incorrectly expects error for this safe-missing case.

Exact-candidate observation: Safe absent committed docs/context.md yields stateerror and EM001_CONTEXT_SELECTOR.

### RWB102-F6 (medium) — _ask/scripts/engineering_model/passages.py:44

Heading/table discovery treats fenced Markdown examples as actual contract structure. A fenced ##Work breakdown beneath actual #Work resolves available and displays example text including closing fence. Ignore code-fenced structure while preserving literal full-chain/row selection and duplicate ambiguity for real Markdown headings/tables.

Exact-candidate observation: Fenced example heading selected as available contract passage.

### RWB102-F7 (high) — _ask/scripts/engineering_model/snapshot.py:67

Captured closure omits Scenario.case selected work plan; mapping discovery follows only test_case external selectors. A valid foreign selected flow with reviewed foreign-local→product-external mapping passes direct validate but capture omits foreign plan and reports FLOW_CASE. Discover canonical case plans and every referenced mapping endpoint transitively, including missing-state identity; keep owning-model/context dependencies revision-consistent.

Exact-candidate observation: Direct validate []; snapshot lacks work/foreign/test-plan.json and rejects FLOW_CASE.

## Reproduction evidence

Every finding above was reproduced with candidate code from clean temporary Git archives of64bf26c and isolated temporary repositories. Current worker remediation changes are excluded. Reproduction inputs:

- F1: `_repo; s=admit`; edit only selected generation manifest `passages[spec_key].resolution.text`; `load_published` returns forged text and the original digest. Captured file bytes remain unchanged.
- F2: change Task.execution.work_id from product to foreign, retain product plan path/rowWB003; selected execution foreign/WB003 enters real workflow action.
- F3: valid disposable accepted canonical contracts and exact task-review v2 input scope task/task_idWB003; leave docs/context.md absent; omit selected_execution in real record_test_review. The task review file is written.
- F4: `_repo(spec_text=None)` then real driver.run_once returns runningWB003; independently cas_init then real cmd_spawn returns0/runningWB003. Required context absence prevents neither state mutation.
- F5: commit a valid fixture with optional docs/context.md absent, select that real full commit for context; capture returns error and admit emits EM001_CONTEXT_SELECTOR rather than admitted unavailable.
- F6: source bytes `# Work
```text
## Work breakdown
Example only.
```
`; selector Work/Work breakdown returns available example text.
- F7: valid foreign selected plan with reviewed localWBpublish→externalproductWBpublish mapping. Direct validate returns no diagnostics; capture omits foreign plan and emits FLOW_CASE.

## Full source/caller and authority review

Inspected all14 changed Python sources from originalc3c148c, including full passages.py/snapshot.py WIP bodies, all eight amended caller paths, actions/admission and the716-line test module. Worker source stays within amended owned paths. Approved coordinator plan/design/TaskGraph/pin changes and prior-task runtime/state history are explicit exclusions, not WIP exemptions. No extra worker source path or glob-too-narrow finding. Accepted spec/plan/graph/policy still match current authority.

Immutable-base runner snapshot, accepted-ref authority, CheckPlan/case instrumentation, candidate source/log integrity, coordinator CAS lock and FF-only integration mechanics are unchanged. Bridge changes carry explicit selected identity, but actual driver start and review-target omissions lose it (F3/F4); preserving those lower-level gates does not cure the admission bypass. v1 direct integration compatibility has an explicit successful fresh test after its genuine failing red. The v1 atomic edit and all10 assigned generic guard regressions remain fresh green.

The tests now execute meaningful actual traceability/driver/integration/review/model CLI operations instead of only helper surrogates, and prior invalid fixtures/helper freshness expectations are corrected. Registry coverage is still incomplete: writer start and omitted or contradictory review target paths are not tested; exactly-once ordered input/result lineage is asserted only for semantic edit rather than every real foundation route; stale linked/helper action refusal is absent from the new freshness case. Missing tests correspond to reproduced defects, so green cannot establish complete adopted entrypoint coverage.

## Execution and TDD assessment

Independently checked retained run-report canonical digests against the execution ledger, log byte hashes and recorded test-source hashes against Git for attempts through this candidate. Final `ea6618f1d89d4f4f9c91a85527eac00f` contains the exact13 assigned cases, all passed. No dynamic subtests or unmapped cases occur.

Meaningful redb3554cd/run3a59338cbe7c484abf43eae5676486e2 has three new assertion failures plus10 baseline passes: last-validated publication, selected-context response and current observer publication. Subsequent test changes strengthen real caller/identity/legacy coverage and preserve earlier assertions. Latest full-byte red7d0c207/run54aca100d25f41a89a516e84fa606c4a exposes valid-v1 direct integration refusal, while selector/freshness already pass; its exact test bytes equal final64bf26c. Earlier fixture/API/runtime-error runs remain historical rejected attempts; none is used as a substitute for meaningful behavior red. No source/test TDD exemption or regression relabel is used. F5 is a wrong expected disposition in a current assertion and needs correction against the unchanged accepted safe-gap contract, retaining no-fallback requirements.

## Assigned criterion/type decisions

- EM-001: APPROVED; types integration. Assigned unchanged atomic graph/lifecycle batch regression retains original validation semantics and passes current candidate execution. This task-scoped decision does not certify later whole-workstream graph/migration obligations.
- EM-002: REJECTED; types integration. Existing atomic semantic regression remains green, but real writer-start and task-review mutations bypass selected passage admission (F3/F4). New action-case assertions do not cover these actual targets and cannot authorize their writes.
- EM-007: REJECTED; types e2e, integration, unit. Canonical/runner/CAS/FF protections remain, but persisted generation integrity, complete closure and actual selected caller admission fail (F1-F7). Existing generic v1 e2e regressions cannot supply missing v2 registry/order/lineage/refusal evidence.
- EM-015: REJECTED; types integration, unit. Current/committed selector and optional/required semantics have substantial tests, but source-owner binding, safe missing classification, fenced structure, closed capture and caller refusal still fail (F1-F7).

## Assigned case decisions

### RWB-SELECTORS: REJECTED

Tests full chains, exact plan header/row, duplicate ambiguity, malformed shape, current symlink ancestors, real historical regular/missing/symlink blobs, version fields and last-validated view. Missing F1 integrity/F6 fence/F7 closure cases; F5 currently asserts incorrect error for safe absent historical blob.

Counterexample: Fenced example heading incorrectly resolves; safe missing committed context globally errors; forged persisted spec text is trusted under unchanged digest.

Continuity: Meaningful red b3554cd3e8a565729cd314152af696378448c4c6/run3a59338cbe7c484abf43eae5676486e2 has all three new behavior assertion failures and10 baseline passes, targeting last-validated/current publication and selected-context response. Final test adds real integration/identity/v1 positives without dropping earlier assertions. Latest full-byte red7d0c207bcf85fe9dcf728f55b7d2b594a7567fa2/run54aca100d25f41a89a516e84fa606c4a isolates the v1 direct-CLI compatibility failure in action case; selector/freshness pass. Exact test file bytes match final64bf26c, finalea6618f1d89d4f4f9c91a85527eac00f passes all13. Earlier fixture/API/runtime-error attempts are retained but not relied on as behavior red. Semantic defects above remain despite valid continuity.

### RWB-PASSAGE-ACTIONS: REJECTED

Valid canonical fixtures; direct selected edit/workflow refusal and identities, same-ID neighbor refusal, real traceability run/review, actual coordinator review/driver integration, model admit CLI, explicit candidate integration, and valid v1 direct CLI compatibility. However actual writer selection/spawn and omitted/mismatched review target paths bypass; qualified plan owner not checked. Only direct edit has exact phase/count/input-result assertions; no complete stage-local success/refusal lineage registry.

Counterexample: Actual run_once/cmd_spawn start a missing-context Task; direct record_test_review records it when optional selector omitted; foreign execution borrows product plan same-ID row.

Continuity: Meaningful red b3554cd3e8a565729cd314152af696378448c4c6/run3a59338cbe7c484abf43eae5676486e2 has all three new behavior assertion failures and10 baseline passes, targeting last-validated/current publication and selected-context response. Final test adds real integration/identity/v1 positives without dropping earlier assertions. Latest full-byte red7d0c207bcf85fe9dcf728f55b7d2b594a7567fa2/run54aca100d25f41a89a516e84fa606c4a isolates the v1 direct-CLI compatibility failure in action case; selector/freshness pass. Exact test file bytes match final64bf26c, finalea6618f1d89d4f4f9c91a85527eac00f passes all13. Earlier fixture/API/runtime-error attempts are retained but not relied on as behavior red. Semantic defects above remain despite valid continuity.

### RWB-CONTEXT-FRESHNESS: REJECTED

Same-mtime context/helper recapture, current observer/full parity, safe missing→present, selector-only, unique→ambiguous and deletion changes are asserted. Persisted resolution text remains unauthenticated and foreign selected case closure is absent. No actual stale selected action after linked/helper edit or complete case/owner closure assertion.

Counterexample: Edit stored resolution.text without changing admitted identity; foreign valid case plan is omitted from capture, breaking validity and freshness.

Continuity: Meaningful red b3554cd3e8a565729cd314152af696378448c4c6/run3a59338cbe7c484abf43eae5676486e2 has all three new behavior assertion failures and10 baseline passes, targeting last-validated/current publication and selected-context response. Final test adds real integration/identity/v1 positives without dropping earlier assertions. Latest full-byte red7d0c207bcf85fe9dcf728f55b7d2b594a7567fa2/run54aca100d25f41a89a516e84fa606c4a isolates the v1 direct-CLI compatibility failure in action case; selector/freshness pass. Exact test file bytes match final64bf26c, finalea6618f1d89d4f4f9c91a85527eac00f passes all13. Earlier fixture/API/runtime-error attempts are retained but not relied on as behavior red. Semantic defects above remain despite valid continuity.

### RWB-GUARD-PRE: APPROVED

Unchanged collected regression asserts: Action callback is never invoked for invalid current document. Current candidate execution passes; test_engineering_guard.py bytes remain unchanged.

Counterexample: A violation of the explicit retained regression assertion would fail its unchanged public boundary checks; this is not claimed as new selected-passage coverage.

Continuity: Unchanged regression source from original/accepted bases through final; final runea6618f1d89d4f4f9c91a85527eac00f passed. No new-behavior exemption or imported historical pass.

### RWB-GUARD-POST: APPROVED

Unchanged collected regression asserts: Invalid candidate leaves stable generation and bytes unchanged. Current candidate execution passes; test_engineering_guard.py bytes remain unchanged.

Counterexample: A violation of the explicit retained regression assertion would fail its unchanged public boundary checks; this is not claimed as new selected-passage coverage.

Continuity: Unchanged regression source from original/accepted bases through final; final runea6618f1d89d4f4f9c91a85527eac00f passed. No new-behavior exemption or imported historical pass.

### RWB-GUARD-REFS: APPROVED

Unchanged collected regression asserts: Linked specification-only edit invalidates admission. Current candidate execution passes; test_engineering_guard.py bytes remain unchanged.

Counterexample: A violation of the explicit retained regression assertion would fail its unchanged public boundary checks; this is not claimed as new selected-passage coverage.

Continuity: Unchanged regression source from original/accepted bases through final; final runea6618f1d89d4f4f9c91a85527eac00f passed. No new-behavior exemption or imported historical pass.

### RWB-GUARD-EVENTS: APPROVED

Unchanged collected regression asserts: External saves and missed events fail closed through startup/action/read. Current candidate execution passes; test_engineering_guard.py bytes remain unchanged.

Counterexample: A violation of the explicit retained regression assertion would fail its unchanged public boundary checks; this is not claimed as new selected-passage coverage.

Continuity: Unchanged regression source from original/accepted bases through final; final runea6618f1d89d4f4f9c91a85527eac00f passed. No new-behavior exemption or imported historical pass.

### RWB-GUARD-PARITY: APPROVED

Unchanged collected regression asserts: Cached and full validation return equivalent admissions. Current candidate execution passes; test_engineering_guard.py bytes remain unchanged.

Counterexample: A violation of the explicit retained regression assertion would fail its unchanged public boundary checks; this is not claimed as new selected-passage coverage.

Continuity: Unchanged regression source from original/accepted bases through final; final runea6618f1d89d4f4f9c91a85527eac00f passed. No new-behavior exemption or imported historical pass.

### RWB-GUARD-PUBLISH: APPROVED

Unchanged collected regression asserts: Concurrent multifile publication/recovery presents one valid stable generation. Current candidate execution passes; test_engineering_guard.py bytes remain unchanged.

Counterexample: A violation of the explicit retained regression assertion would fail its unchanged public boundary checks; this is not claimed as new selected-passage coverage.

Continuity: Unchanged regression source from original/accepted bases through final; final runea6618f1d89d4f4f9c91a85527eac00f passed. No new-behavior exemption or imported historical pass.

### RWB-GUARD-BOOTSTRAP: APPROVED

Unchanged collected regression asserts: Bootstrap admits only validated state. Current candidate execution passes; test_engineering_guard.py bytes remain unchanged.

Counterexample: A violation of the explicit retained regression assertion would fail its unchanged public boundary checks; this is not claimed as new selected-passage coverage.

Continuity: Unchanged regression source from original/accepted bases through final; final runea6618f1d89d4f4f9c91a85527eac00f passed. No new-behavior exemption or imported historical pass.

### RWB-GUARD-BATCH: APPROVED

Unchanged collected regression asserts: Atomic node/edge/lifecycle batch preserves model and semantic invariants; Atomic node/edge/lifecycle batch preserves model and semantic invariants; Atomic node/edge/lifecycle batch preserves model and semantic invariants. Current candidate execution passes; test_engineering_guard.py bytes remain unchanged.

Counterexample: A violation of the explicit retained regression assertion would fail its unchanged public boundary checks; this is not claimed as new selected-passage coverage.

Continuity: Unchanged regression source from original/accepted bases through final; final runea6618f1d89d4f4f9c91a85527eac00f passed. No new-behavior exemption or imported historical pass.

### RWB-GUARD-ORDER: APPROVED

Unchanged collected regression asserts: Exactly one pre/action/post/publication succeeds in order against captured identities. Current candidate execution passes; test_engineering_guard.py bytes remain unchanged.

Counterexample: A violation of the explicit retained regression assertion would fail its unchanged public boundary checks; this is not claimed as new selected-passage coverage.

Continuity: Unchanged regression source from original/accepted bases through final; final runea6618f1d89d4f4f9c91a85527eac00f passed. No new-behavior exemption or imported historical pass.

### RWB-GUARD-ENTRYPOINTS: APPROVED

Unchanged collected regression asserts: All enumerated public mutation and workflow wrappers refuse bypass. Current candidate execution passes; test_engineering_guard.py bytes remain unchanged.

Counterexample: A violation of the explicit retained regression assertion would fail its unchanged public boundary checks; this is not claimed as new selected-passage coverage.

Continuity: Unchanged regression source from original/accepted bases through final; final runea6618f1d89d4f4f9c91a85527eac00f passed. No new-behavior exemption or imported historical pass.

## Machine evidence and handoff

Exact source digests, accepted-base inspected inventory, full-original-base source inventory, all criteria/types/cases and semantic decisions are in `traceability/RWB-102-review-input-64bf26c.json`. Changed mapped methods are exactly the three new cases; no unmapped exclusions. Parser rejects only intended semantic decisions, with no stale candidate/spec/plan/source/inventory errors.

Required remediation: genuine failing assertions for F1-F7 and missing real registry paths, source fixes within current amended ownership, fresh final green and independent review bound to the corrected SHA. Preserve this rejection and its evidence. No integration authorization for64bf26c.
