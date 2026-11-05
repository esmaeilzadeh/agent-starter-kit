# Task 9 mapped Green attempt 2 — failed

- Candidate/source: `e821ceaf478542dfdec4e484df88394dac4347a0`
- Run: `1f7075be8bb242a88e2883b13657cbbd`
- Execution: `8d56343240a546bab40c53d3d05734d1`
- Collection: `ok`; exit status: `1`
- Outcomes: 9/1, 9/2, 9/4, 9/5 passed; 9/3 failed with `behavior_assertion`.
- Failure: the stale-candidate assertion received `migration_required: missing/invalid JSON .../traceability/static-<new-candidate>.json`. The fixture ran `verify` before committing its changed candidate, so the receipt was keyed to the earlier commit.
- Report SHA-256: `f871bd4f1d54769686b3d9515eac09eb280b5747dd39e728dd5088c8a1987e6b`
- Execution JSON SHA-256: `2deb42c5e71fbed858040098d270bcd209c5b7489385dd6b52d0b3f4ef870fbb`
- Execution log SHA-256: `2df2402cdca69beb66a5f056f5f5e199846d81024f3ae48cf86e8698125abb9f`
- The traceability ledger records this actual outcome in `work/shorter-hashes/traceability/executions.json`; no TaskResult was checkpointed because the supported checkpoint command refused to classify a Green failure as a Red.
