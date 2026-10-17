# RWB-107 independent complete-task review

- Reviewer: `/root/review_rwb107`; runtime: Codex; model: GPT-6 family, exact selectable identifier unavailable. Configured review selection: `gpt-6.1-sol`/high. Parent model exact identifier unavailable.
- Candidate: `cdd39795845e0589d6e0c38c4b2c219728dab822`.
- Recorded task base: `bf197e62a7cfcb7046901535e1e16ea1c4c6cebf`.
- Accepted contract/inventory base: `daa4e8188793599faf5a1e355788213002dd808f`.
- TaskResult: `work/revising-workbench/inner-loop/results/RWB-107.json`.
- TaskResult byte SHA256: `2137818494a1ed14f8c1acb3ec554f6a4d58519063daa0a5c3404bcc1e8c6690`.
- TaskResult canonical JSON SHA256: `f3231685fb7ec95f3f9830423e4a8bd7017647fb9cfac879f5b27fe0caa30d9d`.
- Policy: `_ask/policies/delegation.md`, pinned SHA256 `ba6fc8e139606df8d5db7fcbc19dc42655ec49a3c9c6523baf3ac15c27f44107`.
- Canonical spec digest: `b2ea24b24259f90bbc3aabc36c5cd0f0df6e16d252fd95c457dfa4485470c911`.
- Canonical plan digest: `0befd96ea5c5ed4715a413017292cb1730be1328b8674f4e47a852583ce2d685`.
- TaskGraph digest: `ef1c6a2729a2d4a179e9fa9c89c67d931a49158865831c4491067d42e8c36e0e`.
- Structured review: `work/revising-workbench/inner-loop/evidence/RWB-107-test-review-cdd3979.json`, canonical digest `fe64a4e3fd323b957480468aaf625cb2656ab1ee41e28dc2a298e675151ba5ba`.
- Verdict: **APPROVED / boundary ok**. Blocking findings: none. Extras: none requiring reversion. `glob_too_narrow`: none.

## Source, scope and authority

Reviewed the complete original-base task diff and current changes, including readable UI source/evidence, reasoned Task blockers, lazy freshness, the accepted-contract anchor repair, both workflow amendments, the new sync-cleanliness case and shell restoration. All changed production/test/documentation paths are in the current accepted RWB-107 ownership: the three UI render/load files, `test_revising_detail.py`, inner-loop `evidence.py`, `test_traceability_entrypoints.py`, `test-sync-runtime-agents.sh`, and the traceability documentation. Source-administrative changes are reviewed spec/plan/TaskGraph/intent/proposal/pin history; additional state/results/reviews/integration evidence are explicit runtime exceptions. Serial task ownership is preserved.

`load_accepted` independently accepts the exact candidate as anchor/candidate. Its pin equals external coordinator authority, canonical contracts match the recorded accepted contract, and policy is unchanged. Verifier code/imports still snapshot from the original task base, while CheckPlan and independently approved obligations come from the immutable candidate. The original gate still rejects candidate-only accepted-pin mutation; no generated-file exclusion or integrity weakening was added.

The current shell check snapshots complete `.cursor/agents`, `.claude/agents`, `.codex/agents`, and `.opencode/agents` directories, including original presence, before synchronization. Its EXIT handler removes temporary generated contents and restores the original directory snapshots on both success and failure. This handles all runtime projections changed by temporary risk/model overrides, rather than restoring only the first observed reviewer file. A forced exit 97 occurs after actual sync calls and model assertions; successful invocation continues through existing Codex effort tests. Existing portable defaults/model assertions remain intact.

I09 creates a disposable detached child checkout of the actual candidate and activates the work-specific overlay. It snapshots every projection file, requires the precise forced-failure status/marker, compares exact pre/post projection bytes and checks tracked/untracked Git cleanliness, then runs the script successfully and repeats both comparisons. Thus the deliberate error reaches actual post-write cleanup and the normal required command remains checked. The final code requires no cleanup behavior in the integration gate itself.

## Semantic and inventory decisions

All five assigned cases have **APPROVED integration** assessments, with explicit per-criterion coverage/type decisions and per-test assertion/counterexample/continuity decisions in the structured artifact:

