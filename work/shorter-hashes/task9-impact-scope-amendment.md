# Task 9 scope amendment: transition-wide impact decisions

Status: **PROPOSED**. This proposal is for independent exact-revision review
and human approval. It does not authorize production implementation by itself.

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
`revise` decision, impact assessment must validate required input paths across
the registered old and replacement dependent revisions. Any missing or
unresolved path remains blocking. Retain the existing authority, generation,
profile, exact-reference, candidate registration, and incomplete-input checks.

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
