# RWB-107 independent complete-task review

- Reviewer: `/root/review_rwb107`; runtime: Codex; model: GPT-6 family, exact selectable identifier unavailable. Configured review selection: `gpt-6.1-sol`/high. Parent model exact identifier unavailable.
- Candidate: `6f807cf9e95547356e8004148ac92212f478e3c2`.
- Original recorded task base: `bf197e62a7cfcb7046901535e1e16ea1c4c6cebf`.
- Accepted contract/inventory base: `54d2e10c9f80317967426acab37b3017d55aaa2b`.
- TaskResult: `work/revising-workbench/inner-loop/results/RWB-107.json`.
- TaskResult byte SHA256: `9ed2a3c1f715383c19c5a23c92f91de40ac45344cf3717cc64efa693e596821b`.
- TaskResult canonical JSON SHA256: `4ec32ff0941eef1671ef6810d261574a133db7896cd87d1f4b81447d16535f32`.
- Policy: `_ask/policies/delegation.md`, pinned SHA256 `ba6fc8e139606df8d5db7fcbc19dc42655ec49a3c9c6523baf3ac15c27f44107`.
- Canonical spec digest: `549e490b2e013957fea941921d41d48338d7faca98cf3e98d5baa5cfbf4475a1`.
- Canonical plan digest: `5af89843427a100e5b90c164167217520ad33ba88ad1721cf91022e91ed6809d`.
- TaskGraph digest: `8effd240d9f62408e618831dd705b5ff806ec6f7ea5ae77f6fb62eae522483aa`.
- Structured review: `work/revising-workbench/inner-loop/evidence/RWB-107-test-review-6f807cf.json`, canonical digest `d3a50e55c4e6a56895a3f8fd58ee520ff3aad34768427cd26c4fdbc5f021b3a5`.
- Verdict: **APPROVED / boundary ok**. No remaining blocking findings, extras requiring reversion or `glob_too_narrow` findings.

## Complete source and ownership

Reviewed the complete original-base task implementation and accepted amendment history: same-revision source/setup/helper/context/output loading; readable Test/Task presentation; content-sensitive lazy caching; independent candidate-contract authority with base-pinned verifier/imports and candidate CheckPlan; full runtime projection cleanup; first-run and binding-overlay consumer isolation; shared installer target binding; and direct canonical/off-path temporary-root callers.

All changed product/test/documentation paths are within the current accepted RWB-107 ownership, including the newly accepted installer and two temporary-root scripts. Spec/plan/TaskGraph/intent/proposal/pin changes are independently accepted coordinator history; state/results/reviews/logs are explicit runtime exceptions. Serial task ownership and all prior acceptance conditions remain intact.

The installer repair is exactly the approved seam: only its target synchronization subprocess receives `ASK_ROOT="$TARGET" ASK_WORK_ID=`, with TARGET already resolved to an absolute validated consumer path. Other install logic is unchanged. This stops caller verifier context redirecting generated projections into the candidate while preserving consumer-owned binding exclusion/canary behavior. The original binding-overlay script still performs two real installs and asserts its model-binding canary remains.

Each direct canonical/off-path shell test now sets ASK_ROOT to its own TMP for the sync call. Both retain their original generated-content assertions, including canonical-stage preference and the session-only off-path command. I09 runs each real script under deliberately injected child-candidate ASK_ROOT, requires successful execution, exact unchanged projection snapshots and clean tracked/untracked child source after each.

I09 retains all earlier stages: actual forced post-sync failure with exit 97/marker and full projection restoration; successful sync with exact restoration; first-run adoption/refusal checks with candidate-root injection and clean candidate. The shell sync EXIT restoration still covers complete four runtime agent directories, while first-run clears inherited root only for its distinct temporary consumer operations. No output/canary assertion was removed and no integrity-gate exclusion was added.

`load_accepted` accepts the exact immutable candidate and verifies candidate pin equality with external coordinator authority, canonical contract digests and unchanged delegation policy. Verifier code/imports remain snapshotted from recorded task base; accepted obligations and CheckPlan remain candidate-derived. Candidate-only acceptance mutations still reject.

## Semantic and inventory decisions

