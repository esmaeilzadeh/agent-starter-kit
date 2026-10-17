# Independent RWB-103 review: c7b63a7

**REJECTED. Ownership boundary APPROVED.** Reviewer `/root/review_revising_plan`, independently selected `gpt-6.1-sol` / high. Exact candidate `c7b63a75ab6910d670d43b749f2ccbb6ae3f3e4b`; task base `ec1c2d614e014ade18a54fbfa13c970f77cb0322`; accepted contract/inventory base `5964fbfb56128e95676f0b991852ac58529cb8f8`. Source and probes used an immutable archive, including after the live checkout advanced for remediation. No source, state, refs or commits changed by reviewer.

## F1 — explicit bounded context is discarded

High severity, `engineering_model/context.py:75-132`; EM-013/EM-018 and subject/caller/CLI cases. A valid explicit request for known product/story with `contribution: "Parser only"`, `exclusions: ["UI"]` and qualified execution owner product/WB-003 returns `disposition: "resolved"`, but its contribution is None, exclusions empty and execution owner None. Only recorded-association outputs populate these fields. `requested_owner` is used solely for comparison with an existing association, never to establish or return explicit owner context.

The accepted intake establishes/explains bounded contribution before existing work operations. Validate and retain explicit bounded context (including actual qualified ownership), or clearly request missing/contradictory context. A resolved response with silently discarded supplied scope is insufficient. An explicit subject should retain precedence without silently borrowing an unrelated recorded association's scope.

## F2 — valid foreign source revision is erased

High severity, `context.py:123-136`; EM-013/EM-018/EM-004. The foreign owning model is captured and validated, its snapshot assigned to `external_context`, and its title/relationships used. The unconditional `result["external_context"] = None` then deletes that snapshot. A valid other/story result is resolved with foreign purpose but no foreign inspected revision anywhere; the top-level snapshot still identifies local product. Tracker metadata can also overwrite this field.

Preserve the foreign repository context/revision independently from optional tracker metadata. Foreign definitions must remain bound to their inspected owning snapshot, including through both public context entrypoints. No service call is necessary.

## F3 — malformed prior history reaches the semantic action and throws

High severity, `domain.py:115-117` and `actions.py:331-360`; EM-002/EM-007. Setting current `subject_association = {"history": null}` produces no `validate_current` diagnostics. A legitimate association proposal passes the new precondition; `apply_batch` copies None as history and calls `.append`, throwing uncaught `AttributeError: 'NoneType' object has no attribute 'append'` during action.

Malformed existing association/history must produce safe diagnostics before invoking semantic action, with stable bytes/publication preserved. Review the JSON container/type class rather than special-casing only null. The current whitespace-contribution assertion proves one new-proposal guard but does not cover malformed current association state. Any needed ownership expansion must follow the existing contract-amendment process; do not bypass a gate or silently edit an unowned validator.

## F4 — confirmed foreign association cannot be persisted

High severity, `actions.py:334-336` and matching domain check; EM-013/EM-015 association semantics. The accepted planning design explicitly says foreign subject records are pointers resolved read-only in the owning model. The new guarded action nevertheless insists `subject.work_id == edited work_id`. With valid local product and valid other/story models, associating execution work product with subject other/story refuses `EM018_SUBJECT_ID` at pre-check. The owning product must stay distinct from the execution workstream; writing the association into the foreign model instead does not represent the local execution association.

Support the accepted pointer association through the guarded entry, using the actual captured owning context and required contribution passages without cloning product nodes or modifying the foreign model. Missing/unavailable/conflicting foreign context should remain explicit and refuse dependent writes.

## Exact independent reproductions

Run against the immutable c7 candidate using its existing fixture:

```python
from pathlib import Path
import json, tempfile
from _ask.tests.test_revising_context import _repo, _put
from _ask.scripts.engineering_model.context import resolve
from _ask.scripts.engineering_model.admission import validate_current
from _ask.scripts.engineering_model.actions import associate_subject

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    _repo(root)
    result = resolve(root, "product", {
        "explicit_subjects": [{"work_id": "product", "node_id": "story"}],
        "contribution": "Parser only", "exclusions": ["UI"],
        "execution_owner": {"work_id": "product", "task_id": "WB-003"}})
    # F1: resolved, but bounded fields are None / [] / None.

    foreign = json.loads((root / "work/product/engineering-model.json").read_text())
    foreign["work_id"] = "other"
    _put(root, "work/other/engineering-model.json", foreign)
    assert not validate_current(root, "other")[1]
    result = resolve(root, "product", {
        "explicit_subjects": [{"work_id": "other", "node_id": "story"}]})
    # F2: resolved, purpose Outcome, external_context None, no foreign revision.
    current, errors = validate_current(root, "product")
    assert not errors
    result = associate_subject(root, "product", current.identity["digest"],
        subject={"work_id": "other", "node_id": "story"},
        contribution="Parser only", exclusions=[], actor="human", rationale="Confirmed")
    # F4: valid False, steps [pre], EM018_SUBJECT_ID.

    document = json.loads((root / "work/product/engineering-model.json").read_text())
    document["subject_association"] = {"history": None}
    _put(root, "work/product/engineering-model.json", document)
    current, errors = validate_current(root, "product")
    assert not errors
    associate_subject(root, "product", current.identity["digest"],
        subject={"work_id": "product", "node_id": "story"},
        contribution="Parser only", exclusions=[], actor="human", rationale="Confirmed")
    # F3: uncaught AttributeError NoneType.append.
```

