# Independent baseline regression amendment review

Decision: **APPROVED**. Challenge verdict: **PASS**. No blocking findings remain for exact candidate `55c11fad3e0391f8a47236166c8d5941d824ef73`, compared with accepted contract `722fe3002253e473de0689823c3fe35052d458a1`.

Reviewer: `review_checkplan_amendment`, independent child context; model: `gpt-6-astra` (configured Spec Challenge role); runtime: `codex`; parent model: not exposed. This review covers the accepted-plan whitelist, bounded verification implementation, regressions, graph ownership and preserved task evidence. It permits coordinator pinning of this exact contract and implementation. It does not integrate WB-001, approve a later candidate, grant individual baseline exemptions or authorize workstream completion.

## Exact reviewed authority

| Contract | Canonical digest |
| --- | --- |
| Specification | `f2707008c69698e6f659bc071f42b2dd0bbfac8b381d8a5ca5efa5d4d6adcaeb` |
| Test plan | `4845c9f46fb7ecfe4f368e006c1a8d89b2f7c3ea5beefe1478b08ea184eb09e8` |
| Parsed TaskGraph | `eea31a815b6b3857f1cbbe2bddd7b820cd0e4c62c89a73d822c96af502aac606` |

Machine decision and reviewed source hashes: `traceability/baseline-regression-plan.json` under this workstream.

## Whitelist and scope

The new accepted-plan field contains exactly 22 unique IDs under WB-001: MV-valid, MV-graph, MV-fields, MV-refs, ME-decision, ME-revise, ME-reject, ME-race, EV-real, EV-missing, MP-shared, MC-journey, DG-pre, DG-post, DG-refs, DG-events, DG-parity, DG-publish, DG-bootstrap, ME-batch, DG-success and DG-entrypoints. The three new workbench cases are excluded. Every listed test remains classified `new`; every referenced source exists and is byte-identical between the prior accepted pin and this candidate.

Removing only this new whitelist field yields the prior test-plan JSON exactly. Product criteria, test IDs, assertions, runners, assignments and classifications are unchanged. All nine graph tasks match their test scopes, all 57 cases retain a unique task owner, dependencies precede dependents, and owned paths do not overlap. WB-001 explicitly owns the modified verification modules, contract tests, evidence tests and plan support path. Ownership does not bypass `load_accepted` protection against unreviewed changes to accepted obligations.

The plan and proposal distinguish task integration from final workstream completion. They preserve the 22-case history gap, require a new independent pin and fresh coordinator/base, retain prior execution evidence, and require a partial final result while genuine required red evidence remains absent. UI checkpoint obligations are unchanged.

## Enforcement and counterexamples

Contract validation requires each exemption group to name an accepted task and a nonempty unique list of that task's assigned `new` test IDs. Unknown tasks, unknown/unassigned tests and other classifications reject.

Semantic review requires an approved decision, a nonempty rationale and `reviewer_ack=true`. A baseline exemption additionally requires task scope, whitelist membership and classification `new`. For every referenced source, `read_at` must succeed at the accepted contract and candidate revisions, and their bytes must match. Missing baseline source and any differing source reject. Full-workstream review rejects this exemption regardless of source equality. The existing nested scope binding prevents relabeling the task review to acquire wider authority.

Independent disposable-fixture checks confirmed rejection for missing acknowledgment, empty rationale, rejected decision, absent whitelist membership, `changed` or `regression` classification, and a secondary source present in the candidate but absent from the accepted baseline. Existing focused regressions additionally reject changed test source and workstream use.

An end-to-end disposable check committed and independently pinned an explicit task exemption, recorded its scoped semantic review, executed genuine task green and supplied no red. Completion passed with the explicit evidence value `exempt:baseline-regression`. A complete full-workstream review and genuine full green without red still failed with missing-red entries. Thus the exemption can unblock the bounded task without manufacturing historical red or satisfying final completion. The existing evaluator also rejects combining an exemption with recognized red history for the same case.

## Preserved WB-001 evidence

The archived TaskResult remains bound to candidate/base `92c43e541ee244add20e02eb65082348add716ad`. Its SHA-256 matches the independently authored review's recorded TaskResult digest. Archived run `c07ccc0c8926414d9ad70f729597bf4d` records exactly 25 passing WB-001 cases at that candidate; its case identities match the semantic review, and every reported source digest matches the historical Git object. Its retained log digest is `8b1ab6a7af35a57b3e20a393e86c6c8a763c3dadba2002cd967806d387e50b28`, matching the archived log bytes.

Those records establish historical green execution and prior review. They do not establish red for the 22 foundation cases or execution of this amendment candidate. The TaskResult's synthetic shell red/green remains separate from instrumented Python case evidence. Individual exemptions require a new candidate-bound independent task review after pinning.

## Verification and transition

- `python3 -m unittest discover -s _ask/tests -p 'test_traceability*.py'`: **25 tests passed**, 32.985 seconds.
- `./ask traceability validate-plan structured-agentic-environment --revision 55c11fad3e0391f8a47236166c8d5941d824ef73`: passed.
- `./ask inner-loop validate structured-agentic-environment`: `ok`.
- Exact-source contract comparisons, whitelist/source checks, graph consistency checks and disposable completion counterexamples passed.

The whitelist changes the test-plan digest, so the existing report selector will not reuse old-plan red reports. After pinning, execute the genuine historical WB assertion-red source revisions through the current accepted runner to obtain fresh reports under the new contract, then perform candidate-bound green and review. The CLI supports historical source execution for phase `red`. Preserve previous reports without rewriting their identities. This requirement does not authorize intentional weakening of tests or fabricated failures.

No full repository Verify, current WB-001 integration or final workstream completion is claimed. The reviewer changed only review artifacts and did not pin the candidate. The final 22-case TDD gap remains unresolved.
