# Independent review: Task 9 impact scope amendment

Decision: **APPROVED** for human decision. Planning amendment only; no
implementation authorization or runtime recovery approval.

- Reviewer: `/root/review_task9_amendment`, Codex independent reviewer.
- Confidence: 98%.
- Exact reviewed commit: `79281ac02d8da6fb9837e64902ff860655925cc6`.
- Exact amendment SHA-256: `c9f19672b5f0b4eb84651c95f2a4421346644733f8fef137c6b4328864641768`.
- Plan SHA-256: `04f2f8f7e014cdfcd16e82715c935a3bccd3f7f1e6d133a08209c82657ea5bc6`.
- TaskGraph SHA-256: `accce58832a35dd216f8b5e8f44f5feb898656b952e0a17c7dacb865e985a86c`.
- Canonical specification digest: `9bd9107a4d9490528178e2ac204c44926aa9b0e8675fd58f042e2a6fa2a77a3e`.
- Canonical plan digest: `6124e76195b53bf22299a12d8dd06d78ebb3f3d09702a8c596beb3eba11d8a3d`.
- Proposed TaskGraph digest: `f3e69d797e74d663dd2a4523d1dee4524af6bef319dc7f917120fab111df6072`.
- The currently registered authority still carries graph digest
  `3c8e40f7501dffc72feec3a476e9dcbfabfdce11726d93fdde08487792ad942f`; renewed
  registration is pending human approval and implementation of the amendment.
- The specification, test plan, and their content digests remain unchanged.

The reviewer confirmed the proposal derives required paths from both registered
dependent revisions, validates one transition assessment, and applies it to
both named endpoints. Missing or unresolved evidence remains blocking.
Consumer retention and historical execution reuse remain separate decisions.
Task 4 and Task 9 may share `impact.py` because the task dependency chain
serializes their writes. No spec, intent, confirmation, case, source binding,
authority rule, or acceptance criterion changes.

Before runtime interruption/reopening after human approval, preserve the exact
TaskResult and all linked execution evidence through reviewed archival or
reconciliation, checkpoint the consistent state, then use supported interrupt,
renewed plan registration, coordinator-base reconciliation, and Task 9 reopen.
The existing failure remains a final-Green behavior assertion; the Red waiver
does not turn it into passing or review evidence.