The foreign fixture deliberately preserves canonical product references/case IDs. Its own capture has zero diagnostics; valid qualified cross-work references are already supported. No guard, resolver or action implementation is mocked in these probes.

## Planned assertion gaps

- **G1, fresh intake:** The fresh subprocess correctly calls the adopted adapter for both stages. Its trace contains only resolver-enter/exit, with no adopted-caller event or existing branch/intent/admission boundary probes. Only inspection/chooser and conflicting IDs are driven. Field-presence assertions do not prove meaningful bounded context. Add the successful known-subject/recorded/bounded output and later-only no-write paths, plus actual existing-operation boundaries and no admission/assignment publication checks. Canonical stage instructions do place the adapter before writes, but tests must substantiate the accepted caller ordering obligation.
- **G2, context CLI:** The supposed positive parity request names `story-a`, which is absent from `_repo` (the node is `story`). It compares two clarification outputs, without asserting a successful qualified subject or owning revision. Test known local and valid foreign subjects, useful diagnostics and captured identity parity. Malformed JSON/model-byte preservation already works.
- **G3, association passages/registry:** Existing optional success and missing/duplicate-role/unsafe/stale refusals are substantive. There is no successful required uniquely resolved passage association. The new real entry is not exercised against an invalid current model as part of a stage-local guard matrix; callback noninvocation and retained input/result/publication lineage are not asserted. Returned step labels alone do not establish that full lineage. Extend the introducing task's real-entry checks, preserving the unchanged baseline registry.
- **G4, confirmed intent recording:** Accepted spec/design require the confirmed association's bound context in intent. The implementation writes only the model; shipped 00/01 bindings do not explain or exercise the subsequent confirmed-association intent-recording responsibility. Make that existing protocol responsibility concrete and reviewable; fresh-work orchestration remains outside scope.

These are missing accepted obligations, not new product scope. The machine review rejects all four assigned cases and the affected criterion/type assessments; genuine partial coverage is recorded explicitly.

## Verified strengths, evidence and boundary

The c7 tracker correction is sound: supplied data is labeled unverified or unavailable; branches, trackers and later proposals do not infer ownership or call external services. The actual `./ask stage-intake` adapter and model CLI share a read-only resolver. All six generated Explore/Grill skill/command bodies include the **complete exact canonical stage body**, not merely the new token. Nominal local associations record attribution/contribution/input digest through the common guard. The new precondition rejects several malformed proposal fields before action. Shared publication machinery and accepted authority/runner/CAS/FF rules are not changed.

I independently executed `python3 -m unittest _ask.tests.test_revising_intake` in the clean c7 archive: all four collected cases pass. This does not override the additional failing probes above.

Retained, coordinator-ledger-registered evidence independently verified:

- Initial test-only `15a4a5b0b475a5f62ebfb9c3dad7ca975b49a2ef`, run `b7bbcf2e28c146469ac6d9387a776ae9`: all four behavior assertion failures before implementation.
- Additive tracker correction test-only `29b94642fd9ea1db858d106f464b7ebddf0d0c52`, run `aae20776f485426da350b3bb1d985a0f`: one subject-rule assertion failure and three passes.
- Exact c7 final green `b36de66829a347eab082b85a3204891d`: all four cases pass.

Canonical report/ledger digests, retained log hashes, immutable case-source hashes and both red ancestries match. Latest red/final test bytes are identical. TaskResult was observed bound to c7/base ec1 and this latest pair. During review, live HEAD advanced to 900cee2 for remediation while TaskResult remained c7; live `read_candidate` therefore correctly refused candidate mismatch. Standalone TaskResult structural `check_integrable` passes and current `source_changes` is empty. That runtime drift is not a frozen-c7 source defect, and no current integration-readiness claim is made.

All **17 task-diff paths** from ec1 to c7 fit accepted RWB-103 ownership. No source extras. Accepted-contract Python inventory also includes earlier RWB-102 changes, explicitly retained from their independent reviews; it contains seven mapped changed cases overall, four assigned to this task, and no unmapped methods. The machine artifact uses this exact parser-required inventory rather than a task-only shortcut. Every selected criterion/type is assessed: EM-002 integration, EM-004 integration, EM-007 integration, EM-013 unit/integration, EM-015 integration, EM-018 unit/integration.

Machine input `work/revising-workbench/traceability/RWB-103-review-input-c7b63a7.json` has exact candidate/spec/plan/source/scope/inventory bindings. `review_errors` reports only deliberate semantic rejections, with no stale binding or inventory errors. Preserve this rejection and obtain corrected red/green evidence plus fresh independent review; no integration authorization for c7.