All five task cases have **APPROVED integration** coverage/type/assertion/counterexample/TDD decisions in the structured review:

- RWB-APP-EVIDENCE: EM-003/EM-005/EM-011, admitted source/setup/helpers and flow identity, criterion-only sibling exclusion, actual digest-authorized observations, explicit historical/invalid/skipped/error/not-run meanings.
- RWB-APP-DECISIONS: EM-002/EM-006/EM-007/EM-010, persisted reasoned decisions/readiness and Task blockers, stale/missing-rationale no-write and historical read-only forms.
- RWB-LAZY-CACHE: EM-012, zero initial source/history scans, lazy selection/cache reuse, content-sensitive source/helper/log freshness and tamper refresh.
- RWB-INNER-LOOP-AMENDMENT: EM-019, reviewed post-base amendment acceptance, original runner identity, normal integration and candidate-only pin refusal.
- RWB-CANDIDATE-SYNC-CLEAN: EM-020 revision 5, actual failure/success cleanup and isolated consumer/temporary-root checks preserving candidate/consumer integrity.

Canonical inventory relative to accepted `54d2e10` requires the changed entrypoints Python source, mapped I08/I09 cases and five explicit exclusions for unchanged existing I05/I06/I07/E01/E02 methods. Only I09 is a behavior change relative to that baseline. The artifact additionally records complete original-base inspected Python/shell source digests, with all installer and actual shell sources bound by the canonical test plan. Current `review_errors` returns `[]`. Required types assigned to other tasks remain required.

## Retained current-contract execution

The read-only report service recognizes exactly these three reports under the accepted revision-5 spec/plan, with no rejected current attempts:

| Run | Immutable source | Canonical report SHA256 | Result |
| --- | --- | --- | --- |
| `af8e9e805092426e94f826b4264187d2` | `532862d3846a9789d2f23ba3fe6a33a494a420cd` | `4a8d9a4902a26e9a075b31216b693270238805c3ebc7edc077fb6bc20a640f22` | I09 collected behavior-red; other four pass |
| `ced3cf058da947bf9431237d3f676f34` | `6d4c8b3fcf0bcd943b409bba16c9449ab712daaa` | `5620a7b87f9a2d83005cd226bc7afcf4ac3da0307137ef929156d342b82a3bd2` | Three UI cases plus amendment collected behavior-red; I09 passes |
| `d4aa6ad8e4524b88a47bab5952b3e553` | `6f807cf9e95547356e8004148ac92212f478e3c2` | `612a55237bd917d0f412129e973f4f4d625ccf4cccee2fff3183463c07b45bc7` | All five pass |

All fifteen case records have matching immutable source and retained log SHA256 values; canonical reports match the ledger. Case/execution/runner/phase/scope/task/candidate bindings agree, all collected successfully and exits match failing/passing cases. Every assigned case has recognized current-contract assertion-red and exact-candidate green.

The I09 red reaches the binding-overlay check after earlier sync/first-run stages pass, then fails on changed candidate Codex projection bytes. Final scopes installer synchronization to the actual target and satisfies the same snapshot/cleanliness assertion. The other red source restores prior UI and base-anchor behavior with unchanged intended Python assertions. These produce the missing-readable-context, missing-reasoned-blocker, missing-captured-output and rejected-approved-amendment assertion failures. Final retains the assertions; no setup error, obsolete contract evidence, regression relabeling or exemption supplies completion.

No tests were run by this reviewer and no source, state, TaskResult, contract or accepted pin was modified. Only the two permitted runtime review artifacts were written. Approval binds this exact candidate and latest TaskResult. Coordinator recording, executed integration, outer Verify and human Accept remain required.

## Runtime-only candidate rebind

Compared previous reviewed source candidate `c5dd130fa60bffb814b595398cab17f080613ac5` to this exact candidate. Only runtime review, TaskResult and state artifacts changed; implementation, test, contract and policy bytes are identical. Independently verified the new exact-candidate final-green report and all five collected passing cases, immutable source/log hashes and ledger binding. The same current-contract red reports remain recognized. This refreshed approval binds the new candidate and latest TaskResult rather than treating the prior candidate review as interchangeable.
