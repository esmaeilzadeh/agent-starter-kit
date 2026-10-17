# Independent review: WB-003

## Attribution and identities

- model: gpt-6-astra; runtime: codex; parent_model: gpt-6-luna
- reviewer: /root/review_wb001
- work_id / task_id: structured-agentic-environment / WB-003
- task base_sha: b9644b94da99dc6752a5f5a01cdd59e3e19d74a6
- candidate_sha: 0e9614eb6d364f5541ffbe2b48d69347518eeb6f
- accepted contract / semantic inventory base_sha: 55c11fad3e0391f8a47236166c8d5941d824ef73
- TaskResult: work/structured-agentic-environment/inner-loop/results/WB-003.json
- TaskResult SHA-256: e30de56e49eb77cd919c7ea1e525c2bb4880feace23e7b97b32509fc0c0b37ac
- spec_digest: f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb
- plan_digest: 4845c9f46fb7ecfe4f368e006c1a8d89b2f7c3ea5beefe1478b08ea184eb09e8

## Boundary

boundary: ok

The exact task-base/candidate name-only diff contains only the accepted owned files `_ask/scripts/engineering_model/workbench_evidence.py` and `_ask/tests/test_engineering_workbench_evidence.py`. All findings can be addressed within that boundary.

The semantic inventory uses the accepted pin rather than the task base and consequently includes inherited WB-002 sources/cases. Those inherited paths were independently reviewed previously; the v2 JSON preserves the actual inventory without expanding current implementation-review scope. There are no unmapped cases or exclusions.

## R1 — Contradictory run/source commit identity accepted (blocking, high)

Location: workbench_evidence.py:209, together with the report/ledger checks at line 164.

The adapter checks report candidate equals ledger candidate and execution source equals case source, but never checks that the execution source equals the report candidate. A record can therefore attach execution/source bytes from commit A to a report attributed to commit B while receiving output_status=valid.

Independent disposable reproduction used the task fixture builder with candidate_sha=current and source_sha=older. Report/ledger/log digests were internally consistent, and source digests correctly matched the older commit. The returned row contained the current report candidate and older source_sha, output_status=valid and diagnostic=None. Applicability stale does not repair contradictory run attribution: the original retained execution contract binds each case/execution to its report's source candidate.

Fix: require one immutable commit identity across report candidate, ledger candidate, execution source and case source before accepting detail, and add a discriminating mismatch assertion. Preserve honest raw failure information while labeling inconsistent evidence invalid; do not claim shared evaluator approval merely from source/log digest agreement.

## R2 — Historical executions labeled current after production changes (blocking, high)

Location: workbench_evidence.py:248, especially lines 253–262.

Execution applicability is derived only from equality of test-source digests and whether the requested candidate equals HEAD. The actual row's run/source candidate is ignored. Thus an older passing execution becomes applicability=current when production changes but tests remain unchanged.

Independent disposable reproduction recorded a run at the fixture's current candidate, committed only a new src/app.py value without changing test_sample.py, then inspected the new HEAD. The returned row retained the older run candidate but reported source_status=current and applicability=current. The selected implementation was never executed by that retained run.

Fix: keep test-source equality and actual execution currency separate. Compare the retained run's source/candidate with the inspected candidate, and preserve historical applicability when they differ even if test bytes match. Do not translate an old outcome into evidence for the newer implementation.

## R3 — Ancestor work-directory symlink bypasses evidence confinement (blocking, medium)

Location: workbench_evidence.py:132 and the reads at lines 140, 161 and 229.

The root check compares runtime.resolve() with `(root/work/work_id).resolve()`. If work/work_id itself is a symlink to an external directory, both resolve into that external directory and the check passes. Direct runtime/report/log symlink checks do not detect this ancestor. The final log containment check likewise compares against the external resolved runtime.

Independent disposable reproduction created a valid fixture report/log, moved work/w into a separate temporary directory and replaced work/w with a directory symlink. execution_history read the external ledger/report/log and returned status=available, output_status=valid and no diagnostic. This violates repository/snapshot confinement while presenting the outside files as the selected workstream's evidence.

Fix: establish confinement against the supplied resolved repository root before any ledger/report/log content read, including ancestor paths. Add a test proving no external content read occurs through work or work/<id> ancestor symlinks. The existing direct-file checks should remain.

All three independent reproductions used only disposable test-owned repositories and directories. No real external file, workspace source, refs or coordinator state was changed.

## Assertion and authority assessment

- WB-evidence-identity / EM-003 and EM-011 unit: work/test/selector/runner/run/contract filters are useful but omit R1. Rejected pending a discriminating inconsistent-source record.
- WB-source-version / EM-011 unit: historical/current full class/method extraction distinguishes same-named methods and avoids current-source substitution; unavailable revision/traversal states are explicit. This tested slice is approved.
- WB-evidence-states / EM-003, EM-011 and EM-012 integration: actual failure/skip outcomes, tampered logs, refreshed retained runs and changed test-source staleness are asserted, but R2 and R3 are omitted. Rejected. Missing timing fields are represented in implementation but currently lack explicit assertions.

The module consistently leaves completion=not_evaluated. That is an honest separation from shared evaluator/completion authority, and this review grants no completion meaning to raw retained output. The blocking findings concern correctness of the adapter's own identity, applicability and confinement claims.

## Retained red/green evidence

Accepted red: 7bb07cdc57204777919381371c0f2324 at source 754520d49298ba3608502527225e6ed1aa6255e6.

- Current accepted spec/plan digests; scope task / WB-003.
- phase red; collection_status ok; exit_code 1.
- All three assigned cases fail by behavior_assertion.
- Log: work/structured-agentic-environment/traceability/runs/7bb07cdc57204777919381371c0f2324/f370f5722316424b91ef59bb8ab7e4d3.log
- Verified log SHA-256: e5b9c992898d2af370f1c1bf1466f63357cf6abb09beddfeb81d98dc02a008ec

Candidate final green: bb7f280329f0405789f6080d159ef37b at source/candidate 0e9614eb6d364f5541ffbe2b48d69347518eeb6f.

- Current accepted spec/plan digests; scope task / WB-003.
- phase final_green; collection_status ok; exit_code 0.
- All three assigned cases pass.
- Log: work/structured-agentic-environment/traceability/runs/bb7f280329f0405789f6080d159ef37b/77cad12336a6451fa77ed9a362436f79.log
- Verified log SHA-256: d9c5b849b89c9403f54eacecf26337ec6e22f6987beaa3a1b1aced7ea74ad6b8

The TaskResult agrees with both reports. Every case source digest matches git show at its recorded revision. Mapped test bytes are identical between accepted red and candidate green, SHA-256 c513dc60c7ba6f8df49ff07f80761dd361f912051d96b70bfaacd78b56a7e7e1. Earlier setup/runtime-error history is not used; no exemption is requested or granted. These authentic outcomes do not cover the independently reproduced counterexamples.

## Semantic artifact and verdict

Artifact: `work/structured-agentic-environment/traceability/review-input-WB-003-0e9614e.json`.

It is task-scoped ask-test-review/v2 with the exact three selected test IDs, EM-003/EM-011/EM-012, matching source/candidate/result digests and actual accepted-pin inventory. It records rejected criterion/identity/state coverage and approved qualified-source assertions rather than fabricating an all-approved record. Read-only validation reports semantic rejection, without source-binding or inventory errors.

verdict: REJECTED

boundary: ok

Resolve R1–R3 and submit a new committed candidate with discriminating red/green evidence before integration. This reviewer made no source edits, commits, coordinator recordings or state changes.
