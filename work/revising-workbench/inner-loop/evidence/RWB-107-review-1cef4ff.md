# RWB-107 independent complete-task review

- Reviewer: `/root/review_rwb107`; runtime: Codex; model: GPT-6 family, exact selectable identifier unavailable. Configured review selection: `gpt-6.1-sol`/high. Parent model exact identifier unavailable.
- Candidate: `1cef4fff0a15267177aadfdd0e433d9c71c13284`.
- Original recorded task base: `bf197e62a7cfcb7046901535e1e16ea1c4c6cebf`.
- Accepted contract/inventory base: `3d2949e85e8e08932db1fe2d6b7f333d7bec42fa`.
- TaskResult: `work/revising-workbench/inner-loop/results/RWB-107.json`.
- TaskResult byte SHA256: `fc9d3cf768c4254bccd10b64f14ab916ee79a633e34069c0cbcba17126a81781`.
- TaskResult canonical JSON SHA256: `d10744acd74cdb61565b80a06e31ea0fa96d5028962c4291a1c0bbc67fb3ece1`.
- Delegation policy: `_ask/policies/delegation.md`; pinned SHA256 `ba6fc8e139606df8d5db7fcbc19dc42655ec49a3c9c6523baf3ac15c27f44107`.
- Canonical spec digest: `ef61929ead5e8a5e52fb431f830a71ccc4f30fcba08daf4604298ce79fe77687`.
- Canonical plan digest: `dea83a9607dc9654b2ae70d1f2126a845af9b5cc22af8ba0a5a20e0928f3d77c`.
- TaskGraph digest: `7220567a2cda4c0f092ff89b04c10a40fbe59aa74429147c6b1cf3bd39df245e`.
- Structured review: `work/revising-workbench/inner-loop/evidence/RWB-107-test-review-1cef4ff.json`; canonical digest `bc600ebdf07cf8807ccf5a4262864ed4b4afe209154a2f74a763fa07807154e4`.
- Verdict: **APPROVED / boundary ok**. No blocking findings, scope extras requiring reversion or `glob_too_narrow` findings.

## Complete source and authority assessment

The complete original-base task diff remains reviewed: captured same-revision test/helper/context/output loading; readable test/Task presentation; content-sensitive lazy caching; independent candidate pin authority; base-pinned verifier/imports; candidate CheckPlan; full runtime projection cleanup; I09 and actual first-run consumer isolation; and the corresponding accepted amendments/documentation. Changed implementation/test/documentation paths are inside the current accepted RWB-107 ownership. The added first-run shell path is specifically authorized by the independently reviewed revision-4 amendment. Additional spec/plan/TaskGraph/intent/proposal/pin paths are accounted-for coordinator changes; runtime state/results/reviews/logs are explicit policy exceptions. The task remains serialized.

Independently called `load_accepted` for the exact candidate: its pin matches the external coordinator authority, canonical spec/plan/graph match the accepted contract and policy remains unchanged. No candidate-only obligation authority, generated-path ignore rule or candidate-integrity weakening is introduced.

The new delta since `11010f7` is narrow. `_ask/tests/test-askit-first-run.sh` clears inherited `ASK_ROOT` before operating in its separate non-git/temporary consumer directories. Its existing refusal and explicit-adoption assertions remain intact. I09 deliberately invokes that actual shell script with `ASK_ROOT` set to the candidate child, requires exit 0, compares every runtime projection against the original snapshot and requires no tracked/untracked candidate changes. The sync subprocess still receives the explicit child root, and the first-run script then drops that root for its own separate consumers. These are the correct distinct fixture boundaries.

The existing shell sync check still snapshots/restores entire four runtime agent directories through EXIT. I09 still requires post-sync forced failure exit 97/marker, exact projection restoration and clean child state, then successful sync with the same conditions. The added first-run step runs after both assertions rather than replacing them.

## Semantic decisions and inventory

All five cases have **APPROVED integration** coverage/type/assertion/TDD decisions in the structured artifact:

