# Independent RWB-103 review: d95d5a8

**REJECTED. Ownership boundary APPROVED.** Reviewer `/root/review_revising_plan`, independently selected `gpt-6.1-sol` / high. Exact candidate `d95d5a82c46f0c61f624fe53c84c7d2e4b7f8fc7`; task base `ec1c2d614e014ade18a54fbfa13c970f77cb0322`; accepted contract/inventory base `5964fbfb56128e95676f0b991852ac58529cb8f8`. Immutable source archive and complete task diff reviewed. Previous c7/958 artifacts remain preserved. Reviewer wrote runtime artifacts only, with no source/state/ref/commit changes.

## Remaining F5b: foreign freshness still stops before final publication

High severity; `engineering_model/actions.py:165-196`. Additional foreign snapshots now receive a pre-action `is_current` check and contribute file signatures to journal observations. This correctly closes the previously reported save immediately after semantic staging. However `recover_locked` checks those observations **before** applying local target changes. Its later candidate/current checks and `_publish` use only the local snapshot closure; the separately captured foreign inputs are still absent there.

Exact-candidate deterministic reproduction uses valid local product and foreign other/story fixture models. Wrap only the actual local target-write timing:

```python
real_write = actions._write_target
fired = []

def foreign_save_before_publication(*args, **kwargs):
    result = real_write(*args, **kwargs)
    if args[1] == "work/product/engineering-model.json" and not fired:
        fired.append(True)
        foreign["nodes"][1]["title"] = "External save after journal freshness check"
        _put(root, "work/other/engineering-model.json", foreign)
    return result

with patch.object(actions, "_write_target", side_effect=foreign_save_before_publication):
    result = associate_subject(root, "product", local.identity["digest"],
        subject={"work_id": "other", "node_id": "story"},
        contribution="Parser support", exclusions=[], actor="human", rationale="Confirm")
```

Observed: external save fires; result is valid with `pre/action/post/publication`; local generation is published and diagnostics are empty. Guards, actual target write, semantic action and publication are real. Only external-save scheduling is controlled. The foreign owning model changed after the last foreign observation check but before final publication.

Bind the actual foreign owner/context/helper closure through the same final publication and recovery freshness mechanism as local inputs. Refusal/recovery must preserve or restore stable local bytes/generation without overwriting the foreign save. An extra early observation check and stored subject digest alone are insufficient. This asks for the already accepted state-changing dependency guard, not a stronger unrelated locking scheme or product scope.

## Prior findings and G1–G4 assessment

All earlier exact examples now pass, apart from this remaining final-publication aspect of F5:

- **F1/F1b:** shared validation now applies to top-level and per-subject bounded detail shapes. Malformed contribution/exclusions/owner clarify; valid explicit and later-only bounded details survive. Duplicate conflicting explicit details clarify.
- **F2:** valid foreign repository context retains its owning snapshot; optional tracker metadata remains separately labeled supplied-unverified/unavailable. No API/network or automatic identity join appears.
- **F3/F3b:** prior history container and event attribution/timestamp shapes are checked before action, with matching defensive domain checks. The mapped malformed matrix preserves bytes and absent generation, with pre-only refusal.
- **F4:** nominal foreign qualified pointers publish against the actual owning snapshot without cloning product nodes or writing the foreign model. Existing missing/ambiguous/unsafe/stale and optional paths remain substantive.
- **F5 after-action example:** the newly mapped real semantic-staging save refuses with `EM007_INPUT_CHANGED` and preserves local bytes/generation. F5b above remains later in the same protected publication sequence.

The consolidated suite substantively addresses prior G1–G4 within the accepted stage-adapter scope:

| Prior gap | Current evidence and assessment |
| --- | --- |
| G1, actual caller/order/no-write | Fresh processes now trace actual adopted adapter enter → real resolver enter/exit → adapter exit for both stages. Known-subject bounded results, later-only bounded proposals, inspection and conflicting identities are driven. Model bytes, HEAD/refs/index, absent intent/explore artifacts and absent published generation are checked. Source inspection confirms the adapter contains no branch/intent/admission operation; canonical pre-operation instruction binding and complete generated bodies are asserted. Recorded fallback/owner conflict are covered by shared resolver unit cases. This is adequate for the shipped read-only adapter plus canonical instruction boundary; arbitrary external LLM behavior remains outside the accepted deterministic scope. |
| G2, positive CLI context | The nonexistent story-a fixture is replaced with known story. Actual CLI asserts resolved purpose, bounded contribution and snapshot; valid foreign owning model/path is asserted. Local actual CLI/stage-adapter parity and malformed JSON data preservation remain. |
| G3, required passage and real guard lineage | Unique required spec now succeeds (also correcting the previous wrong-level state lookup). Tests compare captured input, returned result and retained publication identities. Probes wrap real validation/semantic/post/publication implementations and establish exactly one ordered sequence. Invalid current unsafe context invokes no semantic action; malformed history, missing/ambiguous/unsafe/stale refusals preserve state. The new entry is exercised locally without modifying baseline guards. F5b is the one remaining concrete publication-integrity counterexample. |
| G4, confirmed intent responsibility | Canonical Grill now explicitly carries confirmed qualified subject, source revision, bounded contribution/exclusions/owner into intent before presenting complete intent for approval, through the guarded association path. Generated copies match; documentation and binding assertions exercise this shipped protocol responsibility. The read-only adapter does not auto-write intent or add a fresh-work orchestrator. Existing complete-intent approval/invalidation remains applicable. |

No other accepted-scope semantic blocker was found. Three assigned cases (`RWB-SUBJECT-RULES`, `RWB-FRESH-INTAKE`, `RWB-CONTEXT-CLI`) are now approved. `RWB-ASSOCIATION-PASSAGES` remains rejected for F5b. EM-004 integration, EM-013 unit/integration and EM-018 unit/integration are approved; EM-002, EM-007 and EM-015 integration remain rejected. Every assigned criterion/type and case has a substantive machine assessment.

## Current source, ownership and evidence

All 17 task-diff paths from ec1 fit accepted RWB-103 owned paths. Canonical Explore/Grill and all six generated skill/command bodies match completely. The full accepted-contract Python inventory retains earlier task changes and seven mapped changed cases, with four assigned here; no unmapped test methods or inventory exclusions. No accepted contract/authority, immutable runner, state CAS, FF-only integration or baseline guard restriction is weakened. New additional observation handling preserves ordinary action defaults; its final-publication omission is the blocker above.

Independent immutable-candidate execution:

- `python3 -m unittest _ask.tests.test_revising_intake`: four pass.
- `python3 -m unittest discover -s _ask/tests -p test_engineering_guard.py`: ten pass.

Both ran with ambient PYTHONPATH/PYTHONHOME removed and bytecode disabled. These are fresh exploratory reviewer executions, not replacements for coordinator-retained candidate evidence.

Registered retained red `c57cc149e7e004a7dc5213c62b8404fe9eab914e`, run `af792b39f2544a0e8091b5e0eeec419f`, has three behavior assertion failures (subject rules, fresh intake, association) and CLI pass, all collected successfully. Exact d95 final green `100ba814520e46c8854097a80fd7ab8d` passes all four. Latest red/final test bytes are identical. Canonical ledger/report digests, retained execution-log hashes, every immutable case-source digest and red ancestry independently verify. Earlier original/tracker/remediation assertion history remains preserved; no exemption, regression relabel or weakened assertions are used.

TaskResult, independent `read_candidate` and structural `check_integrable` bind exact d95/base ec1/current pair; `source_changes` was empty at that check. Green collected evidence is accurate but lacks the independently failing final-publication save probe.

Exact evidence paths:

- `work/revising-workbench/inner-loop/results/RWB-103.json`
- `work/revising-workbench/traceability/runs/af792b39f2544a0e8091b5e0eeec419f/results.json`
- `work/revising-workbench/traceability/runs/100ba814520e46c8854097a80fd7ab8d/results.json`

Machine input `work/revising-workbench/traceability/RWB-103-review-input-d95d5a8.json` has exact candidate/spec/plan/source/scope/inventory bindings. `review_errors` reports only deliberate F5b integration/criterion/action-case rejections, with no stale binding or inventory errors. Preserve this rejection, add the final-publication failing counterexample, repair within reviewed ownership or obtain a narrow amendment if necessary, then obtain fresh evidence and independent review. No integration authorization for d95.
