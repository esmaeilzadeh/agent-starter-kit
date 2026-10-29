# Task 9 scope amendment: transition-wide impact decisions

Status: **INDEPENDENTLY REVIEWED; HUMAN DECISION PENDING**. The exact proposal
at `79281ac02d8da6fb9837e64902ff860655925cc6` was approved by reviewer
`/root/review_task9_amendment` at 98% confidence. Review evidence is in
`task9-impact-scope-review.md`. It does not authorize production implementation
by itself.

## Evidence

ADR 0001 records that one assessment covers the P1 → P2 transition using the
relevant inputs of both versions, and that unresolved required evidence keeps
the assessment unresolved. The accepted normative behavior is also stated in
`specs/proposals/shorter-hashes.md#normative-propagation-stop-decision`.

The mapped Task 9 Green on candidate
`9e381599cc11fabe26b8a0a3a8d92d076dcfd9d2` failed case 9/3 at
`work/shorter-hashes/traceability/runs/cf5d501d1a904f4a9c53a238f272de64/results.json`.
The public impact result rejects the reviewed parent transition decision as
`comparison_incomplete` because it compares its full transition input vector
against only the old dependent revision's inputs. The replacement dependent is
registered in the same captured graph, and the decision already names its
complete reviewed input vector. This blocks a valid transition decision under
the recorded ADR behavior.

## Proposed change

Add `.agents/ask/workflow_refs/impact.py` to Task 9's owned paths and amend its
outcome to include the correction exercised by existing case 9/3. For a
`revise` decision, derive required paths from the actual declared dependencies
of both registered dependent revisions, including added, removed, retained,
and shared inputs. Validate the complete transition assessment once against
those paths and the existing context, authority, profile, registration, and
exact-reference requirements. Apply that one assessment to both named
endpoints, including when traversal encounters the replacement, without
requiring duplicate approval. Missing or unresolved required evidence remains
blocking. Consumer retention remains separately assessed; the transition
decision grants no general retention permission or historical execution reuse.

The path is already included in case 9/3's `source_paths`; no test case,
assertion, source binding, spec, intent, authority rule, or acceptance criterion
changes. Task 4 retains its existing ownership. The shared file is serialized:
Task 9 depends on Task 8, which transitively depends on Task 4, so the Task 9
correction follows Task 4 integration.

## Evidence and limits

Task 9 has an explicit user-authorized process waiver against manufacturing a
behavioral Red. Preserve the observed 9/3 Green failure as evidence; do not
fabricate or relabel a Red. After this amendment is independently reviewed,
approved, and registered, implement the correction, commit it, and run one
mapped Task 9 Green on the exact candidate. Then obtain exact-candidate
independent implementation review and continue the existing Task 9 integration
gates.

The test-only projection/import corrections for 9/2 and 9/4 are committed at
`6aa126d`. This amendment does not claim those cases passed on that commit.

## Runtime preservation required after approval

At state revision 85, Task 9 is running as attempt `9:attempt-1` from base
`a955fb036694f034cfb6b7969a09639cb5645b5f`. The live
`work/shorter-hashes/inner-loop/results/9.json` has SHA-256
`cdc2e19534c2db831219cee78d728b0b76b8a54bbce3b2c2da897c0dec816f41`; native
interruption refuses while that TaskResult file exists. After approval, first
preserve its exact bytes and references through an attributable, reviewed
runtime archival/reconciliation and checkpoint the consistent state. Then
interrupt through the supported operation, register the independently reviewed
amended contract, advance/reconcile the coordinator base through supported
state operations, and reopen Task 9 with attempt 1 and its actual outcomes
retained. The failed final Green remains a behavior assertion failure; carry the
existing Red waiver forward without relabeling it. Do not interrupt, register,
or reopen while preservation/reconciliation is incomplete.
