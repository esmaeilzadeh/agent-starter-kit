# RWB-108 retained ledger recovery

The missing ledger was recoverable from Git history. Commit
`24473ca42826ac397b9b1c60ec54dabbc8fa2599` stopped tracking the runtime ledger;
its parent `d21dfcc2cca1ebbacee5c7de4025b0d85e4e518a` retains the original bytes at
`work/structured-agentic-environment/traceability/executions.json`.

The original file was restored to that ignored runtime path under its existing
`executions.lock`. No entries were generated or edited. Its SHA-256 is
`b5ce6be822ee7903442b9695ae8585bac2e324046c6ae1b933c21f38cc5451a2`.

The selected WB-003 run `799924ec199b4717a3eabf4fb39a1bdc` binds candidate
`70dd295aacff869857081a94870d02fcbf4d640c`. Its retained report's canonical
digest matches ledger digest
`989d3a54624870f55d284e5396161683380b8661dcd08146df503450a5ebaf67`.
The selected case passed, and its retained log matches SHA-256
`020e0797771061f5c2c8244fc7853c7b3e41e93d5d44b81f3b193d68815b9ff9`.

The snapshot contains 142 original entries. All 141 reports present locally
match their ledger digests; one unrelated report is absent. The selected WB-003
report and log are present. The existing authority checks additionally validate
its source, accepted historical contract, coordinator review, and integration
receipt. A later failed workstream completion does not invalidate this
separately recorded historical task result.

After recovery, `python3 -m unittest _ask.tests.test_revising_pilot -v` passed
all 12 tests, including the previously failing genuine-result and representative
context cases. This removes the recorded historical-evidence blocker; it does
not approve task integration or human comprehension.

For another checkout, recover the file from the exact source commit above,
verify its SHA-256 before publishing it under `executions.lock`, and rerun the
pilot tests. Preserve an existing runtime ledger rather than overwriting it.