- RWB-APP-EVIDENCE, EM-003/EM-005/EM-011: real admitted v2 source/setup/helper/flow inspection, criterion-only sibling exclusion, same-mtime helper invalidation, digest-authorized retained output and honest observation/provenance states.
- RWB-APP-DECISIONS, EM-002/EM-006/EM-007/EM-010: actual reasoned Task blocker context, persisted actor/rationale/readiness, missing-rationale/stale no-write and committed read-only inspection.
- RWB-LAZY-CACHE, EM-012: no Overview source/history scans, selected lazy loading/revisit reuse and content-sensitive tamper refresh.
- RWB-INNER-LOOP-AMENDMENT, EM-019: approved post-base amendment accepted, actual base runner identity, unamended pass and candidate-only accepted-pin refusal.
- RWB-CANDIDATE-SYNC-CLEAN, EM-020 revision 4: actual failure/success sync restoration and actual first-run consumer execution under injected verifier root without candidate writes.

Canonical inventory relative to accepted `3d2949e` requires the changed entrypoints Python source, mapped I08/I09 cases and five explicit exclusions for unchanged existing I05/I06/I07/E01/E02 methods. The artifact records each exclusion and additionally binds complete original-base inspected source digests, including both shell scripts. Source paths for I09 include the Python method and both actual shell checks. Current `review_errors` returns `[]`. Other tasks' unit/e2e obligations remain required.

## Current-contract retained execution

The current report service recognizes exactly the four reports below under the revision-4 contract, with no rejected current attempts. Together they supply recognized assertion-red and exact final green for every assigned case:

| Run | Immutable source | Canonical report SHA256 | Result |
| --- | --- | --- | --- |
| `a97f075a28054758ab5bf8eb7c082ed1` | `afd7d26193bb73226f845de8717a4bbbc3513303` | `33a2cb8b08047008fad6febd46c623195ffc440b23a2b891220eb31cb41496b9` | Sync/first-run case behavior-red; others pass |
| `876e60e7013e40f39ba5b6fc26fafb21` | `392408e13cdad3ec414a1684549d3ef1719d1df3` | `e13ca441a61fd6cfa1d9cb22534f27c270387966f108151b78b1d3d1677233c3` | Amendment case behavior-red; others pass |
| `c202bfb3681143b194c22696df7eb062` | `a6c400569573ac467d107747b1d90256c8623b38` | `8ea03c8e166331c9a91fb22454c9ccfdac3144d65ec81cc1e5e50074de11c0a1` | Three UI cases behavior-red; others pass |
| `4d2350aa00a24213841145688669624f` | `1cef4fff0a15267177aadfdd0e433d9c71c13284` | `dfe79fbed05d16cb3e9bc2696fb248666982df94d1e5c54f686eee27c85c07bc` | All five pass |

All twenty case records have matching immutable Git source and retained-log SHA256 values. Canonical reports match the ledger. Execution/case/runner/source/phase/scope/task bindings agree; all collected successfully with expected failure exit 1 or success exit 0.

The current first-run red reaches and passes both sync stages, then fails on genuine changed candidate projection bytes: the Codex reviewer model/effort changes under inherited `ASK_ROOT`. Final retains identical Python assertions and unsets that root in the declared shell source, satisfying the same projection equality and clean-tree checks. The other reds preserve the intended UI/anchor assertions while restoring recorded prior production behavior. No setup failure, regression relabeling, exemption or weakened assertion supplies TDD continuity. Older contracts' reds are historical only.

Final source hashes are `024058a56d299d3ada986c8a2641d6d27873891d8f7f670e51fb3a4ae1f9e407` (UI test), `6a0793fc327dce7fc63d4cdf193dae442f5a78101c07a0e37e0537b2ad4ca5c9` (entrypoints), `014546f38e0701e0b5ffae0ad0e52e48b9c5f0c2c3f952ddf935c1b6c972098e` (sync shell), and `c35e3edac27710043a103c8e849fd2525439204bcc4a7002816d61a2b66a83a9` (first-run shell).

No tests were run by this reviewer. Only the two permitted runtime review artifacts were written; source, state, TaskResult, contracts and pins were untouched. Approval binds the exact candidate and TaskResult above. Coordinator recording, executed integration, outer Verify and human Accept remain required.
