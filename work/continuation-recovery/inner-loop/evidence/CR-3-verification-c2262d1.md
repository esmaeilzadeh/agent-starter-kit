# CR-3 verification checkpoint

Verified source candidate: `c2262d11216f3142a75a994cd88a14801c9a86a6`.

All **38/38 canonical checks** and **8/8 mapped CR-3 cases** passed.
`./ask verify` exited 1 because the exact-candidate independent semantic review
is absent. This is incomplete verification, not workstream acceptance.

Corrections committed during verification:

- `222477f`: isolate the standalone test fixture runtime from the enclosing verifier.
- `94458d8`: commit the cross-task regression before its implementation fix.
- `c2262d1`: finalize only selected-task runs, load the verification package before imports,
  and preserve pre-initialization standalone task-run compatibility.

The cross-task assertion Red is run `f21a95f6b4c4499aacf37a3ffd27a77d`
at `94458d8376a75f052adbf2c4737f4f3c18cef4b6`.
Final Green is run `4e002835e740484c88160aeb14c4cc4e` at the verified source candidate.
Both runs collected successfully; preserve their original immutable evidence.

Coverage remains incomplete for the accepted CR-T13/14 rollback and clone/CLI
scenarios, CR-T20 process-death/rejection scenarios, and CR-T21 real old-verifier
execution and compatibility diagnostics. Details and reproduction are in
`CR-3-verification-c2262d1.json` and the historical `222477f` notes beside it.
Existing inherited implementation must be considered when classifying evidence;
do not create artificial Red by removing working behavior.

CR-3 remains running. No TaskResult, approval, integration, CR-4 admission,
or product adoption is claimed. The user requested a stop after verification
and the evidence commit. The evidence-only commit changes no tested source;
its HEAD must not be substituted for the verified source SHA in exact-candidate gates.