- RWB-APP-EVIDENCE covers EM-003/EM-005/EM-011: admitted same-revision namespaced source/setup/helpers, canonical flow, criterion-only sibling exclusion, genuine retained output/integrity, historical/invalid states and explicit skipped/error/not-run UI semantics.
- RWB-APP-DECISIONS covers EM-002/EM-006/EM-007/EM-010: persisted attribution/rationale/readiness, actual reasoned Task blocker context, stale/missing-rationale no-write and committed read-only forms.
- RWB-LAZY-CACHE covers EM-012: zero initial source/evidence scans, lazy selected load/revisit reuse, content freshness and same-mtime tamper reevaluation.
- RWB-INNER-LOOP-AMENDMENT covers EM-019: reviewed post-base amendment accepted, base runner identity retained, ordinary integration passes and candidate-only accepted-pin mutation rejects.
- RWB-CANDIDATE-SYNC-CLEAN covers EM-020: full-directory post-failure and post-success restoration, exact bytes and clean immutable child source.

Canonical inventory relative to `daa4e81` requires inspected source `test_traceability_entrypoints.py`, mapped cases RWB-CANDIDATE-SYNC-CLEAN and RWB-INNER-LOOP-AMENDMENT, and five explicit exclusions. Those exclusions are unchanged pre-existing I05/I06/I07/E01/E02 methods in the shared source; their original responsibilities remain and no new unassigned behavior is hidden. Only I09 is an AST behavior change relative to this accepted baseline. The structured artifact also records complete original-base inspected sources/digests, including the shell file outside Python inventory. Current `review_errors` validates the artifact with no errors.

## Current-contract execution and continuity

The current read-only report service recognizes all three red reports and the exact final-green report. All five required cases have a recognized collected behavior-red and exact final pass under the current spec/plan:

| Run | Candidate | Canonical report SHA256 | Outcome |
| --- | --- | --- | --- |
| `2a3daf25f24f48a880b8a9056c81c92b` | `29fea9e831af16309b7fea54fbda60ca672dd827` | `8a11621fe8829d6aab9dc596a2cf2ce5e40ed6ed2facd7d06c0df7cf4a89120d` | Sync case assertion-red; other four pass |
| `bee56115126b4b689a30c4056b926e35` | `c903b2ee0157f36c65ef0038756e80f03a1927d4` | `1add511069e8e889263f40038c60543d6d928e71607d6efc8337888fb573bd35` | Amendment case assertion-red; other four pass |
| `9019915e52144838969b857bea334070` | `512476998910b671512adf85b9b5f5ec9d108284` | `2ce3a64573dfb77aed2702d97f91b24bae7eab6c251ae7f93d8b157d4ed5ddfc` | Three UI cases assertion-red; workflow cases pass |
| `b0205ccb9d8043a5811eabb09c65be90` | `cdd39795845e0589d6e0c38c4b2c219728dab822` | `db06d34b29261e33477db72f9e2b91d4245b48723cd97c7284372f85c27bb170` | All five pass |

All twenty inspected case records have matching immutable Git source and retained log hashes; report digests match the ledger. Case/execution/runner/phase/scope/task/candidate bindings agree. Every execution collected successfully, with expected failure exit 1 or passing exit 0. The report service excludes incomplete collection attempt `accb1367...`; it supplies no TDD history. Older-contract red reports are historical only.

The sync red fails the explicit exit assertion because the old script ignores the newly required deliberate post-sync failure input (returns 0 rather than 97). It does not claim the later cleanup assertions were reached in red. Final retains byte-identical Python test assertions and reaches/passes failure and success exact-restoration/cleanliness assertions; declared shell source changes are independently bound. Other red candidates restore the recorded prior UI or acceptance-anchor production behavior while retaining the final Python assertions. No failed semantic condition was weakened, relabeled regression or exempted.

Final declared source SHA256 values are `024058a56d299d3ada986c8a2641d6d27873891d8f7f670e51fb3a4ae1f9e407` for the UI test, `44290aecabe3ff6bae6e69fb88c1ff641524b864ad50c24ab848a38790cae14e` for entrypoints, and `014546f38e0701e0b5ffae0ad0e52e48b9c5f0c2c3f952ddf935c1b6c972098e` for the shell check. TaskResult's placeholder red command was replaced with concrete immutable candidate invocations before this digest binding.

No tests were run by this reviewer. Only the two runtime review artifacts were written; implementation, state, TaskResult, accepted pins and contracts were untouched. Approval binds this exact candidate and latest TaskResult. Coordinator recording, executed integration, outer Verify and human Accept remain required.
