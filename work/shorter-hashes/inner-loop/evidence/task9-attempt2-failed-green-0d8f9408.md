# Task 9 attempt 2 failed final Green

Run: `0d8f94087f1d43b28f8dd2285d43db2e`  
Candidate/source: `905c1aca97c2532db048e79df08fbdb4e3f0fc06`  
Execution: `87723c073ec847cea89b082cdc56b2ce`  
Collection: `ok`; exit: `1`.

The report, execution JSON, and log are preserved byte-for-byte in
`preserved-task9-attempt2-failed-green-0d8f9408/`; SHA-256 values are
`186aea90ed88af777a37ab2367a1435b0503544b66b18d8417d490be54cfd2fa`,
`2deb42c5e71fbed858040098d270bcd209c5b7489385dd6b52d0b3f4ef870fbb`, and
`384b0ee4250fde2a37fde07cce0c6c24afdd7a8e4c1dc31faa0166002356879c`.
The execution ledger entry is retained in `traceability/executions.json`.

Cases 9/1, 9/2, 9/4, and 9/5 passed. Case 9/3 passed the transition-impact
assertions, then failed the later stale-final-candidate assertion: the fixture's
successful `verify` left an untracked `verification-result.json`, so completion
correctly returned `dirty or non-current candidate source` before reaching the
stale-run check. A focused fixture reproduction confirmed this was the sole
dirty source path. The fixture now removes that generated artifact after
asserting `verify` succeeded; no test assertion or product acceptance behavior
changed.

The coordinator refused to checkpoint this failed final Green because its
behavior assertion is not bound to a failing Red execution. Preserve it as a
failed Green, not Red or passing completion evidence. A corrected candidate
and one exact-candidate mapped Green remain required.
