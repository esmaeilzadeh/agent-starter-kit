# Independent implementation plan review

Decision: **APPROVED** for planning acceptance at the exact contract below. No unresolved findings remain. This original review recorded the plan-ready endpoint; its implementation stop was later superseded by the explicit human `implement` direction and the amendment review below.

Reviewer: `gpt-6-astra/security-plan-review`, runtime `codex`, independent child context. Existing submitted Astra selection applies. Parent model: GPT-6; exact variant unavailable. The previous REJECTED review is retained in Git at `b7848e2`.

## Exact reviewed contract

- `contract_sha`: `64ec68e5409b461d0a5b3c3e88644c63e29044f8`
- `spec_digest`: `664778e240718fadd15f40f9bd23a10d2664b8d3d7d1fc3942426dfc4ad5e8cc`
- `plan_digest`: `c754f5576b91b34adfbe488475a89dff2809bc5ba0a754286704d5b365a22ebf`
- `graph_digest`: `6d99009738a029cb42c546d93726b7864445ab5feecc5ed2f5a98305fbaa4668`
- `plan_markdown_sha256`: `4b6db0e6bf8d467ae9fdb6746c97605afaed5b1952dcdd52ff491c327d4c0222`
- `frozen_contract_sha`: `88035127763fb1436775c13c941fbcba7484d581`

## Resolved findings

- **PR-01 resolved:** CSH-01 now owns _ask/scripts/install-kit.sh; CSH-T04 explicitly exercises public prepare, install, bootstrap and upgrade failure propagation. Shared ownership with CSH-03 is ordered.
- **PR-02 resolved:** CSH-T07 is limited to existing --complete candidate lookup with no project dispatcher marker. New CSH-T08 owns launcher help, snippet generation and startup default behavior, requiring real behavior Red.
- **PR-03 resolved:** CSH-01 owns initial journey/fixture authorship before production writes. Coordinator captures CSH-T38/T39 assertion Red as scope=task, task_id=CSH-10 under the same accepted contract; initial source stays an ancestor and final review verifies assertion continuity. CSH-10 remains sole execution/completion owner with no early state transition.

## Coverage and scope assessment

All twelve approved criteria have executable cases and the required test types. Forty cases have one execution/completion task each across ten sequential tasks; source ownership covers each case and shared paths are serialized. Frozen structural contract validation passes. Independent inspection of the engineering model found all forty Scenario.case records bound to the updated plan digest and case IDs, with valid local Test.reference paths and IDs.

The plan supplies concrete trust identities, a complete write inventory, durable recovery, private credential migration, shared verifier environment construction, validated scalar generation, explicit loopback precedence and model decision/handoff behavior. It preserves trusted-local limitations, existing client files, independent review and the approved scope. Exact external dependency pins are reviewed task outputs before package execution; absent provenance or incompatibility blocks execution. This does not authorize floating versions.

Model obligations distinguish the actual orchestrator from a child, verify automatic switch results, record the permitted manual acknowledgment fallback honestly, preserve old workstream choices without invented consent, and check the plan-only endpoint before discovery or switching. Runtime probes are future implementation evidence; contract tests using fake adapters do not claim live vendor support.

T07 and T11 preserve existing behavior and require baseline Green evidence rather than fabricated failure. T08 and the new feature journeys retain real Red requirements. Early coordinator evidence for the two final journeys is compatible with the frozen reader's same-contract task-scoped Red records and source-ancestry checks. Final independent review must inspect the actual assertion continuity.

The JSON decision contains individual criterion assessments and test adequacy details. No hidden scope change or new approval question is needed.

## Limits and endpoint

No behavior tests, exploit reproduction, dependency audit, paid model calls or runtime switching checks ran. Tests remain planned; this review does not establish product correctness or available runtime capabilities. Approval binds only the contract digests above.

At the time of this review, the coordinator could record planning acceptance and report Plan ready, then stop. A later explicit implementation instruction was required before production changes, journey baseline execution, task dispatch or orchestrator handoff.

## Implementation authorization amendment review — 2026-11-19

Decision: **APPROVED** by independent reviewer `gpt-6-astra/security-plan-review`.

- Exact candidate: `eebe137bb70629716f5333b7e90d501a25d69586`
- Exact `plan.md` SHA-256: `5f57ea42d3b2fb1c9fde2860339cbfd25d5230b226879d66ed19b04d5f6c1ae1`
- Spec digest: `664778e240718fadd15f40f9bd23a10d2664b8d3d7d1fc3942426dfc4ad5e8cc`
- Test-plan digest: `c754f5576b91b34adfbe488475a89dff2809bc5ba0a754286704d5b365a22ebf`
- TaskGraph digest: `6d99009738a029cb42c546d93726b7864445ab5feecc5ed2f5a98305fbaa4668`

The amendment records the user's explicit implementation authorization and
starts execution at CSH-01. It does not change the accepted intent, specification,
test cases, TaskGraph, or task order. The reviewed CSH-T38/T39 Red baseline does
not advance CSH-10; that task remains pending. Human acceptance remains the final
workstream gate. This amendment supersedes only the earlier plan-only endpoint;
the original planning review and its findings remain historical evidence.

## CSH-01 ownership amendment review — 2026-11-19

Decision: **APPROVED** by independent reviewer `gpt-6.1-sol (medium)`.

- Exact candidate: `ab109ead101e409f8f30b5339cd3ecf2157bf4c6`
- Exact reviewed change: add `_ask/tests/test-prepare-skills-refuses-latest.sh`
  and `_ask/tests/test_tdd_preparation_overlay.py` to CSH-01 `owned_paths`.
- The added paths exercise skill preparation, which CSH-01 owns. The approved
  specification, test cases, plan text, task order, and dependencies are unchanged.
- No additional contract obligations were introduced.
- This review approves only the ownership amendment, not implementation
  correctness or completion of CSH-01.
